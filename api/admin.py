from django.apps import apps
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered


models_dict = apps.all_models['api']
for model in models_dict.values():
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass
