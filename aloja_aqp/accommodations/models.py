from django.db import models
from users.models import OwnerProfile, StudentProfile
from universities.models import University
from points.models import PointOfInterest
from cloudinary.models import CloudinaryField
from universities.models import UniversityCampus


class AccommodationStatus(models.Model):
    name = models.CharField(max_length=50, unique=True) 

    def __str__(self):
        return self.name

class AccommodationType(models.Model):
    name = models.CharField(max_length=50, unique=True)  # Departamento, Habitación
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Accommodation(models.Model):
    owner = models.ForeignKey(OwnerProfile, on_delete=models.CASCADE, related_name="accommodations")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    accommodation_type = models.ForeignKey(AccommodationType, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2)
    coexistence_rules = models.TextField(blank=True)
    publication_date = models.DateTimeField(auto_now_add=True)
    status = models.ForeignKey(AccommodationStatus, on_delete=models.SET_NULL, null=True, default=None)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class AccommodationPhoto(models.Model):
    accommodation = models.ForeignKey(Accommodation, on_delete=models.CASCADE, related_name="photos")
    image = CloudinaryField('image')
    order_num = models.IntegerField(default=0)
    is_main = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo for {self.accommodation.title}"

class PredefinedService(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon_class = models.CharField(max_length=100, blank=True, null=True) 

    def __str__(self):
        return self.name


class AccommodationService(models.Model):
    accommodation = models.ForeignKey(Accommodation, on_delete=models.CASCADE, related_name="services")
    service = models.ForeignKey(PredefinedService, on_delete=models.CASCADE)
    detail = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ("accommodation", "service")

    def __str__(self):
        return f"{self.service.name} in {self.accommodation.title}"

class UniversityDistance(models.Model):
    accommodation = models.ForeignKey(Accommodation, on_delete=models.CASCADE)
    campus = models.ForeignKey(UniversityCampus, on_delete=models.CASCADE, related_name='accommodation_distances')
    distance_km = models.DecimalField(max_digits=6, decimal_places=2)
    walk_time_minutes = models.IntegerField(null=True, blank=True)
    bus_time_minutes = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ("accommodation", "campus")

    def __str__(self):
        return f"{self.accommodation.title} - {self.campus}"

class AccommodationNearbyPlace(models.Model):
    accommodation = models.ForeignKey(
        'Accommodation', on_delete=models.CASCADE, related_name='nearby_places'
    )
    point_of_interest = models.ForeignKey(
        PointOfInterest, on_delete=models.CASCADE, related_name='near_accommodations'
    )
    distance_km = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    walking_time_min = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('accommodation', 'point_of_interest')

    def __str__(self):
        return f"{self.accommodation.title} - {self.point_of_interest.name}"



class Review(models.Model):
    accommodation = models.ForeignKey(Accommodation, on_delete=models.CASCADE, related_name="reviews")
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    rating = models.SmallIntegerField()
    comment = models.TextField(blank=True)
    review_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="visible")

    class Meta:
        unique_together = ("accommodation", "student")

    def __str__(self):
        return f"Review by {self.student.user.email}"

class Favorite(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    accommodation = models.ForeignKey(Accommodation, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "accommodation")

    def __str__(self):
        return f"{self.student.user.email} - {self.accommodation.title}"
