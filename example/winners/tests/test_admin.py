from django.contrib.messages.storage.fallback import FallbackStorage

from django_admin_smoke_tests import tests


class AdminSmokeTest(tests.AdminSiteSmokeTest):
    exclude_apps = []
    fixtures = []

    def post_request(self, post_data={}, params=None):  # noqa
        request = self.factory.post("/", data=post_data)
        request.user = self.superuser
        request._dont_enforce_csrf_checks = True
        request.session = "session"
        request._messages = FallbackStorage(request)
        return request
