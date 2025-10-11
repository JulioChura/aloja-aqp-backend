from django.db import models

class University(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    abbreviation = models.CharField(max_length=50, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.abbreviation


class UniversityCampus(models.Model):
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name="campuses")
    name = models.CharField(max_length=100)  
    address = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ("university", "name")

    def __str__(self):
        return f"{self.university.name} - {self.name}"


class StudentUniversity(models.Model):
    student = models.ForeignKey('users.StudentProfile', on_delete=models.CASCADE)
    campus = models.ForeignKey(UniversityCampus, on_delete=models.CASCADE)
    #start_date = models.DateField(null=True, blank=True)
    #end_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ("student", "campus")

    def __str__(self):
        return f"{self.student.user.email} - {self.campus.name}"