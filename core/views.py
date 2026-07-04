from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import uuid
from django.utils.dateformat import format
from django.db.models import Sum, F
from django.shortcuts import redirect
from django.utils import timezone
from decimal import Decimal
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Product, Category, Vendor, Tags, ProductReview, Cart, CartOrder, CartOrderItems, Payment, Address, OrderStatusHistory
from core.serializers import ProductSerializer, CategorySerializer, VendorSerializer, DashboardOrderSerializer, TagsSerializer, CartSerializer, AddressSerializer, InvoiceSerializer, TrackOrderSerializer, OrderStatusHistorySerializer
from django.db import transaction
from rest_framework.permissions import AllowAny
from .sslcommerz import (
    initiate_ssl_payment,
    validate_ssl_payment,
    initiate_ssl_payment,
)
 

@api_view(["GET"])
def product_list(request):
    products = Product.objects.filter(product_status="published", featured=True).order_by("-id")
    serializer = ProductSerializer(
        products,
        many=True,
        context={"request": request}
    )

    return Response(serializer.data)

@api_view(["GET"])
def product_list_page(request):
    products = Product.objects.all()

    serializer = ProductSerializer(
        products,
        many=True,
        context={"request": request}
    )

    return Response(serializer.data)

# 🔹 Get all categories
@api_view(["GET"])
def category_list(request):
    categories = Category.objects.all().order_by("-id")

    serializer = CategorySerializer(
        categories,
        many=True,
        context={"request": request}
    )

    return Response(serializer.data)
@api_view(["GET"])
def category_products_list(request, cid):
    try:
        category = Category.objects.get(cid=cid)
        products = Product.objects.filter(
            category=category,
            product_status="published",
            status=True,
            in_stock=True
        )
        serializer = ProductSerializer(
            products,
            many=True,
            context={"request": request}
        )

        return Response({
            "category": category.title,
            "products": serializer.data
        })

    except Category.DoesNotExist:
        return Response(
            {"error": "Category not found"},
            status=404
        )

@api_view(["GET"])
def vendor_list(request):
    status = request.GET.get("status", "all")
    vendors = Vendor.objects.all()
    if status != "all":
        vendors = vendors.filter(
            products__product_status=status
        ).distinct()
    serializer = VendorSerializer(
        vendors,
        many=True,
        context={"request": request}
    )
    return Response(serializer.data)

@api_view(["GET"])
def vendor_detail(request, vid):
    try:
        vendor = Vendor.objects.get(vid=vid)

        products = Product.objects.filter(
            vendor=vendor,
            product_status="published"
        ).order_by("-id")

        vendor_serializer = VendorSerializer(
            vendor,
            context={"request": request}
        )

        product_serializer = ProductSerializer(
            products,
            many=True,
            context={"request": request}
        )

        return Response({
            "vendor": vendor_serializer.data,
            "products": product_serializer.data
        })

    except Vendor.DoesNotExist:
        return Response(
            {"error": "Vendor not found"},
            status=404
        )

@api_view(["GET"])
def product_detail(request, id):
    try:
        product = Product.objects.get(id=id)
        serializer = ProductSerializer(
            product,
            context={"request": request}
        )

        return Response(serializer.data)

    except Product.DoesNotExist:
        return Response(
            {"error": "Product not found"},
            status=404
        )

@api_view(["GET"])
def products_by_tag(request, slug):
    tag = Tags.objects.get(slug=slug)

    products = Product.objects.filter(
        tags=tag,
        status=True
    ).distinct()

    serializer = ProductSerializer(
        products,
        many=True,
        context={"request": request}
    )

    return Response({
        "tag": tag.title,
        "products": serializer.data
    })

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_review(request, pid):
    try:
        product = Product.objects.get(id=pid)
        rating = request.data.get("rating")
        review = request.data.get("review")
        ProductReview.objects.create(
            user=request.user,
            product=product,
            rating=rating,
            review=review
        )

        return Response({
            "success": True,
            "message": "Review Added Successfully"
        })

    except Product.DoesNotExist:
        return Response({
            "success": False,
            "message": "Product Not Found"
        }, status=404)

@api_view(["GET"])
def tag_list(request):
    tags = Tags.objects.all().order_by("title")

    serializer = TagsSerializer(
        tags,
        many=True,
        context={"request": request}
    )
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_to_cart(request):

    product_id = request.data.get("product_id")
    qty = int(request.data.get("qty", 1))

    try:
        product = Product.objects.get(
            id=product_id,
            product_status="published"
        )

        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={"qty": qty}
        )

        if not created:
            cart_item.qty += qty
            cart_item.save()

        cart_count = Cart.objects.filter(
            user=request.user
        ).count()

        return Response({
            "success": True,
            "message": "Added To Cart",
            "cart_count": cart_count
        })

    except Product.DoesNotExist:
        return Response({
            "success": False,
            "message": "Product not found"
        }, status=404)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_cart(request):

    cart_items = Cart.objects.filter(
        user=request.user
    ).order_by("-id")

    serializer = CartSerializer(
        cart_items,
        many=True,
        context={"request": request}
    )

    total_price = sum(
        item.product.price * item.qty
        for item in cart_items
    )

    return Response({
        "cart": serializer.data,
        "total_price": total_price,
        "cart_count": cart_items.count()
    })

@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_cart(request, id):

    try:
        item = Cart.objects.get(
            id=id,
            user=request.user
        )

        qty = int(request.data.get("qty", 1))

        item.qty = qty
        item.save()

        return Response({
            "success": True,
            "message": "Cart Updated"
        })

    except Cart.DoesNotExist:
        return Response({
            "success": False
        }, status=404)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_cart_item(request, id):

    try:
        item = Cart.objects.get(
            id=id,
            user=request.user
        )

        item.delete()

        return Response({
            "success": True,
            "message": "Item Removed"
        })

    except Cart.DoesNotExist:
        return Response({
            "success": False
        }, status=404)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def clear_cart(request):
    Cart.objects.filter(user=request.user).delete()

    return Response({
        "message": "Cart cleared successfully"
    })


class SSLCommerzSuccessView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        return self.handle_callback(request)

    def get(self, request):
        return self.handle_callback(request)

    def handle_callback(self, request):
        data = request.POST if request.method == "POST" else request.GET
        tran_id = data.get("tran_id")
        val_id = data.get("val_id")
        frontend_base = settings.FRONTEND_BASE_URL
        payment = Payment.objects.filter(
            tran_id=tran_id
        ).first()

        if not payment:
            return redirect(f"{frontend_base}/payment-failed")

        try:
            validation = validate_ssl_payment(val_id)

        except Exception:
            payment.payment_status = "failed"
            payment.save()

            return redirect(
                f"{frontend_base}/payment-failed"
            )

        status_text = validation.get("status")

        amount = Decimal(
            str(validation.get("amount", "0"))
        )

        validated_tran_id = validation.get("tran_id")

        if (
            status_text in ["VALID", "VALIDATED"]
            and validated_tran_id == payment.tran_id
            and amount == payment.amount
        ):

            payment.payment_status = "completed"
            payment.val_id = validation.get("val_id")
            payment.bank_tran_id = validation.get("bank_tran_id")
            payment.card_type = validation.get("card_type")
            payment.store_amount = validation.get("store_amount")
            payment.gateway_response = validation
            payment.paid_at = timezone.now()

            payment.save()

            # ✅ UPDATE ORDER
            order = CartOrder.objects.filter(
                invoice_no=payment.order_number
            ).first()

            if order:
                order.paid_status = True
                order.product_status = "processing"
                order.save()

            # ✅ CLEAR USER CART
            Cart.objects.filter(
                user=payment.user
            ).delete()

            if order:
              return redirect(
                    f"{frontend_base}/payment-success?invoice={order.invoice_no}"
                )

            return redirect(
                f"{frontend_base}/payment-success"
            )

        payment.payment_status = "failed"
        payment.save()

        return redirect(
            f"{frontend_base}/payment-failed"
        )

class SSLCommerzFailView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        tran_id = request.data.get(
            "tran_id"
        )

        payment = Payment.objects.filter(
            tran_id=tran_id
        ).first()

        if payment:

            payment.payment_status = "failed"

            payment.gateway_response = dict(
                request.data
            )

            payment.save()

        return redirect(
            f"{settings.FRONTEND_BASE_URL}/payment-failed"
        )

class SSLCommerzCancelView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        tran_id = request.data.get(
            "tran_id"
        )

        payment = Payment.objects.filter(
            tran_id=tran_id
        ).first()

        if payment:

            payment.payment_status = "cancelled"

            payment.gateway_response = dict(
                request.data
            )

            payment.save()

        return redirect(
            f"{settings.FRONTEND_BASE_URL}/payment-cancel"
        )

class SSLCommerzIPNView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        tran_id = request.data.get(
            "tran_id"
        )

        payment = Payment.objects.filter(
            tran_id=tran_id
        ).first()

        if not payment:

            return Response(
                {"error": "Payment not found"},
                status=404
            )

        payment.ipn_response = dict(
            request.data
        )

        payment.save()

        return Response({
            "message": "IPN received"
        })

class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        try:

            user = request.user
            cart_items = Cart.objects.filter(user=user)

            if not cart_items.exists():
                return Response(
                    {"error": "Cart is empty"},
                    status=400
                )

            # ======================
            # CALCULATE TOTAL
            # ======================
            subtotal = sum(
                item.product.price * item.qty
                for item in cart_items
            )

            shipping_cost = Decimal("60.00")
            total_amount = Decimal(subtotal) + shipping_cost

            invoice_no = f"INV-{uuid.uuid4().hex[:10].upper()}"
            tran_id = f"TXN-{uuid.uuid4().hex[:16].upper()}"

            # ======================
            # CREATE ORDER
            # ======================
            with transaction.atomic():
                Address.objects.filter(
                 user=user,
                 is_default=True
                ).update(is_default=False)

                Address.objects.create(
                user=user,
                first_name=request.data.get("first_name"),
                last_name=request.data.get("last_name"),
                company=request.data.get("company"),
                email=request.data.get("email"),
                phone=request.data.get("phone"),
                country=request.data.get("country", "Bangladesh"),
                district=request.data.get("district"),
                city=request.data.get("city"),
                address=request.data.get("address"),
                postcode=request.data.get("postcode"),
                is_default=True,
                )       

                order = CartOrder.objects.create(
                    user=user,
                    invoice_no=invoice_no,
                    price=total_amount,
                    first_name=request.data.get("first_name"),
                    last_name=request.data.get("last_name"),
                    company=request.data.get("company"),
                    country=request.data.get("country", "Bangladesh"),
                    district=request.data.get("district"),
                    city=request.data.get("city"),
                    address=request.data.get("address"),
                    postcode=request.data.get("postcode"),
                    phone=request.data.get("phone"),
                    email=request.data.get("email"),
                    order_notes=request.data.get("order_notes"),
                    paid_status=False,
                    product_status="processing",
                    order_date=timezone.now(),
                )

                # ======================
                # ORDER ITEMS
                # ======================
                for item in cart_items:
                    CartOrderItems.objects.create(
                        order=order,
                        invoice_no=invoice_no,
                        product_status="processing",
                        item=item.product.title,
                        image=str(item.product.image) if item.product.image else "",
                        qty=item.qty,
                        price=item.product.price,
                        total=item.product.price * item.qty,
                    )

                # ======================
                # PAYMENT RECORD
                # ======================
                payment = Payment.objects.create(
                    user=user,
                    order_number=invoice_no,
                    amount=total_amount,
                    payment_type="sslcommerz",
                    payment_status="pending",
                    tran_id=tran_id,
                )

            # ======================
            # SSL PAYLOAD
            # ======================
            backend_base = settings.VITE_BASE_URL

            payload = {
                "store_id": settings.SSLCOMMERZ_STORE_ID,
                "store_passwd": settings.SSLCOMMERZ_STORE_PASSWORD,
                "total_amount": str(total_amount),
                "currency": "BDT",
                "tran_id": tran_id,

                "success_url": f"{backend_base}/core/payments/sslcommerz/success/",
                "fail_url": f"{backend_base}/core/payments/sslcommerz/fail/",
                "cancel_url": f"{backend_base}/core/payments/sslcommerz/cancel/",
                "ipn_url": f"{backend_base}/core/payments/sslcommerz/ipn/",

                "product_name": f"Order {invoice_no}",
                "product_category": "Ecommerce",
                "product_profile": "general",

                "cus_name": f"{order.first_name} {order.last_name}",
                "cus_email": order.email,
                "cus_add1": order.address,
                "cus_city": order.city,
                "cus_country": order.country,
                "cus_phone": order.phone,

                "value_a": str(payment.id),
                "value_b": invoice_no,
            }

            gateway_data = initiate_ssl_payment(payload)

            payment.gateway_response = gateway_data
            payment.sessionkey = gateway_data.get("sessionkey")
            payment.save()

            # ======================
            # ERROR HANDLING
            # ======================
            if gateway_data.get("status") != "SUCCESS":
                payment.payment_status = "failed"
                payment.save()

                return Response(
                    {
                        "error": gateway_data.get(
                            "failedreason",
                            "Payment session failed"
                        )
                    },
                    status=400
                )

            # ======================
            # SUCCESS RESPONSE
            # ======================
            return Response({
                "success": True,
                "payment_url": gateway_data.get("GatewayPageURL"),
                "invoice_no": invoice_no,
                "tran_id": tran_id,
            })

        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return Response(
              {"error": str(e)},
              status=500
            )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def default_address(request):

    address = (
        Address.objects
        .filter(
            user=request.user,
            is_default=True
        )
        .first()
    )

    if not address:
        return Response({})

    serializer = AddressSerializer(address)

    return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def save_address(request):

    Address.objects.filter(
        user=request.user,
        is_default=True
    ).update(is_default=False)

    serializer = AddressSerializer(data=request.data)

    if serializer.is_valid():

        serializer.save(
            user=request.user,
            is_default=True
        )

        return Response(serializer.data)

    return Response(
        serializer.errors,
        status=400
    )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def invoice_details(request, invoice_no):

    try:

        order = CartOrder.objects.get(
            invoice_no=invoice_no,
            user=request.user
        )

    except CartOrder.DoesNotExist:

        return Response(
            {
                "error":"Invoice not found"
            },
            status=404
        )

    serializer = InvoiceSerializer(
        order,
        context={
            "request":request
        }
    )

    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_orders(request):

    orders = (
        CartOrder.objects
        .filter(user=request.user)
        .order_by("-order_date")
    )

    serializer = DashboardOrderSerializer(
        orders,
        many=True,
        context={"request": request}
    )

    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_orders(request):
    orders = CartOrder.objects.filter(user=request.user).order_by("-id")

    data = []
    for order in orders:
        data.append({
            "id": order.id,
            "invoice_no": order.invoice_no,
            "total": float(order.get_total),
            "product_status": order.product_status,
            "created_at": order.order_date.isoformat() if order.order_date else None,
        })

    return Response(data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def track_order(request, invoice_no):
    try:
        order = CartOrder.objects.get(
            invoice_no=invoice_no,
            user=request.user
        )

        serializer = TrackOrderSerializer(
            order,
            context={"request": request}
        )

        return Response(serializer.data)

    except CartOrder.DoesNotExist:
        return Response(
            {"error": "Order not found"},
            status=404
        )