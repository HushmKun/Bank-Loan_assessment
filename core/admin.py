from typing import override
from django.contrib import admin
from django.db.models import Q

from .models import User, Application, CashFlow, Payment, Transactions

from .forms import CustomerApplicationForm, ProviderApplicationForm, ApplicationAdminForm
# Register your models here.


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["username", "email", "is_staff"]


@admin.register(CashFlow)
class CashFlowAdmin(admin.ModelAdmin):
    list_display = ["transaction_type", "amount", "date", "transaction"]


@admin.register(Transactions)
class TransactionsAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "application",
        "application__amount",
        "start_date",
        "end_date",
        "application__interest_rate",
    ]
    show_facets = True

    
@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "application_type",
        "amount",
        "interest_rate",
        "status",
        "created_at",
    ]
    list_filter = ["application_type", "status"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs

        return qs.filter(user=request.user)

    def get_form(self, request, obj=None, **kwargs):
        user = request.user
        form = None  

        if user.groups.filter(name='Bank Personnel').exists():
            self.form = ApplicationAdminForm
            form = super().get_form(request, obj, **kwargs)
            form.base_fields['reviewed_by'].initial = user
            return form

        elif user.groups.filter(name='Borrower').exists():
            self.form = CustomerApplicationForm
        elif user.groups.filter(name='Provider').exists():
            self.form = ProviderApplicationForm

        if form is None:
            form = super().get_form(request, obj, **kwargs)

        if not kwargs.get('change'):
            form.base_fields['user'].initial = user

        self.readonly_fields = ('status', 'interest_rate')
        return form

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["payment_type", "amount", "status", "transaction"]
    list_filter = ["payment_type", "status"]
    list_display_links = []

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs

        return qs.filter(
            Q(loan__user=request.user) | Q(deposit__user=request.user)
        )
