from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage

from django_admin_smoke_tests import tests

from import_export_celery.models import ExportJob, ImportJob


class AdminSmokeTest(tests.AdminSiteSmokeTest):
    exclude_apps = []
    fixtures = []

    def post_request(self, post_data={}, params=None):
        request = self.factory.post("/", data=post_data)
        request.user = self.superuser
        request._dont_enforce_csrf_checks = True
        request.session = "session"
        request._messages = FallbackStorage(request)
        return request
