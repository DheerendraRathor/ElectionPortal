from django.views.generic.base import TemplateView


class IndexView(TemplateView):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.user.is_authenticated():
            context['base_template'] = 'logged_in.html'
        else:
            context['base_template'] = 'root.html'

        return self.render_to_response(context)
