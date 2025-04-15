from django.contrib import admin
from .models import Order, Payment, OrderProduct

# Register your models here.

class OrderAdmin(admin.ModelAdmin):
    list_display = ["order_number", "full_name", "email", "phone_number", "full_address", "order_total", "tax", "status", "created_at", "is_ordered"]
    list_filter = ["status", "is_ordered"]
    search_fields = ["order_number", "full_name", "email", "phone_number"]
    list_per_page = 20

admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(OrderProduct)