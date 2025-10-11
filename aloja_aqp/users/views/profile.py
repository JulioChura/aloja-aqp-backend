from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..serializers import UserUpdateSerializer, UserResponseSerializer
from universities.models import StudentUniversity
from universities.serializers import StudentUniversitySerializer

class UpdateUserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        # Actualizar datos básicos del usuario
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Procesar sedes enviadas
        campuses = request.data.get('campuses', [])
        if campuses and hasattr(request.user, 'student_profile'):
            student_profile = request.user.student_profile
            for campus_id in campuses:
                StudentUniversity.objects.get_or_create(
                    student=student_profile,
                    campus_id=campus_id
                )


        user_data = UserResponseSerializer(request.user).data

        return Response(user_data, status=status.HTTP_200_OK)
