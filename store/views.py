from django.shortcuts import render, get_object_or_404, redirect
from .models import Product
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id

from django.core.paginator import Paginator

# Create your views here.

def store(request, category_slug = None):
    if category_slug != None:
        categories = get_object_or_404(Category, slug = category_slug)
        products   = Product.objects.filter(category=categories, is_available=True).order_by('id')
    else:
        products   = Product.objects.filter(is_available=True).order_by('id')

    prod_count = products.count()

    p = Paginator(products, 5)
    page_number = request.GET.get('page')                  #paginator
    page_products = p.get_page(page_number)          

    context = {
        "prod_count": prod_count,
        "products": page_products,
    }

    return render(request, 'store/store.html', context)

def product_detail(request, category_slug=None,  product_slug=None):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()

    except Exception as e:
        raise e
    
    context = {
        "single_product": single_product,
        "in_cart": in_cart,
    }

    return render(request, 'store/product_detail.html', context)