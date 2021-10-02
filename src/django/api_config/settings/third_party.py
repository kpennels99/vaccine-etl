"""Third party application configurations."""
from datetime import timedelta

from .environment import env

# DRF
REST_FRAMEWORK = {

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        # 'apps.core.okta_openid.middleware.OktaAuthentication',
        'rest_framework.authentication.SessionAuthentication'
    ],

    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],

    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework_filters.backends.RestFrameworkFilterBackend',
        'rest_framework.filters.OrderingFilter'
    ],

    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',

    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

#  CORS headers
CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_HEADERS = (
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'cache-control',
)

# Okta

OKTA_AUTH = {
    'ORG_URL': env.str('OKTA_ORG_URL', 'https://dev-46582267.okta.com/'),
    'ISSUER': env.str('OKTA_ISSUER', 'https://dev-46582267.okta.com/oauth2/default'),
    'CLIENT_ID': env.str('OKTA_CLIENT_ID', None),
    'CLIENT_SECRET': env.str('OKTA_CLIENT_SECRET', None),
    'REDIRECT_URI': env.str('OKTA_REDIRECT_URI',
                            'http://127.0.0.1:8000/accounts/oauth2/callback'),
    'PUBLIC_URLS': (r'/favicon.ico', r'/okta_login'),
    'PUBLIC_NAMED_URLS': ('okta_login', ''),
    'CLAIMS_HANDLER': 'insights.okta_authorization.claim_handler'
}


# Celery
CELERY_RESULT_BACKEND = 'django-db'
DELAY_CELERY_TASKS = env.bool('DELAY_CELERY_TASKS', True)

# Simple JWT

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
}
