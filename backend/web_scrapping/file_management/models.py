from django.db import models

from file_management.constants import TYPE_CHOICES


# Create your models here.
class LookupKeywords(models.Model):
    key = models.CharField(max_length=255, unique=True, db_column="key")
    value = models.TextField(db_column="value")

    class Meta:
        db_table = "lookup_keywords"


class Urls(models.Model):
    raw_filename = models.CharField(max_length=100, db_column="raw_filename")
    url = models.CharField(max_length=255, db_column="url")
    type = models.CharField(max_length=50, db_column="type", choices=TYPE_CHOICES)
    folder_name = models.CharField(max_length=255, db_column="folder_name")

    class Meta:
        db_table = "urls"
