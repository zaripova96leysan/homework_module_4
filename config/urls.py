from django.contrib import admin
from django.urls import path, include
from users.views import PaymentListView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('lms.urls')),
    path('api/payments/', PaymentListView.as_view(), name='payment-list'),
]