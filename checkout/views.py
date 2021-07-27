from django.shortcuts import (
    render, redirect, reverse, HttpResponse, get_object_or_404)
from django.contrib import messages
from django.views.decorators.http import require_POST
from .forms import OrderForm
from cart.contexts import cart_contents
import stripe
from django.conf import settings
from checkout.models import Category
from profile_page.models import UserProfile
from .models import Order, OrderLineItem
from decimal import Decimal
import json


@require_POST
def cache_checkout_data(request):
    cart = request.session.get('cart', {})
    cart_meta_data = {}
    index = 0
    for item in cart.items():
        item_price = 0
        category = get_object_or_404(Category, pk=int(item[1]["category"]))
        item_price = category.price
        item_price = item_price * Decimal(item[1]["complexity"])
        item_price = item_price * Decimal(item[1]["variations"])
        if item[1]["fast_delivery"] == "True":
            item_price = item_price * Decimal(settings.FAST_DELIVERY_CHARGE)
        item_price = str(round(item_price, 2))

        category = item[1]["category"]
        complexity = item[1]["complexity"]
        variations = item[1]["variations"]
        fast_delivery = item[1]["fast_delivery"]
        price = str(item_price)
        # Data must be small to avoid exceeding stripe metadata charactor limit
        cart_meta_data[index] = f'{category}_{complexity}_' \
            f'{variations}_{fast_delivery}_{price}'
        index += 1
        json_dump = json.dumps(cart_meta_data)
        if len(json_dump) > 500:
            cart_meta_data = {"Cart Data": "Too many characters"}
            json_dump = json.dumps(cart_meta_data)
    try:
        pid = request.POST.get('client_secret').split('_secret')[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            'cart': json_dump,
            'save_info': request.POST.get('save_info'),
            'username': request.user,
        })
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, 'Your payment failed, please try again later.')
        return HttpResponse(content=e, status=400)


def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    if request.method == 'POST':
        cart = request.session.get('cart', {})
        if request.user.is_authenticated:
            user_profile = get_object_or_404(UserProfile, user=request.user)
        else:
            user_profile = None
        form_data = {
            'full_name': request.POST['full_name'],
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
            'country': request.POST['country'],
            'postcode': request.POST['postcode'],
            'town_or_city': request.POST['town_or_city'],
            'street_address1': request.POST['street_address1'],
            'street_address2': request.POST['street_address2'],
            'county': request.POST['county'],
        }
        order_form = OrderForm(form_data)
        if order_form.is_valid():
            cart_items = {}
            order = order_form.save(commit=False)
            for item in cart.items():
                category = get_object_or_404(
                    Category, pk=int(item[1]["category"]))
                item_price = category.price
                item_price = item_price * Decimal(item[1]["complexity"])
                item_price = item_price * Decimal(item[1]["variations"])
                if item[1]["fast_delivery"] == "True":
                    item_price = item_price * Decimal(
                        settings.FAST_DELIVERY_CHARGE)
                item_price = round(float(item_price), 2)

                id = item[0]
                product = {
                    "category": item[1]["category"],
                    "complexity": item[1]["complexity"],
                    "variations": item[1]["variations"],
                    'user_description': item[1]["user_description"],
                    'fast_delivery': item[1]["fast_delivery"],
                    'price': str(item_price)}
                cart_items[id] = product

            pid = request.POST.get('client_secret').split('_secret')[0]
            order.stripe_pid = pid
            order.original_cart = json.dumps(cart_items)
            order.user_profile = user_profile
            order.save()

            for item in cart_items.items():
                order_line_item = OrderLineItem(
                    order=order,
                    category=category,
                    complexity=item[1]["complexity"],
                    variations=item[1]["variations"],
                    user_description=item[1]["user_description"],
                    fast_delivery=item[1]["fast_delivery"],
                    lineitem_total=float(item[1]["price"])
                )
                order_line_item.save()

            request.session['save_info'] = 'save-info' in request.POST
            return redirect(
                reverse('checkout_success', args=[order.order_number]))

        else:
            messages.error(
                request, 'There was an error with your form. ' /
                'Please double check your information.')

    else:
        cart = request.session.get('cart', {})
        if not cart:
            messages.error(
                request, "There's nothing in your cart at the moment")
            return redirect(reverse('products'))

        current_cart = cart_contents(request)
        grand_total = current_cart['total']
        stripe_total = round(grand_total * 100)
        stripe.api_key = stripe_secret_key
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
        )

        if request.user.is_authenticated:
            try:
                profile = UserProfile.objects.get(user=request.user)
                order_form = OrderForm(initial={
                    'full_name': profile.user.get_full_name(),
                    'email': profile.user.email,
                    'phone_number': profile.default_phone_number,
                    'country': profile.default_country,
                    'postcode': profile.default_postcode,
                    'town_or_city': profile.default_town_or_city,
                    'street_address1': profile.default_street_address1,
                    'street_address2': profile.default_street_address2,
                    'county': profile.default_county,
                })
            except UserProfile.DoesNotExist:
                order_form = OrderForm()
        else:
            order_form = OrderForm()

    if not stripe_public_key:
        messages.warning(
            request, 'Stripe public key is missing. '
            'Did you forget to set it in your environment?')

    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
    }

    return render(request, template, context)


def checkout_success(request, order_number):
    """
    Handle successful checkouts
    """
    save_info = request.session.get('save_info')
    order = get_object_or_404(Order, order_number=order_number)
    messages.success(request, f'Order successfully processed! \
        Your order number is {order_number}. A confirmation \
        email will be sent to {order.email}.')

    if 'cart' in request.session:
        del request.session['cart']

    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
    }

    return render(request, template, context)