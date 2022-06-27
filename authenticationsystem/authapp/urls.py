from django.urls import path
from .views import Login, Registration, PasswordReset, Verification, CreateUser, Logout, Dashboard

urlpatterns = [
    path('', Login.as_view(), name="Login"),
    path('register', Registration.as_view(), name="Registration"),
    path('change', PasswordReset.as_view(), name="Change Password"),
    path('verify/<str:email>/', Verification.as_view(), name="Verification"),
    path('verify', Verification.as_view(), name="Token Verification"),
    path('create', CreateUser.as_view(), name="Create User"),
    path('dashboard', Dashboard.as_view(), name="Dashboard"),
    path('logout', Logout.as_view(), name="Logout"),
]
