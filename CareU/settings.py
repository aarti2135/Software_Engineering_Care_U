from pathlib import Path

# --------------------------------------------------------------------------------------
# Core
# --------------------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ⚠️ Dev-only key (don’t use in production)
SECRET_KEY = 'django-insecure-cn%@pbfr9i7)3*y(0*nd5hxb%f9pevs57xz=1f-yvwy#w7jt73'

DEBUG = True
ALLOWED_HOSTS = []

# --------------------------------------------------------------------------------------
# Applications
# --------------------------------------------------------------------------------------
INSTALLED_APPS = [
    # Django built-ins
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
<<<<<<< HEAD
=======
    'usermanagement',
    'healthdata',
>>>>>>> upstream/main

    # Your apps
    #'usermanagement',
    'usermanagement.apps.UsermanagementConfig',
    'healthdata',
    'User_Login',

    # Third-party
    'rest_framework',
]

# --------------------------------------------------------------------------------------
# Middleware
# --------------------------------------------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --------------------------------------------------------------------------------------
# URLs / WSGI
# --------------------------------------------------------------------------------------
ROOT_URLCONF = 'CareU.urls'
WSGI_APPLICATION = 'CareU.wsgi.application'

# --------------------------------------------------------------------------------------
# Templates
# --------------------------------------------------------------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # project-level templates folder
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

# --------------------------------------------------------------------------------------
# Database (SQLite for dev)
# --------------------------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --------------------------------------------------------------------------------------
# Password validation
# --------------------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --------------------------------------------------------------------------------------
# i18n / tz
# --------------------------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --------------------------------------------------------------------------------------
# Static files
# --------------------------------------------------------------------------------------
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# --------------------------------------------------------------------------------------
# Defaults
# --------------------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --------------------------------------------------------------------------------------
# Django REST Framework
# --------------------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

# --------------------------------------------------------------------------------------
# Authentication redirects
# (After login → dashboard | After logout → login)
# --------------------------------------------------------------------------------------
LOGIN_URL = '/accounts/login/'                 # <- corrected
#LOGIN_REDIRECT_URL = '/api/dashboard/nutrition/'
LOGIN_REDIRECT_URL = '/accounts/login/'
LOGOUT_REDIRECT_URL = '/accounts/login/'
