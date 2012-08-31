__author__ = 'vutran'
import settings
def truongnha_global_variable(request):
    return {'VERSION': settings.VERSION}