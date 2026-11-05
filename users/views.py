from rest_framework import generics, filters
from .models import Payment
from .serializers import PaymentSerializer
from django_filters.rest_framework import DjangoFilterBackend


class PaymentListView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]

    ordering_fields = ['payment_date']

    filterset_fields = ['course', 'lesson', 'payment_method']

