from django.contrib import admin
from .models import Order, Payment, OrderProduct

# Register your models here.

class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ["payment", "user", "product", "quantity", "product_price", "variations"]
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ["order_number", "full_name", "email", "phone_number", "full_address", "order_total", "tax", "status", "created_at", "is_ordered"]
    list_filter = ["status", "is_ordered"]
    search_fields = ["order_number", "full_name", "email", "phone_number"]
    list_per_page = 20
    inlines = [OrderProductInline]


class PaymentAdmin(admin.ModelAdmin):
    list_display = ["user", "payment_id", "payment_method", "amount_paid", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["user", "payment_id"]
    list_per_page = 20


admin.site.register(Order, OrderAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(OrderProduct)