from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, ReviewRating
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id
from django.core.paginator import Paginator
from django.db.models import Q
from .forms import ReviewForm
from django.contrib import messages
from orders.models import OrderProduct

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
    
    if request.user.is_authenticated:
        try:
            is_ordered = OrderProduct.objects.filter(user=request.user, product__id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            is_ordered = False
    else:
        is_ordered = False
        
    # Get the reviews
    reviews = ReviewRating.objects.filter(product=single_product, status=True)
    
    context = {
        "single_product": single_product,
        "in_cart": in_cart,
        "is_ordered": is_ordered,
        "reviews": reviews,
    }
    return render(request, 'store/product_detail.html', context)


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword)).order_by('-created_date')
            context = {
                "products": products,
                "prod_count": products.count(),
            }
            return render(request, 'store/store.html', context)
        else:
            return redirect('store')
        

def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST,instance=reviews)
            form.save()
            messages.success(request, 'Thank you! your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.user = request.user
                data.product = Product.objects.get(id=product_id)
                data.subject = form.cleaned_data['subject']
                data.review = form.cleaned_data['review']
                data.rating = form.cleaned_data['rating']
                data.ip = request.META.get('REMOTE_ADDR')
                data.save()
                messages.success(request, 'Thank you! yout review has been submitted!')
            return redirect(url)