
class EnsureLoginStatusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Ensure 'login_status' is in the session
        if request.user.is_authenticated:
            request.session['login_status'] = True
        else:
            request.session['login_status'] = False
        
        return self.get_response(request)