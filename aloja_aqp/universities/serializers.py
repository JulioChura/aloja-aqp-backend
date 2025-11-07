from rest_framework import serializers
from .models import StudentUniversity,University,UniversityCampus

class StudentUniversitySerializer(serializers.ModelSerializer):
    campus_name = serializers.CharField(source='campus.name', read_only=True)
    university_id = serializers.IntegerField(source='campus.university.id', read_only=True)
    university_name = serializers.CharField(source='campus.university.name', read_only=True)

    class Meta:
        model = StudentUniversity
        fields = ['campus_name', 'university_id', 'university_name']


class StudentUniversityDetailSerializer(serializers.ModelSerializer):
    university_name = serializers.CharField(source='campus.university.name', read_only=True)
    university_abbreviation = serializers.CharField(source='campus.university.abbreviation', read_only=True)
    campus_name = serializers.CharField(source='campus.name', read_only=True)
    campus_address = serializers.CharField(source='campus.address', read_only=True)
    campus_latitude = serializers.FloatField(source='campus.latitude', read_only=True)
    campus_longitude = serializers.FloatField(source='campus.longitude', read_only=True)

    class Meta:
        model = StudentUniversity
        fields = [
            'university_name',
            'university_abbreviation',
            'campus_name',
            'campus_address',
            'campus_latitude',
            'campus_longitude',
        ]

class UniversitySerializer(serializers.ModelSerializer):
    campuses = serializers.SerializerMethodField()

    def get_campuses(self, obj):
        # Lazy import: UniversityCampusSimpleSerializer is defined later in this file
        return UniversityCampusSimpleSerializer(obj.campuses.all(), many=True).data

    class Meta:
        model = University
        fields = ['id', 'name', 'abbreviation', 'address', 'logo', 'campuses']
        read_only_fields = ['id']



class CampusSerializer(serializers.ModelSerializer):
    campus_id = serializers.IntegerField(source='campus.id')
    campus_name = serializers.CharField(source='campus.name')

    class Meta:
        model = StudentUniversity
        fields = ['campus_id', 'campus_name']
        
class UniversityCampusSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UniversityCampus
        fields = ['id', 'name', 'address', 'latitude', 'longitude']
        
class UniversityWithCampusesSerializer(serializers.Serializer):
    university_id = serializers.IntegerField()
    university_name = serializers.CharField()
    campuses = CampusSerializer(many=True)
