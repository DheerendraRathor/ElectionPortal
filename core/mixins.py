from django.contrib.auth.views import redirect_to_login


class VoterRequiredMixin(object):
    """
    CBV mixin which verifies that the current user is authenticated.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.voter:
            return redirect_to_login(self.request.get_full_path(), self.get_login_url(), self.get_redirect_field_name())
        return super(VoterRequiredMixin, self).dispatch(request, *args, **kwargs)