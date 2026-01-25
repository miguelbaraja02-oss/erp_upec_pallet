from django.shortcuts import redirect

EXCLUDED_PATHS = [
    "/accounts/",
    "/welcome/",
    "/companies/",
    "/profile/",
    "/logout/",
    "/static/",
    "/media/",
]

class CompanyRequiredMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            return self.get_response(request)

        path = request.path

        for excluded in EXCLUDED_PATHS:
            if path.startswith(excluded):
                return self.get_response(request)

        if not request.session.get("company_id"):
            return redirect("core:welcome")

        return self.get_response(request)
