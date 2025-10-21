from django.urls import path
from .views.auth import (
    UserLoginView, UserRegistrationView, OwnerRegistrationView,
    LogoutView, ChangePasswordView, CurrentUserProfileView
)
from .views.google_auth import GoogleLoginAPIView
from .views.profile import UpdateUserInfoView
from .views.owner import OwnerProfileDetailView

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='token_obtain_pair'),
    path('register-student/', UserRegistrationView.as_view(), name='user-register'),
    path('register-owner/', OwnerRegistrationView.as_view(), name='owner-register'),
    path('update-profile/', UpdateUserInfoView.as_view(), name='update-profile'),
    path('logout/', LogoutView.as_view(), name='token_logout'), 
    path('google-login/', GoogleLoginAPIView.as_view(), name='google-login'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('me/', CurrentUserProfileView.as_view(), name='current-user-profile'),
    path('owners/<int:id>/', OwnerProfileDetailView.as_view(), name='owner-detail'),

]