class ExceptionUserInfoMiddleware(object):
    def process_exception(self, request, exception):
        try:
            if request.user.is_authenticated():
                request.META['USERNAME'] = str(request.user.username)
                request.META['USERID'] = str(request.user.id)
                request.META['AJAX'] = str(request.is_ajax())
        except:
            pass
