from django.shortcuts import get_object_or_404, render, redirect
from .forms import RegistrationForm, UserForm, UserProfileForm
from .models import Account, UserProfile
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from orders.models import Order, Payment, OrderProduct

# verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from carts.models import Cart, CartItem
from carts.views import _cart_id

import requests

# Create your views here.


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            email = form.cleaned_data["email"]
            phone_number = form.cleaned_data["phone_number"]
            password = form.cleaned_data["password"]
            username = email.split("@")[0]

            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                phone_number=phone_number,
                password=password,
            )
            user.save()

            # User Activation email
            current_site = get_current_site(request)
            mail_subject = "Please activate your account"
            message = render_to_string(
                "accounts/verification.html",
                {
                    "user": user,
                    "domain": current_site,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": default_token_generator.make_token(user),
                },
            )
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            return redirect("/account/login/?command=verification&email=" + email)

    else:
        form = RegistrationForm()

    context = {
        "form": form,
    }
    return render(request, "accounts/register.html", context)


def login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = auth.authenticate(email=email, password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_exist = CartItem.objects.filter(cart=cart).exists()

                if is_cart_exist:
                    # getting all the items in cart
                    cart_items = CartItem.objects.filter(cart=cart)

                    #getting all the variations in cart
                    product_variation = []
                    for item in cart_items:
                        variations = item.variations.all()
                        product_variation.append(list(variations))

                    #getting all the variations of the cart of user
                    user_cart_items = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id = []
                    for item in user_cart_items:
                        variations = item.variations.all()
                        ex_var_list.append(list(variations))
                        id.append(item.id)

                    #product variation = [1, 2, 3, 4, 5, 6]
                    #ex_var_list = [3, 4, 7]
                    #id = [usercart_item1, usercart_item2, usercart_item3]

                    for i in range(len(product_variation)):
                        p = product_variation[i]
                        item = cart_items[i]

                        if p in ex_var_list:
                            index = ex_var_list.index(p)
                            item_id = id[index]
                            user_cart_item = CartItem.objects.get(id=item_id)
                            user_cart_item.quantity += 1
                            user_cart_item.user = user
                            user_cart_item.save()
                        else:
                            item.user = user
                            item.save()
            except:
                    pass

            auth.login(request, user)
            messages.success(request, "You are now logged in.")
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    return redirect(params['next'])
            except:
                return redirect("dashboard")
        else:
            messages.error(request, "Invalid Login Credentials")
            return redirect("login")

    return render(request, "accounts/login.html")


@login_required(login_url="login")
def dashboard(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True)
    orders_count = orders.count()
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    context = {
        'orders_count': orders_count,
        'user_profile': user_profile,
    }
    return render(request, "accounts/dashboard.html", context)


@login_required(login_url="login")
def logout(request):
    auth.logout(request)
    messages.success(request, "You are logged out")
    return redirect("login")


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Congratulations! your account has been verified")
        return redirect("login")
    else:
        messages.error(request, "Invalid activation link")
        return redirect("register")


def forgotpassword(request):
    if request.method == "POST":
        email = request.POST["email"]

        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # Reset Password email
            current_site = get_current_site(request)
            mail_subject = "Reset your password"
            message = render_to_string(
                "accounts/reset_password_email.html",
                {
                    "user": user,
                    "domain": current_site,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": default_token_generator.make_token(user),
                },
            )
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(
                request, "Password reset email has been sent to you email address"
            )

            return redirect("login")
        else:
            messages.error(request, "Account does not exist")
            return redirect("forgotpassword")

    return render(request, "accounts/forgotpassword.html")


def validate_password(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session["uid"] = uid
        messages.success(request, "Please reset the password")
        return redirect("reset_password")
    else:
        messages.error(request, "This Link has been expired")
        return redirect("login")


def reset_password(request):
    if request.method == "POST":
        new_password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if new_password != confirm_password:
            messages.error(request, "Password do not match!")
            return redirect("reset_password")
        elif new_password == "":
            messages.error(request, "password can not be empty")
            return redirect("reset_password")
        else:
            uid = request.session["uid"]
            user = Account.objects.get(pk=uid)
            user.set_password(new_password)
            user.save()
            messages.success(request, "Password reset successfully")
            return redirect("login")

    return render(request, "accounts/resetpassword.html")


@login_required(login_url=login)
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'accounts/my_orders.html', context)

@login_required(login_url=login)
def order_detail(request, order_id):
    order = Order.objects.get(order_number=order_id)
    orderProduct = OrderProduct.objects.filter(order__order_number=order_id)
    
    sub_total = 0
    for i in orderProduct:
        sub_total += (i.product_price * i.quantity)
    grand_total = sub_total + order.tax

    context = {
        'OrderProduct': orderProduct,
        'order': order,
        'sub_total': sub_total,
        'grand_total': grand_total,
    }
    return render(request, 'accounts/order_detail.html', context)

@login_required(login_url=login)
def edit_profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=user_profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'user_profile': user_profile,
    }
    return render(request, 'accounts/edit_profile.html', context)


@login_required(login_url=login)
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password updated successfully.')
                return redirect('change_password')
            else:
                messages.error(request, 'Please enter valid current password')
                return redirect('change_password')
        else:
            messages.error(request, 'Password does not match.')
            return redirect('change_password')

        
    return render(request, 'accounts/change_password.html')