

class PostUtils(object):

    @staticmethod
    def get_post_read_only_fields(request, election):
        if not election or request.user.is_superuser:
            return []
        if election.is_finished or (election.is_active and not election.is_temporary_closed):
            return ['name', 'type', 'number']
        return []

    @staticmethod
    def has_delete_permission(request, election):
        if not election or request.user.is_superuser:
            return True
        if election.is_finished or (election.is_active and not election.is_temporary_closed):
            return False
        return True
