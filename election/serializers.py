from io import BytesIO

from rest_framework import serializers
from rest_framework.parsers import FormParser


class AddVoteSerializer(serializers.Serializer):
    election = serializers.IntegerField()
    votes = serializers.JSONField(binary=True)
    key = serializers.IntegerField(default=None)

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
                assert int_val in [1, -1, 0]

                votes[int_key] = int_val
            except (ValueError, AssertionError):
                raise serializers.ValidationError('Dict key/value is not integer')

        return votes