import json
import subprocess

from django.db import transaction
from django.http import HttpResponse, JsonResponse
from file_management.models import Urls, LookupKeywords
from file_management.serializers import (
    UrlsSerializer,
    LookupKeywordsSerializer,
    UrlsJsonSerializer,
    LookupKeywordsJsonSerializer,
    WebScrapingSerializer
)
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response



# Create your views here.
class UrlsViewSet(viewsets.ModelViewSet):
    queryset = Urls.objects.all()
    serializer_class = UrlsSerializer

    def create(self, request, *args, **kwargs):
        try:
            bulk_list = list()
            with transaction.atomic():
                items = request.data
                for item in items:
                    bulk_list.append(
                        Urls(
                            raw_filename=item.get('raw_filename'),
                            url=item.get('url'),
                            type=item.get('type'),
                            folder_name=item.get('folder_name')
                        )
                    )
            Urls.objects.bulk_create(bulk_list)
            return Response("Data created Successfully", status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'])
    def get_json(self, request):
        urls = self.queryset
        data = UrlsJsonSerializer(urls, many=True).data

        # Create a JSON file
        json_data = json.dumps(data, indent=4)

        # Create an HttpResponse with the JSON content
        response = HttpResponse(json_data, content_type='application/json')
        with open('input.json', 'w') as file:
            file.write(json_data)
        # Set the Content-Disposition header to suggest a filename for the browser
        response['Content-Disposition'] = 'attachment; filename="input.json"'

        return response


class LookupKeywordViewSet(viewsets.ModelViewSet):
    queryset = LookupKeywords.objects.all()
    serializer_class = LookupKeywordsSerializer

    def create(self, request, *args, **kwargs):
        try:
            bulk_list = list()
            with transaction.atomic():
                items = request.data
                print("request data :: ",request.data)
                for item in items:
                    print(item)
                    serializer = self.serializer_class(data=item)
                    if serializer.is_valid(raise_exception=True):
                        bulk_list.append(
                            LookupKeywords(
                                key=item.get('key'),
                                value=item.get('value'),
                            )
                        )
            LookupKeywords.objects.bulk_create(bulk_list)
            return Response("Data created Successfully", status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'])
    def get_json(self, request):
        lookup_keywords = self.queryset
        data = LookupKeywordsJsonSerializer(lookup_keywords, many=True).data

        # Create a JSON file
        json_data = json.dumps(data, indent=4)
        # Create an HttpResponse with the JSON content
        response = HttpResponse(json_data, content_type='application/json')
        with open('lookUpTable.json', 'w') as file:
            file.write(json_data)
        # Set the Content-Disposition header to suggest a filename for the browser
        response['Content-Disposition'] = 'attachment; filename="lookUpTable.json"'

        return response


class WebScrappingViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = None
    serializer_class = None


    def get_serializer_class(self):
        return  None

    def create(self, request, *args, **kwargs):
        try:
            from web_scrapping_program import MasterProgram

            print(" \n =====  START ==========\n")
            # TODO : this should wait here for response

            # lookup_keywords = LookupKeywords.objects.all()
            # lookup_keywords_data = LookupKeywordsJsonSerializer(lookup_keywords, many=True).data
            # lookup_table_data = json.dumps(lookup_keywords_data, indent=4)
            # BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            # lookup_json_path = os.path.join(BASE_DIR, 'web_scrapping_program/input.json')
            # with open('lookup_json_path', 'w') as file:
            #     file.write(lookup_table_data)
            # inputs = Urls.objects.all()
            # input_data = UrlsJsonSerializer(inputs, many=True).data
            # input_json_data = json.dumps(input_data, indent=4)
            # BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            # input_json_path = os.path.join(BASE_DIR, 'web_scrapping_program/input.json')
            # with open('input_json_path', 'w') as file:
            #     file.write(input_json_data)

            folder_name = MasterProgram.main()
            print(" \n =====  END ==========\n")
            output_filename = f"data_map_{folder_name}.csv"

            if output_filename:
                AZURE_STORAGE_BASE_URL = 'https://webscrapinginvesco.blob.core.windows.net/raw'
                FOLDER = 'output'

                file_link = "{}/{}/{}".format(AZURE_STORAGE_BASE_URL,FOLDER,output_filename)
                response_data = {
                    'status': 'success',
                    'file_link': file_link
                }
            else:
                response_data = {
                    'status': 'failed',
                }

        except Exception as e:
            response_data = {
                'status': 'error',
                'message': str(e)
            }

        return JsonResponse(response_data)
