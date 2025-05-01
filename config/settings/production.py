from .base import *


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
    }
}

# Switch to PostgreSQL if DATABASE_URL is set
# DATABASE_URL = config('DATABASE_URL', default=None)
# if DATABASE_URL:
#     DATABASES['default'] = dj_database_url.config(default=DATABASE_URL)

# Static files (CSS, JavaScript, Images)
# # Static files storage settings
# if not DEBUG:
#     STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
