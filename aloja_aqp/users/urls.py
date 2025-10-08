from django.urls import path
from .views import UserRegistrationView
from .views import UserLoginView

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='token_obtain_pair'),
    path('register/', UserRegistrationView.as_view(), name='user-register'),
]