__author__ = 'vutran'
import settings
def truongnha_global_variable(request):
    return {'SYSTEM_WARNING': settings.SYSTEM_WARNING,
            'VERSION': settings.VERSION,
            'DEBUG': settings.DEBUG,
            'STATIC_URL': settings.STATIC_URL,
    }
