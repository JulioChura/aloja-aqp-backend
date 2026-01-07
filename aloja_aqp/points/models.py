from django.db import models

class PointType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class PointOfInterest(models.Model):
    name = models.CharField(max_length=255)
    type = models.ForeignKey(PointType, on_delete=models.SET_NULL, null=True, related_name='points')
    address = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.DecimalField(max_digits=16, decimal_places=10, null=True, blank=True)
    longitude = models.DecimalField(max_digits=16, decimal_places=10, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.type})"
