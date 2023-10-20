from file_management.models import Urls, LookupKeywords
from rest_framework import serializers


class UrlsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Urls
        fields = ["id", "raw_filename", "url", "type", "folder_name"]


class LookupKeywordsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = LookupKeywords
        fields = ["id", "key", "value"]


class UrlsJsonSerializer(serializers.ModelSerializer):

    class Meta:
        model = Urls
        fields = ["raw_filename", "url", "type", "folder_name"]


class LookupKeywordsJsonSerializer(serializers.ModelSerializer):

    class Meta:
        model = LookupKeywords
        fields = ["key", "value"]

    def to_representation(self, instance):
        organized_data = dict()
        values = instance.value.split(',')
        organized_data[instance.key] = values
        return organized_data


class WebScrapingSerializer(serializers.Serializer):
    input_file = serializers.FileField()
    lookup_file = serializers.FileField()