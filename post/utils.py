

class PostUtils(object):

    @staticmethod
    def get_post_read_only_fields(request, election):
        if not election or request.user.is_superuser:
            return []
        if election.creator != request.user or election.has_activated:
            return ['name', 'type', 'number']
        return []

    @staticmethod
    def has_delete_permission(request, election):
        if not election or request.user.is_superuser:
            return True
        if election.creator != request.user or election.has_activated:
            return False
        return True
