from django.shortcuts import render, redirect
from django.http import HttpResponse
from carts.models import CartItem
from .forms import OrderForm
from accounts.models import Account
from .models import Order, Payment, OrderProduct
from store.models import Product
from datetime import date
import json


# confirmation email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

# Create your views here.

from django.shortcuts import render, redirect
from .forms import OrderForm
from .models import Order
from datetime import date

def place_order(request):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)

    if cart_items.count() <= 0:
        return redirect('cart')

    tax = 0
    total_price = 0
    grand_total = 0
    for cart_item in cart_items:
        total_price += (cart_item.quantity * cart_item.product.price)
    tax = (2 * total_price) / 100
    grand_total = tax + total_price

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone_number = form.cleaned_data['phone_number']
            data.email = form.cleaned_data['email']
            data.address1 = form.cleaned_data['address1']
            data.address2 = form.cleaned_data['address2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            # Generate order number
            today = date.today()
            order_number = today.strftime("%Y%m%d") + str(data.id)
            data.order_number = today.strftime("%Y%m%d") + str(data.id)
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            cart_items = CartItem.objects.filter(user=current_user, is_active=True)
            context = {
                "tax": tax,
                "total_price": total_price,
                "grand_total": grand_total,
                "order": order,
                "cart_items": cart_items,
                "order_number": order_number,
            }
            return render(request, 'orders/payment.html', context)

    return redirect('checkout')


def payment(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, order_number=body['orderID'])
    print(body)
    
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        status = body['status'],
        amount_paid = order.order_total,
    )
    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()

    # Move cartitems to OrderProduct
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        ordered_product = OrderProduct()
        ordered_product.order = order
        ordered_product.payment = payment
        ordered_product.user = request.user
        ordered_product.product = item.product
        ordered_product.quantity = item.quantity
        ordered_product.product_price = item.product.price
        ordered_product.ordered = True
        ordered_product.save()

        ordered_product.variations.set(item.variations.all())
        ordered_product.save()

        # Reduce sold product stock quantity
        product = Product.objects.get(id=item.product.id)
        product.stock -= item.quantity
        product.save()

    #delete cart items after order payment
    cart_items.delete()

    #order confirmation email
    mail_subject = "Thank you for your Order!"
    message = render_to_string(
        "orders/order_recieved_mail.html",
        {
            "user": request.user,
            "order": order,
        },
    )
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    return render(request, 'orders/payment.html')