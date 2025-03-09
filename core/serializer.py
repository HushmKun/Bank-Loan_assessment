from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Application, CashFlow, Payment, Transactions

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name"]


class ApplicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Application
        fields = [
            "user",
            "duration_months",
            "amount",
            "interest_rate",
            "status",
            "created_at",
            "application_type",
        ]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id','payment_type', 'amount', 'due_date', 'status']  
        # optional: exclude fields that shouldn't be serialized
        # exclude = ['id'] # example