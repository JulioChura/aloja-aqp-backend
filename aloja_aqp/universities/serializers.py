from rest_framework import serializers
from .models import StudentUniversity

class StudentUniversitySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='university.id')  # usamos el id de la universidad

    class Meta:
        model = StudentUniversity
        fields = ['id']
