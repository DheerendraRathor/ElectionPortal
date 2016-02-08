
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.views.generic.edit import FormView, View

from core.core import CAN_VOTE, LOGGED_IN_SESSION_KEY
from election.models import Voter

from .forms import VoterLoginForm


class VoterLoginView(FormView):
    form_class = VoterLoginForm
    template_name = 'account/login.html'
    success_url = 'election:index'

    def get(self, request, *args, **kwargs):
        next_ = request.GET.get('next', self.success_url)
        if next_ == '':
            next_ = self.success_url
        if request.user.is_authenticated():
            return redirect(next_)
        return render(request, self.template_name, {'form': self.form_class})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        next_ = request.POST.get('next', self.success_url)
        if next_ == '':
            next_ = self.success_url
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(username=username, password=password)
            if user and user.is_authenticated():
                if not user.user_profile.can_vote:
                    form.add_error(None, 'Only {0} are allowed to vote'.format(','.join(CAN_VOTE)))
                    return render(request, self.template_name, {'form': form})
                is_valid_voter = Voter.objects.all().filter(
                    roll_no__iexact=user.user_profile.roll_number,
                )
                if not is_valid_voter:
                    form.add_error(None, 'User is not a valid voter')
                request.session[LOGGED_IN_SESSION_KEY] = True
                login(request, user)
                return redirect(next_)
            else:
                form.add_error(None, "Incorrect username/password. Try again!")
        return render(request, self.template_name, {'form': form})


class VoterLogoutView(View):
    def post(self, request, *args, **kwargs):
        if request.user:
            logout(request)
        return redirect('account:login')
