from django.urls import path
from .views import UserRegistrationView
from .views import UserLoginView, OwnerRegistrationView, UpdateUserAvatarView, UpdateUserInfoView

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='token_obtain_pair'),
    path('register-student/', UserRegistrationView.as_view(), name='user-register'),
    path('register-owner/', OwnerRegistrationView.as_view(), name='owner-register'),
    path('update-avatar/', UpdateUserAvatarView.as_view(), name='update-avatar'),
    path('update-profile/', UpdateUserInfoView.as_view(), name='update-profile')
]