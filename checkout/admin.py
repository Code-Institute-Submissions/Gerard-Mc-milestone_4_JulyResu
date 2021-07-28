from django.contrib import admin
from .models import Order, OrderLineItem, Category


class OrderLineItemAdminInline(admin.TabularInline):
    model = OrderLineItem
    fields = (
        'image', 'order', 'category', 'complexity', 'variations',
        'lineitem_total', 'fast_delivery', 'is_complete',
        'display_in_portfolio')
    readonly_fields = ('lineitem_total',)


class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderLineItemAdminInline,)

    readonly_fields = ('order_number', 'date', 'grand_total')

    fields = ('user_profile', 'order_number', 'date', 'full_name',
              'email', 'phone_number', 'country',
              'postcode', 'town_or_city', 'street_address1',
              'street_address2', 'county', 'original_cart',
              'stripe_pid', 'grand_total')
              
    list_display = (
        'order_number', 'date', 'full_name', 'grand_total', 'user_profile',
        'original_cart', 'stripe_pid')

    ordering = ('-date',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'price',
        'name',
        'friendly_name',
    )


admin.site.register(Category, CategoryAdmin)
admin.site.register(Order, OrderAdmin)
