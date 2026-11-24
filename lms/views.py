from rest_framework import viewsets, generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import stripe

from .models import Course, Lesson, Subscription, Payment
from .serializers import CourseSerializer, LessonSerializer
from .permissions import IsModerator, IsOwner
from .paginators import CustomPagination
from .services import create_stripe_product, create_stripe_price, create_stripe_checkout_session



class NotModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        return not IsModerator().has_permission(request, view)

class ModeratorOrOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return IsModerator().has_permission(request, view) or IsOwner().has_permission(request, view)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [permissions.IsAuthenticated(), NotModerator()]
        if self.action in ['update', 'partial_update', 'retrieve', 'list']:
            return [permissions.IsAuthenticated(), ModeratorOrOwner()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListCreateView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, NotModerator]
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [permissions.IsAuthenticated(), NotModerator()]
        return [permissions.IsAuthenticated(), ModeratorOrOwner()]


class SubscriptionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        course_id = request.data.get('course_id')

        if not course_id:
            return Response({"error": "Не передан course_id"}, status=400)

        course_item = get_object_or_404(Course, id=course_id)
        subs_item = Subscription.objects.filter(user=user, course=course_item)

        if subs_item.exists():
            subs_item.delete()
            message = 'подписка удалена'
        else:
            Subscription.objects.create(user=user, course=course_item)
            message = 'подписка добавлена'

        return Response({"message": message})


class CreatePaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({"error": "Курс не найден"}, status=status.HTTP_404_NOT_FOUND)

        try:
            product_data = create_stripe_product(
                name=course.title,
                description=course.description
            )

            price_data = create_stripe_price(
                product_id=product_data["id"],
                amount_in_rubles=course.price
            )

            session_data = create_stripe_checkout_session(
                price_id=price_data["id"],
                success_url="http://127.0.0.1:8000/api/success/",
                cancel_url="http://127.0.0.1:8000/api/cancel/",
            )

            payment = Payment.objects.create(
                user=request.user,
                course=course,
                stripe_product_id=product_data["id"],
                stripe_price_id=price_data["id"],
                stripe_session_id=session_data["id"],
                payment_url=session_data["url"],
                amount=course.price
            )

            return Response({
                "payment_url": payment.payment_url,
                "payment_id": payment.id
            }, status=status.HTTP_201_CREATED)

        except stripe.error.StripeError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)