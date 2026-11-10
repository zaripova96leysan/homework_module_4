from django.contrib import admin
from django.urls import path, include
from users.views import UserListCreateView, UserRetrieveUpdateDestroyView, MyTokenObtainPairView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('lms.urls')),
    path('api/users/', UserListCreateView.as_view()),
    path('api/users/<int:pk>/', UserRetrieveUpdateDestroyView.as_view()),
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
]