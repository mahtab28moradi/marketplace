
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

from products.models import Product
from auctions.models import Bid
from .models import Order


@login_required
def buy_product(request, product_id):

    if request.method != 'POST':
        return redirect('product_detail', product_id=product_id)

    with transaction.atomic():

        product = get_object_or_404(
            Product.objects.select_for_update(),
            id=product_id
        )

        if product.seller == request.user:
            messages.error(request, "You cannot buy your own product.")
            return redirect('product_detail', product_id=product.id)

        if product.status != 'active':
            messages.error(request, "This product is no longer available.")
            return redirect('product_detail', product_id=product.id)

        if product.sale_type != 'direct':
            messages.error(request, "This product is available through auction.")
            return redirect('product_detail', product_id=product.id)

        order = Order.objects.create(
            product=product,
            buyer=request.user,
            seller=product.seller,
            amount=product.price,
            status='pending'
        )

        product.status = 'sold'
        product.save(update_fields=['status'])

    return render(request, 'orders/order_success.html', {
        'order': order
    })


@login_required
def my_purchases(request):

    orders = Order.objects.filter(
        buyer=request.user
    ).select_related(
        'product', 'seller'
    ).order_by('-created_at')

    bids = Bid.objects.filter(
        bidder=request.user
    ).select_related(
        'auction__product',
        'auction__product__seller'
    ).order_by('-created_at')

    return render(request, 'orders/my_purchases.html', {
        'orders': orders,
        'bids': bids,
    })
