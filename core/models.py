from django.db import models
from shortuuidfield import ShortUUIDField
from django.utils.safestring import mark_safe
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField
from bs4 import BeautifulSoup, Comment
User = get_user_model()


# =========================
# STATUS CHOICES
# =========================

STATUS_CHOICES = (
    ("not_confirmed", "Not Confirmed"),
    ("confirmed", "Confirmed"),
    ("picked", "Picked"),
    ("delivered", "Delivered"),
)

STATUS = (
    ("draft", "Draft"),
    ("disabled", "Disabled"),
    ("rejected", "Rejected"),
    ("in_review", "In Review"),
    ("published", "Published"),
)

RATING = (
    (1, "⭐"),
    (2, "⭐⭐"),
    (3, "⭐⭐⭐"),
    (4, "⭐⭐⭐⭐"),
    (5, "⭐⭐⭐⭐⭐"),
)


# =========================
# CATEGORY MODEL
# =========================

class Category(models.Model):
    cid = ShortUUIDField(unique=True)
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="category")
    class Meta:
        verbose_name_plural = "Categories"

    def category_image(self):
        if self.image:
            return mark_safe(
                '<img src="%s" width="50" height="50" />' % self.image.url
            )
        return "No Image"

    def __str__(self):
        return self.title


def clean_html(html):
    if not html:
        return html

    soup = BeautifulSoup(html, "html.parser")

    comments = soup.find_all(
        string=lambda text: isinstance(text, Comment)
    )

    for comment in comments:
        comment.extract()

    return str(soup)


# =========================
# VENDOR MODEL
# =========================

class Vendor(models.Model):
    vid = ShortUUIDField(unique=True)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="vendors"
    )
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="vendors")
    cover_image = models.ImageField(upload_to="vendors", default="vendor.jpg")
    # description = models.TextField(null=True, blank=True)
    description = RichTextUploadingField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    contact = models.CharField(max_length=20, null=True, blank=True)
    chat_res_time = models.CharField(max_length=100, null=True, blank=True)
    shipping_on_time = models.CharField(max_length=100, null=True, blank=True)
    authentic_rating = models.CharField(max_length=100, null=True, blank=True)
    days_return = models.CharField(max_length=100, null=True, blank=True)
    warranty_period = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Vendors"

    def vendor_image(self):
        if self.image:
            return mark_safe(
                '<img src="%s" width="50" height="50" />' % self.image.url
            )
        return "No Image"
    
    def save(self, *args, **kwargs):
        self.description = clean_html(self.description)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# =========================
# TAGS MODEL
# =========================

class Tags(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(blank=True, unique=True)

    class Meta:
        verbose_name_plural = "Tags"
    
    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            while Tags.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)


# =========================
# PRODUCT MODEL
# =========================

class Product(models.Model):
    pid = ShortUUIDField(unique=True)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="products"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="products"
    )
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.SET_NULL,
        null=True,
        related_name="products"
    )
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="products")
    # description = models.TextField(null=True, blank=True)
    description = RichTextUploadingField(null=True, blank=True)
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    old_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    # specifications = models.TextField(null=True, blank=True)
    specifications = RichTextUploadingField(null=True, blank=True)
    type = models.CharField(max_length=100, null=True, blank=True, default="Organic")
    stock_count = models.CharField(max_length=100, null=True, blank=True, default="8")
    life = models.CharField(max_length=100, null=True, blank=True, default="100 Days")
    mfd = models.DateField(auto_now_add=False, null=True, blank=True)
    tags = models.ManyToManyField(Tags, blank=True)
    product_status = models.CharField(
        choices=STATUS,
        max_length=20,
        default="in_review"
    )
    status = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    digital = models.BooleanField(default=False)
    sku = ShortUUIDField(unique=True)
    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Products"

    def product_image(self):
        if self.image:
            return mark_safe(
                '<img src="%s" width="50" height="50" />' % self.image.url
            )
        return "No Image"

    def __str__(self):
        return self.title

    def get_percentage_discount(self):
        if self.old_price and self.price:
            discount = (
                (self.old_price - self.price)
                / self.old_price
            ) * 100

            return round(discount, 2)

        return 0
    
    def save(self, *args, **kwargs):
        self.description = clean_html(self.description)
        self.specifications = clean_html(self.specifications)
        super().save(*args, **kwargs)


# =========================
# PRODUCT IMAGES MODEL
# =========================

class ProductImages(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="images"
    )

    image = models.ImageField(upload_to="product_images")

    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Product Images"

    def product_images(self):
        if self.image:
            return mark_safe(
                '<img src="%s" width="50" height="50" />' % self.image.url
            )
        return "No Image"

    def __str__(self):
        if self.product:
            return self.product.title

        return "Product Image"


# =========================
# CART ORDER MODEL
# =========================

class Cart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="cart_items"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="cart_products"
    )
    qty = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["user", "product"]
        verbose_name_plural = "Cart"

    @property
    def total(self):
        return self.product.price * self.qty

    def __str__(self):
        return f"{self.user.username} - {self.product.title}"

class CartOrder(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    invoice_no = models.CharField(max_length=200)

    # Billing Information
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)

    company = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    country = models.CharField(
        max_length=100,
        default="Bangladesh",
        blank=True,
        null=True
    )

    district = models.CharField(max_length=100, blank=True, null=True)

    city = models.CharField(max_length=100, blank=True, null=True)

    address = models.TextField(blank=True, null=True)

    postcode = models.CharField(
        max_length=30,
        blank=True,
        null=True
    )

    phone = models.CharField(max_length=20, blank=True, null=True)

    email = models.EmailField()

    # Shipping Information
    ship_first_name = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    ship_last_name = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    ship_company = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    ship_district = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    ship_city = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    ship_address = models.TextField(
        blank=True,
        null=True
    )

    ship_postcode = models.CharField(
        max_length=30,
        blank=True,
        null=True
    )

    # Extra
    order_notes = models.TextField(
        blank=True,
        null=True
    )

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )

    paid_status = models.BooleanField(default=False)

    product_status = models.CharField(
        choices=STATUS_CHOICES,
        max_length=30,
        default="processing"
    )

    order_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Cart Orders"
    
    @property
    def get_total(self):
        return sum(item.total for item in self.items.all())

    def __str__(self):
        return self.invoice_no


# =========================
# CART ORDER ITEMS MODEL
# =========================

class CartOrderItems(models.Model):
    order = models.ForeignKey(
        CartOrder,
        on_delete=models.CASCADE,
        related_name="items"
    )

    invoice_no = models.CharField(max_length=200)

    product_status = models.CharField(max_length=200)

    item = models.CharField(max_length=200)

    image = models.ImageField(
        upload_to="cart_order_images"
    )

    qty = models.IntegerField(default=1)

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )

    class Meta:
        verbose_name_plural = "Cart Order Items"

    def order_image(self):
        if self.image:
            return mark_safe(
                '<img src="%s" width="50" height="50" />' % self.image.url
            )
        return "No Image"

    def __str__(self):
        return self.item


# =========================
# PRODUCT REVIEW MODEL
# =========================

class ProductReview(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        related_name="reviews"
    )

    review = models.TextField()

    rating = models.IntegerField(
        choices=RATING,
        default=1
    )

    comment = models.TextField(null=True, blank=True)

    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Product Reviews"

    def __str__(self):
        if self.product:
            return self.product.title

        return "Review"

    def get_rating(self):
        return self.rating


# =========================
# WISHLIST MODEL
# =========================

class Wishlist(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="wishlist"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True
    )

    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Wishlists"

    def __str__(self):
        if self.product:
            return self.product.title

        return "Wishlist"


# =========================
# ADDRESS MODEL
# =========================

class Address(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="addresses"
    )

    first_name = models.CharField(
        max_length=100,
        blank=True
    )

    last_name = models.CharField(
        max_length=100,
        blank=True
    )

    company = models.CharField(
        max_length=255,
        blank=True
    )

    email = models.EmailField(
        blank=True
    )

    phone = models.CharField(
        max_length=20,
        blank=True
    )

    country = models.CharField(
        max_length=100,
        default="Bangladesh"
    )

    district = models.CharField(
        max_length=100,
        blank=True
    )

    city = models.CharField(
        max_length=100,
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    postcode = models.CharField(
        max_length=30,
        blank=True
    )

    is_default = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name_plural = "Addresses"

    def __str__(self):
        return f"{self.user.username} - {self.address}"

class PaymentDetail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_details')
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE, related_name='payments')
    # ⚠️ Only store masked card (last 4 digit)
    card_number = models.CharField(max_length=4, null=True, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.cart.id} - {self.payment_date}"

class Payment(models.Model):

    PAYMENT_TYPE_CHOICES = [
        ("sslcommerz", "SSLCommerz"),
        ("bkash", "bKash"),
        ("nagad", "Nagad"),
        ("rocket", "Rocket"),
        ("cash", "Cash"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
        ("validated", "Validated"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    order_number = models.CharField(max_length=100)

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_type = models.CharField(
        max_length=30,
        choices=PAYMENT_TYPE_CHOICES,
        default="sslcommerz"
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="pending"
    )

    tran_id = models.CharField(
        max_length=100,
        unique=True
    )

    val_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    bank_tran_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    sessionkey = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    card_type = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    store_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    gateway_response = models.JSONField(
        default=dict,
        blank=True
    )

    ipn_response = models.JSONField(
        default=dict,
        blank=True
    )

    paid_at = models.DateTimeField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.order_number} - {self.payment_status}"

class OrderStatusHistory(models.Model):
    order = models.ForeignKey(
        CartOrder,
        on_delete=models.CASCADE,
        related_name="status_history"
    )

    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Order Status History"

    def __str__(self):
        return f"{self.order.invoice_no} - {self.status}"