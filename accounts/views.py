import datetime

import accounts.urls
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm
from django.contrib.auth.models import User, Group
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from mailchimp_marketing import Client
from mailchimp_marketing.api_client import ApiClientError
from catalog.views import get_previous_and_current_url, NavView
from .forms import SignupForm, SubscribeForm, UserEditForm, SignupProfileForm, ProfileEditForm, CheckoutForm
from .tokens import account_activation_token, subscription_token
from catalog.models import Cars
from collections import OrderedDict
from django.db import transaction
from .models import Order, LineItem
import copy

# Mailchimp Settings
api_key = settings.MAILCHIMP_API_KEY
server = settings.MAILCHIMP_DATA_CENTER
list_id = settings.MAILCHIMP_EMAIL_LIST_ID


# APPLICATION FUNCTIONS
# Subscription Logic
def subscribe(email):
    """
     Contains code handling the communication to the mailchimp api
     to create a contact/member in an audience/list.
    """

    mailchimp = Client()
    mailchimp.set_config({
        "api_key": api_key,
        "server": server,
    })

    member_info = {
        "email_address": email,
        "status": "subscribed",
    }

    try:
        response = mailchimp.lists.add_list_member(list_id, member_info)
        print("MAILCHIMP response: {}".format(response))
    except ApiClientError as error:
        print("MAILCHIMP An exception occurred: {}".format(error.text))
        return error.status_code


def unsubscribe(email):
    """
     Contains code handling the communication to the mailchimp api
     to create a contact/member in an audience/list.
    """

    mailchimp = Client()
    mailchimp.set_config({
        "api_key": api_key,
        "server": server,
    })

    try:
        response = mailchimp.lists.delete_list_member(list_id, email)
        print("MAILCHIMP response: {}".format(response))
    except ApiClientError as error:
        print("MAILCHIMP An exception occurred: {}".format(error.text))
        return error.status_code


def subscribe_send_email(request, user, email):
    mail_subject = 'AUTOY SHOP - Subscription email verification'
    mail_template = 'accounts/subscribe_verification_email.html'
    current_site = get_current_site(request)
    message = render_to_string(mail_template, {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(email)),
        'token': subscription_token.make_token(user),
    })
    to_email = email
    email = EmailMessage(
        mail_subject, message, to=[to_email]
    )
    email.send()


def send_email(request, user, email, email_type, order_details=None):
    if email_type == "activation":
        mail_subject = 'AUTOY SHOP - Activate your account'
        mail_template = 'accounts/activation_email.html'
    elif email_type == "reset":
        mail_subject = 'AUTOY SHOP - Reset your password'
        mail_template = 'accounts/password_reset_email.html'
    elif email_type == "change_email":
        mail_subject = 'AUTOY SHOP - Change email request'
        mail_template = 'accounts/change_email_request_email.html'
    elif email_type == "checkout":
        mail_subject = 'AUTOY SHOP - Order Receipt'
        mail_template = 'accounts/checkout_email.html'
    else:
        raise ValueError("Wrong email type")
    current_site = get_current_site(request)
    if email_type == "checkout":
        message = render_to_string(mail_template, {
            'user': user,
            'domain': current_site.domain,
            'profile': order_details["profile"],
            'cart_total_price': order_details["cart_total_price"],
            'cart': order_details["cart"],
            'order_number': order_details["order_number"],
            'bought_date': order_details["bought_date"],
        })
    else:
        message = render_to_string(mail_template, {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })
    to_email = email
    email = EmailMessage(
        mail_subject, message, to=[to_email]
    )
    email.send()


def navbar():
    nav = NavView()
    return nav.get_context_data()


def email_confirm_check(request):
    email_confirm = request.session.get('email_confirm', None)
    context = {"email_confirm": ""}
    if email_confirm:
        context["email_confirm"] = email_confirm
        del request.session['email_confirm']
        request.session.modified = True
    return context


# NO TEMPLATE VIEWS
def AccountsRedirect(request):
    return redirect("accounts:profile")


def subscribe_verification(request, uidb64, token):
    try:
        email = force_str(urlsafe_base64_decode(uidb64))
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        email = None
    if email is not None and subscription_token.check_token("Customer", token):
        response = subscribe(email)
        if response:
            if response == 400:
                request.session["email_confirm"] = {"message": "You are already subscribed", "success": False}
            else:
                return HttpResponse("Some errors encountered. Try again later...")
        else:
            request.session["email_confirm"] = {"message": "You are successfully subscribed", "success": True}
        return redirect("accounts:subscribe")
    else:
        request.session["email_confirm"] = {"message": "Verification link is invalid!", "success": False}
        return redirect("accounts:subscribe")


def change_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        unsubscribe(user.email)
        user.email = user.profile.temp_email
        user.profile.temp_email = ""
        user.save()
        request.session["email_confirm"] = {
            "message": "Thank you for your email confirmation. Now your email is changed", "success": True}
        if user.profile.subscription:
            response = subscribe(user.email)
            if response:
                if response != 400:
                    user.profile.subscription = False
                    user.profile.save()
                    request.session["email_confirm"][
                        "message"] += " \nWe had some problems with newslatters subscription. \nResubscribe later..."
        return redirect("accounts:profile")
    else:
        request.session["email_confirm"] = {"message": "Change email link is invalid!", "success": False}
        return redirect("accounts:profile")


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        logout(request)
        request.session["email_confirm"] = {
            "message": "Thank you for your email confirmation. Now you can login your account", "success": True}
        if user.profile.subscription:
            response = subscribe(user.email)
            if response:
                if response != 400:
                    user.profile.subscription = False
                    user.profile.save()
                    request.session["email_confirm"][
                        "message"] += " \nWe had some problems with newslatters subscription. \nResubscribe later..."
        return redirect("accounts:login")
    else:
        request.session["email_confirm"] = {"message": "Activation link is invalid!", "success": False}
        return redirect("accounts:login")


# VIEWS


def AgreementView(request):
    context = navbar()
    return render(request, 'accounts/agreement.html', context=context)


def LoginView(request):
    # get previous and current urls for redirecting
    urls = get_previous_and_current_url(request)
    if request.user.is_authenticated:
        return redirect(urls["previous_full_url"])

    context = navbar()
    context = context | email_confirm_check(request)

    # if login clicked
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # login
            user = form.get_user()
            login(request, user)
            if urls["current_url"] == urls["previous_url"]:
                return redirect("catalog:home")
            else:
                return redirect(urls["previous_full_url"])
        else:
            if 'username' in form.data:
                user = User.objects.filter(username=form.data['username']).first()
                if user:
                    if not user.is_active:
                        context["check_email"] = True
    else:
        form = AuthenticationForm()

    context["form"] = form
    return render(request, 'accounts/login.html', context=context)


def LogoutView(request):
    urls = get_previous_and_current_url(request)
    if not request.user.is_authenticated:
        return redirect("accounts:login")
    if request.method == "POST":
        cart = request.session.get("cart", OrderedDict())
        logout(request)
        request.session["cart"] = cart
    if urls["current_url"] == urls["previous_url"]:
        return redirect("catalog:home")
    else:
        return redirect(urls["previous_full_url"])


class ProfileViewClass:
    template_name = "accounts/profile.html"

    def __init__(self, request):
        self.request = request
        self.redirect = self.check_redirect()
        if not self.redirect:
            self.context = navbar()
            self.redirect = self.main()

    def check_redirect(self):
        if not self.request.user.is_authenticated:
            return redirect("accounts:login")

    def prepare_user_form_initial(self):
        user_form_initial = {'username': self.request.user.username, "first_name": self.request.user.first_name,
                             "last_name": self.request.user.last_name, "email": self.request.user.email}
        return user_form_initial

    def prepare_profile_form_initial(self):
        profile_form_initial = {'address': self.request.user.profile.address, "city": self.request.user.profile.city,
                                "country": self.request.user.profile.country,
                                "phone": self.request.user.profile.phone,
                                "delivery": self.request.user.profile.delivery,
                                "subscription": self.request.user.profile.subscription}
        return profile_form_initial

    def prepare_user_data(self):
        # profile_special = \
        #    ProfileModel.objects.filter(user=self.request.user).values("purchases", "ratings", "comments")[0]
        user = {"Username": self.request.user.username, "First name": self.request.user.first_name,
                "Last name": self.request.user.last_name, "Email": self.request.user.email,
                "Address": self.request.user.profile.address, "City": self.request.user.profile.city,
                "Country": self.request.user.profile.country, "Phone": self.request.user.profile.phone,
                "Delivery": self.request.user.profile.delivery,
                "Subscription": "Yes" if self.request.user.profile.subscription else "No",
                #        "Purchases": self.request.user.profile.purchases if profile_special["purchases"] else "None",
                #        "Comments": self.request.user.profile.comments if profile_special["comments"] else "None",
                #        "Ratings": self.request.user.profile.ratings if profile_special["ratings"] else "None",
                "Joined": self.request.user.date_joined, "Last login": self.request.user.last_login,
                }
        return user

    def main(self):
        self.context["profile"] = self.prepare_user_data()
        self.context = self.context | email_confirm_check(self.request)
        user_form_initial = self.prepare_user_form_initial()
        profile_form_initial = self.prepare_profile_form_initial()
        user_form = None
        profile_form = None
        if self.request.method == "POST":
            if self.request.POST.get("edit"):
                user_form = UserEditForm(initial=user_form_initial, instance=self.request.user)
                profile_form = ProfileEditForm(initial=profile_form_initial, instance=self.request.user.profile)
                self.context["profile"].pop("Joined", None)
                self.context["profile"].pop("Last login", None)
            if self.request.POST.get("edit-submit"):
                user_form = UserEditForm(self.request.POST, instance=self.request.user)
                profile_form = ProfileEditForm(self.request.POST, instance=self.request.user.profile)
                user = User.objects.filter(username=user_form.data["username"]).first()
                if user_form.is_valid() and profile_form.is_valid():
                    if user_form.cleaned_data["email"] != user.email:
                        try:
                            send_email(self.request, user, user_form.cleaned_data["email"], 'change_email')
                            messages.success(self.request, 'Check your email to apply email change')
                        except ValueError as v:
                            print(v)
                            messages.warning(self.request, 'Cannot send confirmation latter for email change -'
                                                           ' try again later...')
                        self.request.user.profile.temp_email = user_form.cleaned_data['email']
                        user_form.cleaned_data["email"] = user.email
                        self.request.user.email = user.email
                        user.save()
                    if profile_form.cleaned_data["subscription"] == True and profile_form_initial[
                        'subscription'] == False:
                        response = subscribe(self.request.user.email)
                        if response:
                            if response != 400:
                                self.request.user.profile.subscription = False
                                profile_form.cleaned_data["subscription"] = False
                                self.request.user.save()
                                messages.warning(self.request, 'Cannot subscribe you now'
                                                               ' try again later...')
                        else:
                            messages.success(self.request, 'You are successfully subscribed')
                    if profile_form.cleaned_data["subscription"] == False and profile_form_initial[
                        "subscription"] == True:
                        response = unsubscribe(self.request.user.email)
                        if response:
                            if response != 204:
                                self.request.user.profile.subscription = True
                                profile_form.cleaned_data["subscription"] = True
                                self.request.user.save()
                                messages.warning(self.request, 'Cannot unsubscribe you now'
                                                               ' try again later...')
                        else:
                            messages.success(self.request, 'You are successfully unsubscribed')
                    user_form.save()
                    profile_form.save()
                    self.context["profile"] = self.prepare_user_data()
                    messages.success(self.request, 'Profile details updated.')
                    user_form = None
                    profile_form = None
            if self.request.POST.get("delete"):
                self.context["delete_form"] = True
            if self.request.POST.get("delete-submit"):
                self.request.user.delete()
                messages.warning(self.request, "Your account has been deleted")
                return redirect("accounts:login")
        if user_form:
            self.context["user_form"] = user_form
            self.context["profile_form"] = profile_form
        return


def ProfileView(request):
    profile_prepare = ProfileViewClass(request)
    if profile_prepare.redirect:
        return profile_prepare.redirect
    return render(request, profile_prepare.template_name, context=profile_prepare.context)


class SignupViewClass:
    template_name = "accounts/signup.html"

    def __init__(self, request):
        self.request = request
        self.redirect = self.check_redirect()
        if not self.redirect:
            self.context = navbar()
            self.redirect = self.main()

    def check_redirect(self):
        urls = get_previous_and_current_url(self.request)
        if self.request.user.is_authenticated:
            return redirect(urls["previous_full_url"])

    # because
    # profile_form.instance = user.profile;
    # profile_form.save()
    # has no effect
    def update_profile(self, user, profile_form):
        profile = user.profile
        profile.address = profile_form.cleaned_data["address"]
        profile.city = profile_form.cleaned_data["city"]
        profile.country = profile_form.cleaned_data["country"]
        profile.phone = profile_form.cleaned_data["phone"]
        profile.delivery = profile_form.cleaned_data["delivery"]
        profile.agreement = profile_form.cleaned_data["agreement"]
        profile.subscription = profile_form.cleaned_data["subscription"]
        profile.save()

    def main(self):
        # if sign up clicked
        if self.request.method == "POST":
            user_form = SignupForm(self.request.POST)
            profile_form = SignupProfileForm(self.request.POST)
            if user_form.is_valid() and profile_form.is_valid():
                user = user_form.save(commit=False)
                user.is_active = False
                user.save()
                group = Group.objects.get(name='Customers')
                user.groups.add(group)
                self.update_profile(user, profile_form)
                try:
                    send_email(self.request, user, user_form.cleaned_data["email"], 'activation')
                except ValueError as v:
                    print(v)
                    user.delete()
                    return HttpResponse("Some errors encountered. Try again later")
                self.request.session["email_confirm"] = {
                    "message": "Please confirm your email address to complete the registration", "success": True}
                return redirect("accounts:login")
        else:
            user_form = SignupForm()
            profile_form = SignupProfileForm()
        self.context["user_form"] = user_form
        self.context["profile_form"] = profile_form
        return


def SignUpView(request):
    signup_prepare = SignupViewClass(request)
    if signup_prepare.redirect:
        return signup_prepare.redirect
    return render(request, signup_prepare.template_name, context=signup_prepare.context)


def PasswordReset(request):
    context = navbar()
    context = context | email_confirm_check(request)
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            associated_users = User.objects.filter(email__iexact=email)
            if associated_users:
                for user in associated_users:
                    # noinspection PyBroadException
                    try:
                        send_email(request, user, form.cleaned_data["email"], "reset")
                    except:
                        return HttpResponse("Some errors encountered. Try again later...")
                    request.session["email_confirm"] = {"message": "Check your email to reset password",
                                                        "success": True}
                    return redirect("accounts:reset")
            else:
                form.add_error(None, "No such email")
    else:
        form = PasswordResetForm()
    context["form"] = form
    return render(request, "accounts/password_reset.html", context=context)


def PasswordResetConfirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):

        context = navbar()

        user.is_active = True
        user.save()
        logout(request)

        if request.method == "POST":
            form = SetPasswordForm(data=request.POST, user=user)
            if form.is_valid():
                user = form.save()
                user.save()
                request.session["email_confirm"] = {"message": "Password is reseted successfully!", "success": True}
                return redirect("accounts:login")
        else:
            form = SetPasswordForm(user=user)

        context["form"] = form

        return render(request, "accounts/password_reset_confirm.html", context=context)
    else:
        request.session["email_confirm"] = {"message": "Reset link is invalid!", "success": False}
        return redirect("accounts:reset")


def PasswordChangeView(request):
    if not request.user.is_authenticated:
        redirect("accounts:redirect")

    context = navbar()

    form = PasswordChangeForm(user=request.user)
    if request.method == "POST":
        if request.POST.get('change-password'):
            form = PasswordChangeForm(user=request.user)
        if request.POST.get('reset'):
            form = PasswordChangeForm(data=request.POST or None, user=request.user, )
            if form.is_valid():
                form.save()
                return redirect("accounts:profile")
    else:
        form = PasswordChangeForm(user=request.user)
    context["form"] = form
    return render(request, "accounts/password_change.html", context=context)


def Subscribe(request):
    context = navbar()
    context = context | email_confirm_check(request)
    if request.method == "POST":
        form = SubscribeForm(request.POST)
        if form.is_valid():
            if request.user.is_authenticated and form.cleaned_data["email"] == request.user.email:
                response = subscribe(form.cleaned_data["email"])
                if response:
                    if response == 400:
                        messages.warning(request, "You are already subscribed")
                    else:
                        return HttpResponse("Some errors encountered. Try again later...")
                else:
                    messages.success(request, "Email received. thank You! ")
            else:
                try:
                    subscribe_send_email(request, "Customer", form.cleaned_data["email"])
                    messages.success(request, 'Check your email to apply subscription')
                except ValueError as v:
                    print(v)
                    messages.warning(request, 'Cannot send confirmation latter -'
                                              ' try again later...')
    else:
        form = SubscribeForm()
    context["form"] = form
    return render(request, "accounts/subscribe.html", context=context)


from django.forms.models import model_to_dict


def cart_processor(request, view_only=False, object_as_dict=True):
    context = {}
    cart = request.session.get("cart", OrderedDict())
    if cart:

        cart_total_price = 0
        if view_only:
            items = Cars.objects.filter(pk__in=cart)
            for item in items:
                pk = str(item.pk)
                if object_as_dict:
                    object = model_to_dict(item)
                    if object["image"]:
                        object["image"] = str(object["image"])
                    del object["characteristics"]
                    cart[pk]["object"] = object
                else:
                    cart[pk]["object"] = item
                cart[pk]["price_total"] = item.price * cart[pk]["quantity"]
                cart_total_price += cart[pk]["price_total"]
        else:
            items = Cars.objects.filter(pk__in=cart).filter(quantity__gte=1)
            available = []
            for item in items:
                pk = str(item.pk)
                available.append(str(item.pk))
                cart[pk]["object"] = item
                quantity = item.quantity
                cart[pk]["max"] = False
                if cart[pk]["quantity"] >= quantity:
                    cart[pk]["quantity"] = quantity
                    cart[pk]["max"] = True
                    if cart[pk]["quantity"] > quantity:
                        messages.warning(request, "Item: {} - changed quantity to {}, because only {} pcs remaining!"
                                         .format(cart[pk]["object"].title, cart[pk]["quantity"], cart[pk]["quantity"]))
                cart[pk]["price_total"] = item.price * cart[pk]["quantity"]
                cart_total_price += cart[pk]["price_total"]
            exclude = []
            for item in cart:
                if item not in available:
                    exclude.append(item)
            for item in exclude:
                messages.warning(request, "Item: {} - is not available any more"
                                 .format(cart[item]["object"]["title"]))
                cart.pop(item)
            cart_session = copy.deepcopy(cart)
            for item in cart_session:
                cart_session[item].pop("object")
                cart_session[item].pop("price_total")
                cart_session[item].pop("max")
            request.session["cart"] = cart_session
        context["cart_total_price"] = cart_total_price
        context["cart"] = cart
    return context


def CartView(request):
    context = navbar()
    context = context | cart_processor(request)
    return render(request, "accounts/cart.html", context=context)


def cart_controller(request):
    if request.method == "POST":
        cart = request.session.get("cart", OrderedDict())
        if not cart:
            cart = OrderedDict()
        if request.POST.get("add-to-cart"):
            item = request.POST.get("add-to-cart")
            if Cars.objects.filter(pk=item).filter(quantity__gte=1).exists():

                if cart.get(item):
                    cart[item]["quantity"] += 1
                else:
                    cart[item] = {"quantity": 1}
                request.session["cart"] = cart
                messages.success(request, "The item is added to the cart")
        if request.POST.get("remove-from-cart"):
            item = request.POST.get("remove-from-cart")
            cart.pop(item, None)
            request.session["cart"] = cart
        if request.POST.get("cart-minus-one"):
            item = request.POST.get("cart-minus-one")
            if cart.get(item):
                cart[item]["quantity"] -= 1
                if cart[item]["quantity"] == 0:
                    del cart[item]
            request.session["cart"] = cart
        if request.POST.get("cart-plus-one"):
            item = request.POST.get("cart-plus-one")
            if cart.get(item):
                cart[item]["quantity"] += 1
            request.session["cart"] = cart
    urls = get_previous_and_current_url(request)
    return redirect(urls["previous_full_url"])


class CheckoutClass:
    template_name = "accounts/checkout.html"

    def __init__(self, request):
        self.request = request
        self.redirect = self.check_redirect()
        if not self.redirect:
            self.context = navbar()
            self.redirect = self.main()

    def check_redirect(self):
        if self.request.method == "GET":
            return redirect("accounts:cart")

    def prepare_profile(self, form=None):
        if form:
            profile = {"First name": form.cleaned_data["first_name"],
                       "Last name": form.cleaned_data["last_name"], "Email": form.cleaned_data["email"],
                       "Address": form.cleaned_data["address"], "City": form.cleaned_data["city"],
                       "Country": form.cleaned_data["country"], "Phone": form.cleaned_data["phone"],
                       "Delivery": form.cleaned_data["delivery"], "Agreement": "Yes"}
            self.context["profile"] = profile
            self.request.session["checkout_profile_form_initial"] = form.cleaned_data
            self.request.session["checkout_profile"] = profile
        else:
            if self.request.user.is_authenticated:
                profile = {"First name": self.request.user.first_name,
                           "Last name": self.request.user.last_name, "Email": self.request.user.email,
                           "Address": self.request.user.profile.address, "City": self.request.user.profile.city,
                           "Country": self.request.user.profile.country, "Phone": self.request.user.profile.phone,
                           "Delivery": self.request.user.profile.delivery}
            else:
                profile = {"First name": "",
                           "Last name": "", "Email": "",
                           "Address": "", "City": "",
                           "Country": "", "Phone": "",
                           "Delivery": ""}
            self.context["profile"] = profile

    def prepare_form(self):
        profile_form_initial = self.request.session.pop("checkout_profile_form_initial", None)
        self.request.session.pop("checkout_profile", None)
        if not profile_form_initial:
            if self.request.user.is_authenticated:
                profile_form_initial = {'first_name': self.request.user.first_name,
                                        'last_name': self.request.user.last_name,
                                        'email': self.request.user.email, 'address': self.request.user.profile.address,
                                        "city": self.request.user.profile.city,
                                        "country": self.request.user.profile.country,
                                        "phone": self.request.user.profile.phone,
                                        "delivery": self.request.user.profile.delivery}
        self.context["form"] = CheckoutForm(initial=profile_form_initial)

    def reserve(self):
        cart = self.request.session.get("cart", OrderedDict())
        if cart:
            with transaction.atomic():
                items = Cars.objects.select_for_update().filter(pk__in=cart)
                for item in items:
                    pk = str(item.pk)
                    if not item.quantity >= cart[pk]["quantity"]:
                        cart_processor(self.request)
                        return redirect("accounts:cart")
                for item in items:
                    pk = str(item.pk)
                    item.quantity -= cart[pk]["quantity"]
                    item.save()
        else:
            messages.warning(self.request, "Reservation error: Cart is empty")
            return redirect("accounts:cart")

    def place_order(self):
        reserve = self.reserve()
        if reserve:
            return reserve
        cart = cart_processor(self.request, view_only=True, object_as_dict=False)
        with transaction.atomic():
            order = Order()
            if self.request.user.is_authenticated:
                order.user = self.request.user
            data = self.request.session.pop("checkout_profile_form_initial", None)
            order.first_name = data["first_name"]
            order.last_name = data["last_name"]
            order.email = data["email"]
            order.address = data["address"]
            order.city = data["city"]
            order.country = data["country"]
            order.phone = data["phone"]
            order.delivery = data["delivery"]
            order.agreement = data["agreement"]
            order.total_price = cart["cart_total_price"]
            order.save()
            in_order_number = 1
            for item in cart["cart"]:
                lineitem = LineItem()
                lineitem.order_id = order.id
                lineitem.model_id = cart["cart"][item]["object"].id
                lineitem.title = cart["cart"][item]["object"].title
                lineitem.price = cart["cart"][item]["object"].price
                lineitem.image = cart["cart"][item]["object"].image
                lineitem.quantity = cart["cart"][item]["quantity"]
                lineitem.in_order_number = in_order_number
                in_order_number += 1
                lineitem.save()
            self.request.session.pop("cart", None)
            messages.success(self.request, "Your order is received!")
            self.context["order_number"] = order.id
            order_details = {"profile": self.request.session.pop("checkout_profile", {}), "cart": cart["cart"],
                             "order_number": order.id, "cart_total_price": cart["cart_total_price"],
                             "bought_date": order.bought_date}
            send_email(self.request, "{} {}".format(order.first_name, order.last_name), order.email, "checkout",
                       order_details=order_details)

    def main(self):
        if self.request.POST.get("cancel"):
            self.request.session.pop("checkout_profile_form_initial", None)
            self.request.session.pop("checkout_profile", None)
            return redirect("accounts:cart")
        elif self.request.POST.get("edit"):
            self.prepare_form()
            self.prepare_profile()
        elif self.request.POST.get("confirm"):
            return self.place_order()
        elif self.request.POST.get("submit"):
            form = CheckoutForm(self.request.POST)
            if form.is_valid():
                self.prepare_profile(form)
                self.context |= cart_processor(self.request, view_only=True)
        else:
            self.checkout_1_of_2()

    def checkout_1_of_2(self):
        self.prepare_form()
        self.prepare_profile()


def CheckoutView(request):
    checkout_prepare = CheckoutClass(request)
    if checkout_prepare.redirect:
        return checkout_prepare.redirect
    return render(request, checkout_prepare.template_name, context=checkout_prepare.context)


def ProfileOrdersView(request):
    if request.user.is_authenticated:
        context = navbar()
        orders = Order.objects.filter(user=request.user)
        context |= {"orders": orders}
        return render(request, "accounts/profile_orders.html", context=context)
    else:
        return redirect(get_previous_and_current_url(request)["previous_full_url"])


def ProfileOrderDetailsView(request, pk):
    order = Order.objects.filter(pk=pk).first()
    if not order:
        return redirect(get_previous_and_current_url(request)["previous_full_url"])
    if order.user != request.user:
        return redirect(get_previous_and_current_url(request)["previous_full_url"])
    context = navbar()
    context["items"] = LineItem.objects.filter(order=order)
    order = {"Date": order.bought_date,
             "First name": order.first_name,
             "Last name": order.last_name, "Email": order.email,
             "Address": order.address, "City": order.city,
             "Country": order.country, "Phone": order.phone,
             "Delivery": order.delivery, "Agreement": "Agreed with Terms and conditions" if order.agreement else "No",
             "Status": order.get_status_display(), "TOTAL PRICE": str(order.total_price) + " $"}
    context["order"] = order
    return render(request, "accounts/profile_order_details.html", context=context)
