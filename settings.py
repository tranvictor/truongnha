# -*- coding: utf-8 -*-
# Django settings for qlnt project

# open path for template folder
import os
import sys
DEBUG = True
if os.environ.pop('DJANGO_SETTINGS_TESTING', None):
    IS_TESTING = True
else:
    IS_TESTING = False

TEMPLATE_DEBUG = True

VERSION = '0.9.9'

ADMINS = (
    ('admin', 'qlnt@googlegroups.com'),
)

MANAGERS = ADMINS
if IS_TESTING:
    DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.sqlite3', 
           'NAME': os.path.join(os.path.dirname(__file__), 'sqlite3.db'), 
           'USER': '', # Not used with sqlite3.
           'PASSWORD': '', # Not used with sqlite3.
           'HOST': '', # Set to empty string for localhost. Not used with sqlite3.
           'PORT': '', # Set to empty string for default. Not used with sqlite3.
       },
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'freeschool',
            'USER': 'freeschool',
            'PASSWORD':'freeschool',
            'OPTIONS': { 'init_command': 'SET storage_engine=INNODB',},
        },
    }
STATIC_PORT = 8080
STOMP_PORT = 9000
INTERFACE = "localhost"


# uncomment following line to use auto multiple db router.
#DATABASE_ROUTERS = ['school.schoolrouter.SchoolRouter']
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Asia/Ho_Chi_Minh'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'vi' #'en-us'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = False
DATE_FORMAT = r'\N\gà\y d \t\há\n\g n \nă\m Y'
TIME_FORMAT = 'H:i:s'
DATETIME_FORMAT = r'H:i:s \N\gà\y d \t\há\n\g n \nă\m Y'
YEAR_MONTH_FORMAT = 'F Y'
MONTH_DAY_FORMAT = 'j F'
SHORT_DATE_FORMAT = 'd/m/Y'
SHORT_DATETIME_FORMAT = 'H:i:s d/m/Y'
# FIRST_DAY_OF_WEEK = 

# The *_INPUT_FORMATS strings use the Python strftime format syntax,
# see http://docs.python.org/library/datetime.html#strftime-strptime-behavior
# DATE_INPUT_FORMATS = 
# TIME_INPUT_FORMATS = 
# DATETIME_INPUT_FORMATS = 
DECIMAL_SEPARATOR = '.'
#THOUSAND_SEPARATOR = '.'


#DATE_FORMAT = ('D/M/YY', 'DD/MM/YYYY')
DATE_INPUT_FORMATS = ('%d/%m/%Y', '%d-%m-%Y')
#DECIMAL_SEPARATOR = '.'

SITE_ID = 1

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))


# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
#MEDIA_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), 'static/'))
MEDIA_ROOT = os.path.join(SITE_ROOT, 'static')


# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/static/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
#ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '$@fga3_%m!y@v+0_0h8kqo4n#4@(7fl7b++xz31nf0v)6861=3'
# Viettel sms gate parameters
SMS_WSDL_URL = 'http://viettelvas.vn:7777/sentmt/fromcp.asmx?WSDL'
WSDL_USERNAME = 'ws8x62'
WSDL_PASSWORD = 'password'
MT_USERNAME = 'username'
MT_PASSWORD = 'password'
# iNET sms gate parameters
INET_BRAND = '70077'
INET_AUTH = 'secret_key'
# Google Captcha Key, the private key must be secret and secured
CAPTCHA_PUBLIC_KEY = '6LdfIc4SAAAAACxRkXpRGhyK-mHYUsCQIHwF42fc'
CAPTCHA_PRIVATE_KEY = '6LdfIc4SAAAAAHHguVm0LwTPDOFNYzsMSomK718P'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'django.middleware.gzip.GZipMiddleware'
    #'htmlmin.middleware.HtmlMinifyMiddleware',
    #'slimmer.middleware.CompressHtmlMiddleware',

)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
#    'objectpermission.backends.ObjectPermissionBackend',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "truongnha_context_processor.truongnha_global_variable",
)

sys.path.append(os.getcwd())
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
#    'django.contrib.messages',
    'django.contrib.admin',
    'crumbs', #requires django-crumbs
    'app',
    'school',
    'sms',
    'api',
    'pagination',
    'djcelery',
    #'south', #for database migration/upgrade
#    'django_jenkins',
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # other finders..
    #'compressor.finders.CompressorFinder',
)

# Celery configuration
if not DEBUG:
    import djcelery
    djcelery.setup_loader()
    BROKER_URL = 'amqp://guest@localhost//'
    CELERY_IMPORTS = ("sms.utils", )

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# This variable define the url that system will redirect logged in user to
LOGIN_REDIRECT_URL = '/'
# These variable define demo accounts (username) for anonymous
# These accounts WON'T be automatically created on database, if these variables change,
# make sure that these username exist on database
# Set these variables to None to disable demo-login feature
DEMO_LOGIN_SCHOOL = 'truongnha_demo_account_school'
DEMO_LOGIN_TEACHER = 'truongnha_demo_account_teacher'
DEMO_LOGIN_UPPER = 'truongnha_demo_account_upper'

LOCALE_PATHS = (
    os.path.join(os.path.dirname(__file__), 'locale')
)

AUTH_PROFILE_MODULE = 'app.UserProfile'
LOGIN_FAILURE_LIMIT = 5

TEMP_FILE_LOCATION = os.path.join(SITE_ROOT, 'temp/uploaded')
SCHOOL_SETTING_FOLDER = os.path.join(SITE_ROOT, 'school/school_settings')
EXPORTED_FILE_LOCATION = os.path.join(SITE_ROOT, 'temp/exported')

#Email
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'support@truongnha.com'
EMAIL_HOST_PASSWORD = 'truongnhadotcom'
EMAIL_SUBJECT_PREFIX = '[www.truongnha.com]'
TEST_RUNNER = 'django_coverage.coverage_runner.CoverageRunner'

#Nha mang dc phep nhan tin
ALLOWED_TSP = ['VIETTEL']
#Cac nha mang
TSPS = ['VIETTEL', 'MOBI', 'VINA', 'EVN', 'VIETNAMMOBILE', 'BEELINE']
# test panel
if DEBUG:
    INTERNAL_IPS = ('127.0.0.1',)
    MIDDLEWARE_CLASSES += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )

    INSTALLED_APPS += (
        'debug_toolbar',
    )

    DEBUG_TOOLBAR_PANELS = (
        'debug_toolbar.panels.version.VersionDebugPanel',
        'debug_toolbar.panels.timer.TimerDebugPanel',
        'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
        'debug_toolbar.panels.headers.HeaderDebugPanel',
        #'debug_toolbar.panels.profiling.ProfilingDebugPanel',
        'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
        'debug_toolbar.panels.sql.SQLDebugPanel',
        'debug_toolbar.panels.template.TemplateDebugPanel',
        'debug_toolbar.panels.cache.CacheDebugPanel',
        'debug_toolbar.panels.signals.SignalDebugPanel',
        'debug_toolbar.panels.logger.LoggingPanel',
    )

    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
    }
