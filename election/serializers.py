from io import BytesIO

from rest_framework import serializers
from rest_framework.parsers import FormParser

from core.core import VOTE_TYPE_DICT


class AddVoteSerializer(serializers.Serializer):
    votes = serializers.JSONField(binary=True)
    key = serializers.CharField(default=None)

    def to_internal_value(self, form_data):
        stream = BytesIO(form_data)
        data = FormParser().parse(stream)
        return super().to_internal_value(data)

    def validate_votes(self, value: dict):
        votes = {}
        for key, value in value.items():
            try:
                int_key = int(key)
                int_val = int(value)
                assert int_val in VOTE_TYPE_DICT.keys()

                votes[int_key] = int_val
            except (ValueError, AssertionError):
                raise serializers.ValidationError('Dict key/value is not integer')

        return votes
