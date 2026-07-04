from django.urls import path
from . import views
from .views import product_list, category_list, product_list_page, category_products_list, vendor_list, vendor_detail, product_detail, products_by_tag, create_review, tag_list, add_to_cart, get_cart, update_cart, delete_cart_item, clear_cart, track_order, user_orders

urlpatterns = [
    path('products/', product_list, name='product_list'),
    path("products/<int:id>/", product_detail, name="product-detail"),
    path("products/<int:pid>/review/",create_review,name="create-review"),
    path('product-page/', product_list_page, name='product_list_page'),
    path("categories/", category_list, name="category-list"),
    path("categories/<str:cid>/", category_products_list, name="category-products"),
    path("vendors/", vendor_list, name="vendor-list"),
    path("vendors/<str:vid>/", vendor_detail,name="vendor-detail"),
    path("address/default/", views.default_address, name="default-address"),
    path("address/save/", views.save_address, name="save-address"),
    path("tags/", tag_list, name="tag-list"),
    path("tags/<slug:slug>/", products_by_tag, name="products-by-tag"),
    path("cart/", get_cart, name="get-cart"),
    path("cart/add/", add_to_cart, name="add-to-cart"),
    path("cart/update/<int:id>/", update_cart, name="update-cart"),
    path("cart/delete/<int:id>/", delete_cart_item, name="delete-cart-item"),
    path("cart/clear/", clear_cart, name="clear-cart"),
    path("checkout/",views.CheckoutView.as_view(),name="checkout"),
    path('payments/sslcommerz/success/', views.SSLCommerzSuccessView.as_view(), name="ssl-success"),
    path("payments/sslcommerz/fail/", views.SSLCommerzFailView.as_view(), name="ssl-fail"),
    path("payments/sslcommerz/cancel/", views.SSLCommerzCancelView.as_view(),name="ssl-cancel"),
    path("payments/sslcommerz/ipn/", views.SSLCommerzIPNView.as_view(), name="ssl-ipn"),
    path("invoice/<str:invoice_no>/",views.invoice_details,name="invoice-details"),
    path("dashboard/orders/", views.my_orders, name="dashboard-orders"),
    path("dashboard/orders/track-all/", user_orders, name="track-all-orders"),
    path("dashboard/orders/track/<str:invoice_no>/", track_order, name="track-order"),
]