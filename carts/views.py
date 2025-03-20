from django.shortcuts import render, redirect
from store.models import Product
from .models import Cart, CartItem
from django.http import HttpResponse

# Create your views here.

def _cart_id(request):
    id = request.session.session_key
    if not id:
        id = request.session.create()
    return id


def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)                            #get the product

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))                  #get the cart having current session as it's id
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request),
        )
        cart.save()

    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)        #increment quantity of a product in cart
        cart_item.quantity +=1
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product = product,
            cart = cart,
            quantity = 1,
        )
    cart_item.save()
    return redirect('cart')


def remove_cart(request, product_id):
    cart    = Cart.objects.get(cart_id=_cart_id(request))
    product = Product.objects.get(id=product_id)
    cart_item = CartItem.objects.get(cart=cart, product=product)

    if cart_item.quantity > 1:
        cart_item.quantity -=1
        cart_item.save()
    else:
        cart_item.delete()

    return redirect('cart')


def remove_cart_item(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = Product.objects.get(id=product_id)
    cart_item = CartItem.objects.get(cart=cart, product=product)
    cart_item.delete()

    return redirect('cart')


def cart(request, total_price=0, total_quantity=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total_price += (cart_item.quantity*cart_item.product.price)
            total_quantity += (cart_item.quantity)
        tax = (2*total_price)/100
        grand_total = tax + total_price
    except CartItem.DoesNotExist:
        pass               #just pass (ignore)

    context = {
        "total_price": total_price,
        "tax": tax,
        "grand_total": grand_total,
        "total_quantity": total_quantity,
        "cart_items": cart_items,
    }
    return render(request, 'store/cart.html', context)