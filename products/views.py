# from django.shortcuts import render

# Create your views here.
from auctions.forms import AuctionForm
from auctions.models import Auction, Bid
from django.db.models import Prefetch

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, Category
from .forms import ProductForm


def product_list(request):
    products = Product.objects.filter(status='active').order_by('-created_at')

    # Search by product title
    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(title__icontains=search_query)

    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)

    categories = Category.objects.all()

    return render(request, 'products/product_list.html', {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_id,
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, status='active')

    return render(request, 'products/product_detail.html', {
        'product': product
    })


# @login_required
# def product_create(request):
#     if request.method == 'POST':
#         form = ProductForm(request.POST, request.FILES)
#         if form.is_valid():
#             product = form.save(commit=False)
#             product.seller = request.user
#             product.save()
#             return redirect('product_list')
#     else:
#         form = ProductForm()

#     return render(request, 'products/product_form.html', {'form': form})




@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        auction_form = AuctionForm(request.POST)

        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user

            if product.sale_type == 'auction':
                if auction_form.is_valid():
                    product.save()

                    Auction.objects.create(
                        product=product,
                        starting_price=auction_form.cleaned_data['starting_price'],
                        start_time=auction_form.cleaned_data['start_time'],
                        end_time=auction_form.cleaned_data['end_time'],
                    )

                    return redirect('product_list')

            else:
                product.save()
                return redirect('product_list')

    else:
        form = ProductForm()
        auction_form = AuctionForm()

    return render(request, 'products/product_form.html', {
        'form': form,
        'auction_form': auction_form,
    })


@login_required
def my_products(request):
    products = Product.objects.filter(
        seller=request.user
    ).order_by('-created_at').prefetch_related(
        Prefetch(
            'auction__bids',
            queryset=Bid.objects.select_related(
                'bidder'
            ).order_by('-amount', '-created_at')
        )
    )

    return render(request, 'products/my_products.html', {
        'products': products
    })
def home(request):
    return render(request, 'products/home.html')