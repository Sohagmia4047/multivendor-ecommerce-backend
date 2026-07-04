from rest_framework import serializers
from .models import (
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
    OrderStatusHistory,
)

# =========================
# CATEGORY SERIALIZER
# =========================

class CategorySerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id",
            "cid",
            "title",
            "image",
            "products",
        ]

    def get_image(self, obj):
        request = self.context.get("request")

        if obj.image:
            return request.build_absolute_uri(obj.image.url)

        return ""
    def get_products(self, obj):
        return obj.products.count()


# =========================
# VENDOR SERIALIZER
# =========================

class VendorSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    class Meta:
        model = Vendor
        fields = [
            "id",
            "vid",
            "title",
            "image",
            "cover_image",
            "description",
            "address",
            "contact",
            "chat_res_time",
            "shipping_on_time",
            "authentic_rating",
            "days_return",
            "warranty_period",
            "products",
        ]

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return ""
    def get_products(self, obj):
      request = self.context.get("request")
      qs = obj.products.all()
      if request:
          status = request.GET.get("status")
          if status and status != "all":
              qs = qs.filter(product_status=status)
      return qs.count()

# =========================
# TAG SERIALIZER
# =========================

class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ["id", "title", "slug"]


# =========================
# PRODUCT IMAGE SERIALIZER
# =========================

class ProductImagesSerializer(serializers.ModelSerializer):

    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImages
        fields = [
            "id",
            "image",
            "date",
        ]

    def get_image(self, obj):
        request = self.context.get("request")

        if obj.image:
            return request.build_absolute_uri(obj.image.url)

        return ""


# =========================
# PRODUCT REVIEW SERIALIZER
# =========================

class ProductReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source="user.username",
        read_only=True
    )

    class Meta:
        model = ProductReview
        fields = [
            "id",
            "username",
            "review",
            "rating",
            "comment",
            "date",
        ]


# =========================
# PRODUCT SERIALIZER
# =========================

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    tags = TagsSerializer(many=True, read_only=True)
    vendor = VendorSerializer(read_only=True)
    reviews = ProductReviewSerializer(
        many=True,
        read_only=True
    )
    images = ProductImagesSerializer(
        many=True,
        read_only=True
    )
    image = serializers.SerializerMethodField()
    discount = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = [
            "id",
            "pid",
            "title",
            "description",
            "image",
            "price",
            "old_price",
            "specifications",
            "category",
            "vendor",
            "tags",
            "product_status",
            "status",
            "in_stock",
            "featured",
            "digital",
            "type",
            "stock_count",
            "life",
            "mfd",
            "sku",
            "date",
            "updated",
            "discount",
            "reviews",
            "images",
        ]

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return ""

    def get_discount(self, obj):
        return obj.get_percentage_discount()
    
    def create(self, validated_data):
      tags_data = validated_data.pop("tags", [])
      product = Product.objects.create(**validated_data)
      for tag in tags_data:
         if isinstance(tag, dict):
             title = tag.get("title")
         else:
             title = tag
         obj, _ = Tags.objects.get_or_create(title=title)
         product.tags.add(obj)
      return product

# =========================
# CART ORDER ITEM SERIALIZER
# =========================
class CartSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    total = serializers.SerializerMethodField()
    class Meta:
        model = Cart
        fields = [
            "id",
            "product",
            "qty",
            "total",
            "created_at",
        ]

    def get_total(self, obj):
        return obj.product.price * obj.qty

class CartOrderItemsSerializer(serializers.ModelSerializer):

    image = serializers.SerializerMethodField()

    class Meta:
        model = CartOrderItems
        fields = [
            "id",
            "invoice_no",
            "product_status",
            "item",
            "image",
            "qty",
            "price",
            "total",
        ]

    def get_image(self, obj):
        request = self.context.get("request")

        if obj.image:
            return request.build_absolute_uri(obj.image.url)

        return ""
class OrderStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusHistory
        fields = ["id", "status", "created_at"]

# =========================
# CART ORDER SERIALIZER
# =========================

class CartOrderSerializer(serializers.ModelSerializer):
    items = CartOrderItemsSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model = CartOrder
        fields = [
            "id",
            "user",
            "invoice_no",
            "price",
            "paid_status",
            "product_status",
            "order_date",
            "items",
            "status_history",
        ]

        read_only_fields = [
            "user",
            "invoice_no",
            "price",
            "paid_status",
            "product_status",
            "order_date",
            "status_history",
        ]


# =========================
# WISHLIST SERIALIZER
# =========================

class WishlistSerializer(serializers.ModelSerializer):

    product = ProductSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = [
            "id",
            "product",
            "date",
        ]


# =========================
# ADDRESS SERIALIZER
# =========================

class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address
        fields = "__all__"

        read_only_fields = [
            "id",
            "user",
            "created_at",
            "updated_at",
        ]

class InvoiceSerializer(serializers.ModelSerializer):
    items = CartOrderItemsSerializer(many=True, read_only=True)

    payment = serializers.SerializerMethodField()

    subtotal = serializers.SerializerMethodField()

    shipping = serializers.SerializerMethodField()

    tax = serializers.SerializerMethodField()

    grand_total = serializers.SerializerMethodField()

    customer_name = serializers.SerializerMethodField()

    customer_address = serializers.SerializerMethodField()
    discount = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = CartOrder

        fields = (
            "invoice_no",
            "order_date",
            "customer_name",
            "customer_address",
            "phone",
            "email",
            "product_status",
            "paid_status",
            "subtotal",
            "shipping",
            "tax",
            "price",
            "grand_total",
            "payment",
            "items",
            "discount",
            "created_at",
        )

    def get_customer_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def get_customer_address(self, obj):
        return f"{obj.address}, {obj.city}, {obj.district}, {obj.country}"

    def get_subtotal(self, obj):
        return sum(item.total for item in obj.items.all())
    def get_created_at(self, obj):
        return obj.order_date.isoformat()
    
    def get_price(self,obj):
        return obj.price

    def get_shipping(self, obj):
        return 60

    def get_tax(self, obj):
        return 0
    
    def get_discount(self, obj):
        return 0

    def get_grand_total(self, obj):
        subtotal = sum(item.total for item in obj.items.all())
        return subtotal + 60

    def get_payment(self, obj):

        payment = Payment.objects.filter(
            order_number=obj.invoice_no
        ).first()

        if not payment:
            return None

        return {
            "payment_type": payment.payment_type,
            "payment_status": payment.payment_status,
            "tran_id": payment.tran_id,
            "paid_at": payment.paid_at,
            "card_type": payment.card_type,
        }

# =========================
# DASHBOARD ORDER SERIALIZER
# =========================

class DashboardOrderSerializer(serializers.ModelSerializer):
    payment_status = serializers.SerializerMethodField()

    class Meta:
        model = CartOrder
        fields = [
            "id",
            "invoice_no",
            "order_date",
            "product_status",
            "paid_status",
            "payment_status",
            "price",
        ]

    def get_payment_status(self, obj):
        payment = Payment.objects.filter(
            order_number=obj.invoice_no
        ).first()

        if payment:
            return payment.payment_status

        return "pending"

# =========================
# TRACK ORDER SERIALIZER
# =========================

class TrackOrderSerializer(serializers.ModelSerializer):
    payment_status = serializers.SerializerMethodField()
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = CartOrder
        fields = [
            "invoice_no",
            "product_status",
            "paid_status",
            "order_date",
            "created_at",
            "price",
            "payment_status",
            "status_history",
        ]

    def get_payment_status(self, obj):
        payment = Payment.objects.filter(
            order_number=obj.invoice_no
        ).first()

        return payment.payment_status if payment else "pending"

    def get_created_at(self, obj):
        return obj.order_date.isoformat() if obj.order_date else None
