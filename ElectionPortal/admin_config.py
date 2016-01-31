from django.contrib.admin import site


def config():
    site.site_header = 'IITB Election Portal Admin'
    site.site_title = 'IITB Election'
    site.index_title = 'Admin portal'
