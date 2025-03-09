from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Application, Payment, User, Transactions

class BaseTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        
        Group.objects.create(name='Borrower')
        Group.objects.create(name='Provider')
        Group.objects.create(name='Bank Personnel')

        
        cls.superuser = User.objects.create_superuser(
            username='admin', password='testpass'
        )
        cls.borrower = User.objects.create_user(
            username='borrower', password='testpass'
        )
        cls.borrower.groups.add(Group.objects.get(name='Borrower'))
        cls.provider = User.objects.create_user(
            username='provider', password='testpass'
        )
        cls.provider.groups.add(Group.objects.get(name='Provider'))
        cls.superuser.groups.add(Group.objects.get(name='Bank Personnel'))


class ApplicationsViewTests(BaseTestCase):
    def test_unauthenticated_access(self):
        response = self.client.get(reverse('list_create_applications'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_applications_regular_user(self):
        
        Application.objects.create(
            user=self.borrower, amount=1000, duration_months=12, application_type='loan'
        )
        Application.objects.create(
            user=self.provider, amount=500, duration_months=6, application_type='deposit'
        )
        self.client.force_authenticate(user=self.borrower)
        response = self.client.get(reverse('list_create_applications'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['user'], self.borrower.id)

    def test_get_applications_superuser(self):
        Application.objects.create(user=self.borrower, amount=1000, duration_months=12, application_type='loan')
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(reverse('list_create_applications'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_post_loan_application_borrower(self):
        self.client.force_authenticate(user=self.borrower)
        data = {'amount': 5000, 'duration_months': 24}
        response = self.client.post(reverse('list_create_applications'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['application_type'], 'loan')
        self.assertEqual(response.data['user'], self.borrower.id)

    def test_post_deposit_application_provider(self):
        self.client.force_authenticate(user=self.provider)
        data = {'amount': 3000, 'duration_months': 12}
        response = self.client.post(reverse('list_create_applications'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['application_type'], 'deposit')

    def test_superuser_post_for_another_user(self):
        self.client.force_authenticate(user=self.superuser)
        data = {'amount': 2000, 'duration_months': 6, 'user':self.provider.id}
        url = f"{reverse('list_create_applications')}"
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user'], self.provider.id)

    def test_post_missing_required_fields(self):
        self.client.force_authenticate(user=self.borrower)
        data = {'duration_months': 12}
        response = self.client.post(reverse('list_create_applications'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('amount', response.data)


class SingleApplicationViewTests(BaseTestCase):
    def setUp(self):
        self.application = Application.objects.create(
            user=self.borrower, amount=1000, duration_months=12, application_type='loan'
        )

    def test_retrieve_application_owner(self):
        self.client.force_authenticate(user=self.borrower)
        response = self.client.get(reverse('read_update_application', args=[self.application.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.application.user.id)

    def test_retrieve_application_superuser(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(reverse('read_update_application', args=[self.application.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_application_unauthorized(self):
        self.client.force_authenticate(user=self.provider)
        response = self.client.get(reverse('read_update_application', args=[self.application.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PaymentsViewTests(BaseTestCase):
    def setUp(self):
        super().setUp()

        
        self.loan_application = Application.objects.create(
            user=self.borrower,
            amount=1000,
            duration_months=1,
            interest_rate=15,
            application_type='loan',
            status='pending'
        )
        self.loan_application.status = 'approved'
        self.loan_application.save()  

        
        self.deposit_application = Application.objects.create(
            user=self.provider,
            amount=500,
            duration_months=1,
            interest_rate=15,
            application_type='deposit',
            status='pending'
        )
        self.deposit_application.status = 'approved'
        self.deposit_application.save()  

    def test_get_payments_regular_user(self):
        self.client.force_authenticate(user=self.borrower)
        response = self.client.get(reverse('list_payments'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['payment_type'], 'loan')

    def test_get_payments_superuser(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(reverse('list_payments'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  

    def test_filter_payments(self):
        self.client.force_authenticate(user=self.superuser)
        
        response = self.client.get(f"{reverse('list_payments')}?payment_type=loan")
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['payment_type'], 'loan')
        
        
        response = self.client.get(f"{reverse('list_payments')}?payment_type=deposit")
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['payment_type'], 'deposit')

class SinglePaymentTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        
        self.deposit_app = Application.objects.create(
            user=self.provider,
            amount=2000,
            duration_months=1,
            interest_rate=10,
            application_type='deposit',
            status='pending'  
        )

        self.deposit_app.status = 'approved'
        self.deposit_app.save()
        
        
        self.loan_application = Application.objects.create(
            user=self.borrower,
            amount=1000,
            duration_months=1,
            application_type='loan',
            interest_rate=15,
            status='pending'  
        )
        self.loan_application.status = 'approved'
        self.loan_application.save()
        
        
        self.payment = Payment.objects.get(
            transaction__application=self.loan_application
        )

    def test_update_payment_status_owner(self):
        self.client.force_authenticate(user=self.borrower)
        data = {'status': 'paid'}
        response = self.client.patch(
            reverse('update_payment', args=[self.payment.id]), 
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'paid')

    def test_update_payment_status_superuser(self):
        self.client.force_authenticate(user=self.superuser)
        data = {'status': 'failed'}
        response = self.client.patch(
            reverse('update_payment', args=[self.payment.id]), 
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'failed')

    def test_update_payment_unauthorized_user(self):
        self.client.force_authenticate(user=self.provider)
        data = {'status': 'paid'}
        response = self.client.patch(
            reverse('update_payment', args=[self.payment.id]), 
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_status_value(self):
        self.client.force_authenticate(user=self.borrower)
        data = {'status': 'invalid'}
        response = self.client.patch(
            reverse('update_payment', args=[self.payment.id]), 
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_missing_status_field(self):
        self.client.force_authenticate(user=self.borrower)
        data = {}
        response = self.client.patch(
            reverse('update_payment', args=[self.payment.id]), 
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)