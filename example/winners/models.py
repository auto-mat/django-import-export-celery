from django.db import models

from import_export.resources import ModelResource
from import_export.fields import Field


class Winner(models.Model):
    name = models.CharField(
        max_length=80,
        null=False,
        blank=False,
        default="",
    )

    @classmethod
    def export_resource_classes(cls):
        return {
            "winners": ("Winners resource", WinnersResource),
            "winners_all_caps": (
                "Winners with all caps column resource",
                WinnersWithAllCapsResource,
            ),
        }


class WinnersResource(ModelResource):
    class Meta:
        model = Winner

    def get_export_queryset(self):
        """To customise the queryset of the model resource with annotation override"""
        return self.Meta.model.objects.all()


class WinnersWithAllCapsResource(WinnersResource):
    name_all_caps = Field()

    def dehydrate_name_all_caps(self, winner):
        return winner.name.upper()
