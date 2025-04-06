from django.shortcuts import render, redirect
from store.models import Product, Variation
from .models import Cart, CartItem
from django.http import HttpResponse
from pprint import pprint
from django.contrib.auth.decorators import login_required

# Create your views here.


def _cart_id(request):
    id = request.session.session_key
    if not id:
        id = request.session.create()
    return id


def add_cart(request, product_id):
    current_user = request.user
    if current_user.is_authenticated:
        product = Product.objects.get(id=product_id)
        product_variation = []
        if request.method == "POST":
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value,)
                    product_variation.append(variation)
                except:
                    pass

        product_exist_in_cart = CartItem.objects.filter(product=product, user=current_user).exists()

        if product_exist_in_cart:
            cart_item = CartItem.objects.filter(product=product, user=current_user)
            ex_var_list = []
            id = []
            print(product_variation)
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id = id[index] 
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
            else:
                item = CartItem.objects.create(product=product, quantity=1, user=current_user)
                item.variations.add(*product_variation)
                item.save()

        else:
            cart_item = CartItem.objects.create(product=product, user=current_user, quantity=1)
            cart_item.variations.add(*product_variation)
            cart_item.save()

        return redirect("cart")
    else:
        product = Product.objects.get(id=product_id)
        product_variation = []
        if request.method == "POST":
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value,)
                    product_variation.append(variation)
                except:
                    pass

        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_cart_id(request))
            cart.save()

        product_exist_in_cart = CartItem.objects.filter(product=product, cart=cart).exists()

        if product_exist_in_cart:
            cart_item = CartItem.objects.filter(product=product, cart=cart)
            ex_var_list = []
            id = []
            print(product_variation)
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id = id[index] 
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
            else:
                item = CartItem.objects.create(product=product, quantity=1, cart=cart)
                item.variations.add(*product_variation)
                item.save()

        else:
            cart_item = CartItem.objects.create(product=product, cart=cart, quantity=1)
            cart_item.variations.add(*product_variation)
            cart_item.save()

        return redirect("cart")


def remove_cart(request, product_id, cart_item_id):
    product = Product.objects.get(id=product_id)

    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(cart=cart, product=product, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass

    return redirect("cart")


def remove_cart_item(request, product_id, cart_item_id):
    product = Product.objects.get(id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(cart=cart, product=product, id=cart_item_id)
    cart_item.delete()

    return redirect("cart")


def cart(request, total_price=0, total_quantity=0, cart_items=None):
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total_price += cart_item.quantity * cart_item.product.price
            total_quantity += cart_item.quantity
        tax = (2 * total_price) / 100
        grand_total = tax + total_price
    except Cart.DoesNotExist:
        tax = 0
        grand_total = 0

    context = {
        "total_price": total_price,
        "tax": tax,
        "grand_total": grand_total,
        "total_quantity": total_quantity,
        "cart_items": cart_items,
    }
    return render(request, "store/cart.html", context)


@login_required(login_url="login")
def checkout(request, total_price=0, total_quantity=0, cart_items=None):
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total_price += cart_item.quantity * cart_item.product.price
            total_quantity += cart_item.quantity
        tax = (2 * total_price) / 100
        grand_total = tax + total_price
    except Cart.DoesNotExist:
        tax = 0
        grand_total = 0

    context = {
        "total_price": total_price,
        "tax": tax,
        "grand_total": grand_total,
        "total_quantity": total_quantity,
        "cart_items": cart_items,
    }
    return render(request, "store/checkout.html", context)
