import re
from enum import Enum

_year_part = r'\d\d'
_program_part = r'[0-9D]'
_department_part = r'[0-9A-Z]{2}'
_sequential_part = r'[0-9]{3,4}'

IITB_ROLL_REGEX = re.compile(r'^' +
                             _year_part +
                             _program_part +
                             _department_part +
                             _sequential_part +
                             r'$',
                             re.IGNORECASE
                             )


class AlertTags(object):
    DANGER = 'alert alert-danger'
    INFO = 'alert alert-info'
    SUCCESS = 'alert alert-success'


class PostTypes(object):
    ALL = 0
    UG = 1
    PG = 2


POST_TYPE_CHOICES = [
    (PostTypes.ALL, 'ALL'),
    (PostTypes.UG, 'UG'),
    (PostTypes.PG, 'PG'),
]
