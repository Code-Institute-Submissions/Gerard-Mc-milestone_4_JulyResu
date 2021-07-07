from django.shortcuts import render
from django.conf import settings
from .forms import OrderForm

def order(request):
    """ Returns the home page """
    form = OrderForm()
    context = {
        'FAST_DELIVERY_CHARGE': settings.FAST_DELIVERY_CHARGE,
        'form': form
    }

    return render(request, 'order/order.html', context)
