from django.db import models

class University(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    abbreviation = models.CharField(max_length=50, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.abbreviation


class StudentUniversity(models.Model):
    student = models.ForeignKey('users.StudentProfile', on_delete=models.CASCADE)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    #start_date = models.DateField(null=True, blank=True)
    #end_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ("student", "university")

    def __str__(self):
        return f"{self.student.user.email} - {self.university.abbreviation}"
    
