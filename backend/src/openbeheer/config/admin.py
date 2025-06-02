from django.contrib import admin

from solo.admin import SingletonModelAdmin

from .models import APIConfig


@admin.register(APIConfig)
class APIConfigAdmin(SingletonModelAdmin):
    pass
