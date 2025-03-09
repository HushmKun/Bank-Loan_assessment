from typing import override
from rest_framework.exceptions import PermissionDenied 
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView, Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Application, Payment
from .serializer import ApplicationSerializer, PaymentSerializer

# Create your views here.


class ApplicationsView(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = self.request.user

        if user.is_superuser:
            data = Application.objects.all()
        else:
            data = Application.objects.filter(user=user)

        serializer = ApplicationSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        user = self.request.user
        serializer = ApplicationSerializer(
            data={
                "user": (
                    user.id
                    if not user.is_superuser
                    else self.request.POST.get("user")
                ),
                "amount": self.request.POST.get("amount"),
                "duration_months": self.request.POST.get(
                    "duration_months"
                ),
                "application_type": (
                    "deposit"
                    if user.groups.filter(name="Provider").exists()
                    else "loan"
                ),
            }
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SingleApplicationView(APIView):

    def get(self, request, id):
        user=request.user
        data = generics.get_object_or_404(
            Application, 
            id=id, 
        )
        serializer = ApplicationSerializer(data)
        
        if not (user.is_superuser or user == data.user):
            raise PermissionDenied()

        return Response(serializer.data, status=status.HTTP_200_OK)

class PaymentsView(generics.ListAPIView):
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['payment_type', 'status']
    serializer_class = PaymentSerializer
    
    @override
    def get_queryset(self):
        user = self.request.user 
        data = Payment.objects.all()
        
        if user.is_superuser:
            return data

        return data.filter(transaction__user=user)
        
class SinglePayment(APIView):

    def patch(self, request, id) -> Response:
        user = request.user
        payment = Payment.objects.get(pk=id)

        if not (user.is_superuser or payment.transaction.user == user) :
            raise PermissionDenied()
        
        patch_status = request.data.get("status", None)
        if not patch_status in ('paid', 'failed'):
            return Response(
                data= {"error": "'status' isn't valid"},
                status=status.HTTP_400_BAD_REQUEST
            )
            

        serializer = PaymentSerializer(
            payment, data={'status':patch_status}, partial=True, 
        )
        if not serializer.is_valid():
            return Response(
                data= serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
            
        serializer.save()
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )
