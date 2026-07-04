from django.contrib import admin
from core.models import (
    Category,
    Vendor,
    Tags,
    Product,
    ProductImages,
    CartOrder,
    CartOrderItems,
    ProductReview,
    Wishlist,
    Address,
    Cart,
    Payment,
    PaymentDetail,
    OrderStatusHistory
)


# =========================
# CATEGORY ADMIN
# =========================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["cid", "title", "category_image"]
    search_fields = ["title"]


# =========================
# VENDOR ADMIN
# =========================

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "vendor_image",
        "contact",
        "address",
    ]

    search_fields = [
        "title",
        "contact",
    ]


# =========================
# TAGS ADMIN
# =========================

@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = ["title", "slug"]
    search_fields = ["title", "slug"]


# =========================
# PRODUCT IMAGES INLINE
# =========================

class ProductImagesAdmin(admin.TabularInline):
    model = ProductImages
    extra = 1


# =========================
# PRODUCT ADMIN
# =========================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImagesAdmin]

    list_display = [
        "title",
        "product_image",
        "price",
        "old_price",
        "category",
        "product_status",
        "featured",
        "in_stock",
    ]

    list_editable = [
        "price",
        "old_price",
        "product_status",
        "featured",
        "in_stock",
    ]

    search_fields = [
        "title",
        "sku",
    ]

    list_filter = [
        "product_status",
        "featured",
        "in_stock",
        "digital",
        "category",
    ]

    list_per_page = 10


# =========================
# PRODUCT IMAGES ADMIN
# =========================

@admin.register(ProductImages)
class ProductImagesAdminView(admin.ModelAdmin):
    list_display = [
        "product",
        "product_images",
        "date",
    ]


# =========================
# CART ORDER ADMIN
# =========================

@admin.register(CartOrder)
class CartOrderAdmin(admin.ModelAdmin):
    list_display = [
        "invoice_no",
        "first_name",
        "last_name",
        "phone",
        "email",
        "price",
        "paid_status",
        "product_status",
        "order_date",
    ]

    search_fields = [
        "invoice_no",
        "first_name",
        "last_name",
        "phone",
        "email",
    ]


# =========================
# CART ORDER ITEMS ADMIN
# =========================

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = [
        "product",
        "qty",
        "total_price",
        "created_at",
    ]

    search_fields = [
        "product__title",
    ]
    

    def total_price(self, obj):
        return obj.product.price * obj.qty

@admin.register(CartOrderItems)
class CartOrderItemsAdmin(admin.ModelAdmin):
    list_display = [
        "item",
        "invoice_no",
        "qty",
        "price",
        "total",
        "order_image",
    ]

    search_fields = [
        "item",
        "invoice_no",
    ]


# =========================
# PRODUCT REVIEW ADMIN
# =========================

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = [
        "product",
        "user",
        "rating",
        "date",
    ]

    search_fields = [
        "product__title",
        "user__username",
    ]

    list_filter = [
        "rating",
        "date",
    ]


# =========================
# WISHLIST ADMIN
# =========================

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "product",
        "date",
    ]

    search_fields = [
        "user__username",
        "product__title",
    ]


# =========================
# ADDRESS ADMIN
# =========================

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "first_name",
        "last_name",
        "phone",
        "district",
        "city",
        "is_default",
    )

    list_editable = (
        "is_default",
    )

    search_fields = (
        "first_name",
        "last_name",
        "phone",
        "city",
    )

    list_filter = (
        "is_default",
        "country",
    )

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        "order_number",
        "user",
        "amount",
        "payment_type",
        "payment_status",
        "created_at",
    ]

    search_fields = [
        "order_number",
        "user__username",
    ]

    list_filter = [
        "payment_type",
        "payment_status",
        "created_at",
    ]

@admin.register(PaymentDetail)
class PaymentDetailAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "cart",
        "card_number",
        "payment_date",
    ]

    search_fields = [
        "user__username",
        "card_number",
    ]

    list_filter = [
        "payment_date",
    ]

@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "order",
        "status",
        "created_at",
    ]

    search_fields = [
        "order__invoice_no",
        "status",
    ]

    list_filter = [
        "status",
        "created_at",
    ]
