from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path("", views.AccountsRedirect, name="redirect"),
    path("agreement/", views.AgreementView, name="agreement"),
    path("profile/", views.ProfileView, name="profile"),
    path("profile/orders/", views.ProfileOrdersView, name="profile-orders"),
    path("profile/orders/<int:pk>", views.ProfileOrderDetailsView, name="profile-order-details"),
    path("signup/", views.SignUpView, name="signup"),
    path("activate/<slug:uidb64>/<slug:token>", views.activate, name='activate'),
    path("change-email/<slug:uidb64>/<slug:token>", views.change_email, name='change-email'),
    path("login/", views.LoginView, name="login"),
    path("logout/", views.LogoutView, name="logout"),
    path("password-reset/", views.PasswordReset, name="reset"),
    path("password-reset/<slug:uidb64>/<slug:token>", views.PasswordResetConfirm, name='reset-confirm'),
    path("password-change/", views.PasswordChangeView, name="password-change"),
    path("subscribe/", views.Subscribe, name="subscribe"),
    path("subscribe/<slug:uidb64>/<slug:token>", views.subscribe_verification, name='subscribe-verification'),
    path("cart/", views.CartView, name="cart"),
    path("cart/controller/", views.cart_controller, name="cart-controller"),
    path("cart/checkout/", views.CheckoutView, name="checkout"),
]