import re

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

POST_TYPE_DICT = {
    PostTypes.ALL: 'ALL',
    PostTypes.UG: 'UG',
    PostTypes.PG: 'PG',
}

POST_TYPE_CHOICES = [(key, value) for key, value in POST_TYPE_DICT.items()]

CAN_VOTE = ['UG', 'PG', 'DD']

UG_TYPE = ['UG', 'DD']

PG_TYPE = ['PG']


class VoteTypes(object):
    YES = 1
    NO = -1
    NEUTRAL = 0

VOTE_TYPE_DICT = {
    VoteTypes.YES: 'Yes',
    VoteTypes.NO: 'No',
    VoteTypes.NEUTRAL: 'Neutral',
}

VOTE_TYPE_CHOICES = [(key, value) for key, value in VOTE_TYPE_DICT.items()]
