from django.shortcuts import render, redirect
from django.http import HttpResponse
from carts.models import CartItem
from .forms import OrderForm
from .models import Order
from datetime import date

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
            }
            return render(request, 'orders/payment.html', context)

    return redirect('checkout')


def payment(request):
    return render(request, 'orders/payment.html')