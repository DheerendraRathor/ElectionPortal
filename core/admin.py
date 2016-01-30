
class RemoveDeleteSelectedMixin(object):

    def get_actions(self, request):
            actions = super().get_actions(request)
            if not request.user.is_superuser:
                if 'delete_selected' in actions:
                    del actions['delete_selected']
            return actions
