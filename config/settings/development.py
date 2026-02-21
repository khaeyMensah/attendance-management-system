from .base import *


# Automatic Database switching
DATABASE_URL = config('DATABASE_URL', default=None)
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(default=DATABASE_URL)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    

# # URL to redirect to after login
# LOGIN_REDIRECT_URL = 'home'

# # URL to redirect to after logout
# LOGOUT_REDIRECT_URL = 'home'

# # Site ID for Django's sites framework
# SITE_ID = 1

# # Authentication backends
# AUTHENTICATION_BACKENDS = (
#     'django.contrib.auth.backends.ModelBackend',
# )

# # Authentication method: username and email
# ACCOUNT_AUTHENTICATION_METHOD = 'username_email'

# # Require email for account creation
# ACCOUNT_EMAIL_REQUIRED = True

# # Email verification is mandatory
# ACCOUNT_EMAIL_VERIFICATION = 'mandatory'

# # Rate limits for account activities
# ACCOUNT_RATE_LIMITS = {
#     'login_failed': '5/300s',    # 5 failed login attempts per 5 minutes
#     'signup': '20/h',            # 20 signups per hour
#     'password_reset': '5/60m',   # 5 password resets per hour
# }

    
# Email settings
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='webmaster@localhost')