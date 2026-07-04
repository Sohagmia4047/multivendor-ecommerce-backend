import os
from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-%3el%2&etp$(qg&m!_4pae+yvrtv(f3pc&(qpwm!^hakwvbr8b'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'foodordering',
    'rest_framework',
    'corsheaders',
    'rest_framework_simplejwt', 
    'ckeditor',
    'ckeditor_uploader',
    'userauths',
    "core.apps.CoreConfig",
]

CORS_ALLOW_ALL_ORIGINS = True

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # This should be here
    ),
}

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'
BACKEND_BASE_URL = "http://127.0.0.1:8000"
FRONTEND_BASE_URL = "http://localhost:5173"


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTHENTICATION_BACKENDS = [
    'userauths.backends.EmailBackend',
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATICFILES_DIRS = [BASE_DIR / "static"]

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
CKEDITOR_UPLOAD_PATH = "uploads/"

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
}

JAZZMIN_SETTINGS = {
    "site_title": "Multivendor Admin",
    "site_header": "Multivendor",
    "site_brand": "Multivendor",
    "welcome_sign": "Welcome to Multivendor Admin",
    "copyright": "Sohag Mia",
    "custom_css": "css/admin.css",
    "show_sidebar": True,
    "navigation_expanded": True,

    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",

        "core.Category": "fas fa-th-large",
        "core.Product": "fas fa-shopping-cart",
        "core.ProductImages": "fas fa-image",
        "core.CartOrder": "fas fa-cart-plus",
        "core.CartOrderItems": "fas fa-box",
        "core.ProductReview": "fas fa-star",
        "core.Wishlist": "fas fa-heart",
        "core.Address": "fas fa-map-marker-alt",
        "core.Tags": "fas fa-tag",
        "core.Vendor": "fas fa-store",
    },

    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
    ],

    "show_ui_builder": False,
}

AUTH_USER_MODEL = 'userauths.User'

CKEDITOR_CONFIGS = {
    "default": {
        "skin": "moono",
        "toolbar": "all",
        "pasteFromWordRemoveFontStyles": True,
        "pasteFromWordRemoveStyles": True,
        "height": 300,
        "width": "100%",
        "toolbar_Custom": [
            ["Bold", "Italic", "Underline", "Strike"],
            ["NumberedList", "BulletedList"],
            ["Outdent", "Indent", "Blockquote"],
            ["JustifyLeft", "JustifyCenter", "JustifyRight", "JustifyBlock"],
            ["Link", "Unlink"],
            ["Image", "Table", "HorizontalRule"],
            ["Format", "Font", "FontSize"],
            ["TextColor", "BGColor"],
            ["RemoveFormat"],
            ["Source"],
            ["Maximize"],
        ],
        "extraPlugins": ",".join([
            "codesnippet",
            "widget",
            "dialog",
            "uploadimage",
            "image2",
            "autogrow",
        ]),
        "removePlugins": "stylesheetparser",
        "autoGrow_minHeight": 300,
        "autoGrow_maxHeight": 800,
        "autoGrow_bottomSpace": 50,
    }
}

SSLCOMMERZ_STORE_ID = "sohag69c39bb96510b"
SSLCOMMERZ_STORE_PASSWORD = "sohag69c39bb96510b@ssl"
SSLCOMMERZ_IS_SANDBOX = True