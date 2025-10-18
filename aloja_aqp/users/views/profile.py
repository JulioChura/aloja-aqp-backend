from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..serializers import UserUpdateSerializer, UserResponseSerializer, StudentProfileSerializer
from universities.models import StudentUniversity, UniversityCampus
from universities.serializers import StudentUniversitySerializer


class UpdateUserInfoView(APIView): 
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user
        data = request.data.copy()

        # Campos del perfil de estudiante
        student_fields = ['phone_number', 'gender', 'age', 'career', 'bio']

        # Extraer datos del perfil
        student_data = {f: data.pop(f) for f in student_fields if f in data}

        # Actualizar datos del usuario principal
        serializer = UserUpdateSerializer(user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Actualizar datos del perfil del estudiante
        if student_data and hasattr(user, 'student_profile'):
            student_serializer = StudentProfileSerializer(user.student_profile, data=student_data, partial=True)
            student_serializer.is_valid(raise_exception=True)
            student_serializer.save()

        # Procesar campus enviados (puede venir como "campus" o "campuses")
        campuses = request.data.get('campuses') or request.data.get('campus')
        if campuses and hasattr(user, 'student_profile'):
            # Normalizar a lista
            if isinstance(campuses, int) or isinstance(campuses, str):
                campuses = [int(campuses)]

            for campus_id in campuses:
                if not UniversityCampus.objects.filter(id=campus_id).exists():
                    return Response(
                        {"campus": [f"Invalid pk '{campus_id}' - object does not exist."]},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Crear o mantener relación StudentUniversity
                StudentUniversity.objects.get_or_create(
                    student=user.student_profile,
                    campus_id=campus_id
                )

        # Respuesta final con datos completos
        user.refresh_from_db()
        user_data = UserResponseSerializer(user).data
        return Response(user_data, status=status.HTTP_200_OK)