from django.shortcuts import render, redirect
from store.models import Product, Variation
from .models import Cart, CartItem
from django.http import HttpResponse
from pprint import pprint

# Create your views here.

def _cart_id(request):
    id = request.session.session_key
    if not id:                                          
        id = request.session.create()
    return id


def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)                              #get the product having id = product_id (add cart button of the product i clicked))
    product_variation = []                                                    #empty list which will contain all the variations of the product 
    if request.method == 'POST':                                              #capture the POST request
        for item in request.POST:                                             #looping the data present in POST request
            key = item                                                        
            value = request.POST[key]                                         #example: color=red and size=XXL (key will be the "color" and value will be "red")

            try:
                variation = Variation.objects.get(
                    product=product,                                          
                    variation_category__iexact=key,                           #get the object which contain key and value pair of clicked product in the Variation model
                    variation_value__iexact=value
                )                 
                product_variation.append(variation)                           #append the object in list product_variation
            except:
                pass    

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))                  
    except Cart.DoesNotExist:                                                 #We are checking if cart with our session_key is present or not, if it's present then we will just store it in cart variable otherwise create it
        cart = Cart.objects.create(
            cart_id = _cart_id(request),
        )
        cart.save()                                                           #save the cart

    product_exist_in_cart = CartItem.objects.filter(product=product, cart=cart).exists()     #check if the selected product is present in our cart or not

    if product_exist_in_cart:                                                 #if product present
        cart_item = CartItem.objects.filter(product=product, cart=cart)       #get the product from the cart
        ex_var_list = []                                                      #list for existing variations of the clicked product
        id = []                                                               #list to store id of the clicked product
        print(product_variation)
        for item in cart_item:                                                
            existing_variation = item.variations.all()                        #store the existing variations of a product
            ex_var_list.append(list(existing_variation))                      #append the list of existing_variation of product in "ex_var_list"
            id.append(item.id)                                                #append id of each variation of the product in list "id"

        if product_variation in ex_var_list:                                  #if product_variation is present in the ex_var_list
            index = ex_var_list.index(product_variation)                      #index of the product_variation present in ex_var_list
            item_id = id[index]                                               #get the id of that variation 
            item = CartItem.objects.get(product=product, id=item_id)          #get the product having that id 
            item.quantity += 1                                                #increase quantity by 1
            item.save()                                                       #save
        else:                                                                 #if product_varition is not present in the ex_var_list
            item = CartItem.objects.create(
                product=product,                                              #create a new item in the cart
                quantity=1, 
                cart=cart
            )
            item.variations.add(*product_variation)                           #add the product_variation
            item.save()
        
    else:                                                                     #if product not present
        cart_item = CartItem.objects.create(
            product = product,                                                #we will create a cart_item of the product in our cart having quantity 1
            cart = cart,
            quantity = 1,
        )                                 
        cart_item.variations.add(*product_variation)                          #add the product_variations to the cart_item and save it
        cart_item.save()

    return redirect('cart')


def remove_cart(request, product_id, cart_item_id):
    cart    = Cart.objects.get(cart_id=_cart_id(request))
    product = Product.objects.get(id=product_id)

    try:
        cart_item = CartItem.objects.get(cart=cart, product=product, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -=1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass

    return redirect('cart')


def remove_cart_item(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = Product.objects.get(id=product_id)
    cart_item = CartItem.objects.get(cart=cart, product=product, id=cart_item_id)
    
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