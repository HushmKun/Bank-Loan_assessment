from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    ApplicationsView,
    SingleApplicationView,
    PaymentsView,
    SinglePayment,
)

urlpatterns = [
    path(
        "login/", TokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("applications/", ApplicationsView.as_view(), name="list_create_applications"),
    path("applications/<int:id>/", SingleApplicationView.as_view(), name="read_update_application"),
    path("payments/", PaymentsView.as_view(), name='list_payments'),
    path("payments/<int:id>/", SinglePayment.as_view(),  name='update_payment'),
]
