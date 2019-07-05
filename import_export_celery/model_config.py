from django.apps import apps
from import_export.resources import modelresource_factory

class ModelConfig():
    def __init__(self, app_label=None, model_name=None, resource=None):
        self.model = apps.get_model(app_label=app_label, model_name=model_name)
        if resource:
            self.resource = resource()
        else:
            self.resource = modelresource_factory(self.model)
