# from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.db.models import Max

from .models import Auction, Bid


def auction_detail(request, auction_id):
    auction = get_object_or_404(
        Auction.objects.select_related('product'),
        id=auction_id
    )

    highest_bid = auction.bids.aggregate(
        highest=Max('amount')
    )['highest']

    current_price = highest_bid or auction.starting_price
    now = timezone.now()

    if auction.status == 'cancelled':
        display_status = 'Cancelled'
    elif now < auction.start_time:
        display_status = 'Scheduled'
    elif now < auction.end_time:
        display_status = 'Active'
    else:
        display_status = 'Completed'

    bids = auction.bids.select_related(
        'bidder'
    ).order_by('-amount', '-created_at')

    return render(request, 'auctions/auction_detail.html', {
        'auction': auction,
        'current_price': current_price,
        'bids': bids,
        'now': now,
        'display_status': display_status,
    })


@login_required
def place_bid(request, auction_id):

    if request.method != 'POST':
        return redirect('auction_detail', auction_id=auction_id)

    with transaction.atomic():

        auction = get_object_or_404(
            Auction.objects.select_for_update(),
            id=auction_id
        )

        now = timezone.now()

        if auction.product.seller == request.user:
            messages.error(request, "You cannot bid on your own auction.")
            return redirect('auction_detail', auction_id=auction.id)

        if now < auction.start_time:
            messages.error(request, "This auction has not started yet.")
            return redirect('auction_detail', auction_id=auction.id)

        if now >= auction.end_time:
            messages.error(request, "This auction has ended.")
            return redirect('auction_detail', auction_id=auction.id)

        highest_bid = auction.bids.aggregate(
            highest=Max('amount')
        )['highest']

        minimum_bid = highest_bid or auction.starting_price

        try:
            amount = request.POST.get('amount')
            amount = float(amount)
        except (TypeError, ValueError):
            messages.error(request, "Please enter a valid bid amount.")
            return redirect('auction_detail', auction_id=auction.id)

        if amount <= minimum_bid:
            messages.error(
                request,
                f"Your bid must be higher than {minimum_bid}."
            )
            return redirect('auction_detail', auction_id=auction.id)

        Bid.objects.create(
            auction=auction,
            bidder=request.user,
            amount=amount
        )

        messages.success(request, "Your bid was submitted successfully!")

    return redirect('auction_detail', auction_id=auction.id)


def auction_result(request, auction_id):
    auction = get_object_or_404(
        Auction.objects.select_related('product'),
        id=auction_id
    )

    now = timezone.now()

    if now < auction.end_time:
        return render(request, 'auctions/auction_result.html', {
            'auction': auction,
            'not_finished': True,
        })

    with transaction.atomic():
        auction = Auction.objects.select_for_update().select_related(
            'product'
        ).get(id=auction_id)

        if auction.status != 'completed':
            winning_bid = auction.bids.select_related(
                'bidder'
            ).order_by('-amount', 'created_at').first()

            auction.status = 'completed'
            auction.save(update_fields=['status'])

            if winning_bid:
                auction.product.status = 'sold'
            else:
                auction.product.status = 'inactive'

            auction.product.save(update_fields=['status'])

        else:
            winning_bid = auction.bids.select_related(
                'bidder'
            ).order_by('-amount', 'created_at').first()

    return render(request, 'auctions/auction_result.html', {
        'auction': auction,
        'winning_bid': winning_bid,
        'not_finished': False,
    })
