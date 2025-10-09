import os
from django.contrib.auth.models import Group
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from google.oauth2 import id_token
from google.auth.transport import requests
import cloudinary.uploader
from ..models import User, UserStatus, StudentProfile
from ..serializers import UserResponseSerializer
from ..utils.tokens import generate_tokens_for_user

GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')


@method_decorator(csrf_exempt, name='dispatch')
class GoogleLoginAPIView(APIView):
    def post(self, request):
        token = request.data.get("id_token")
        if not token:
            return Response({'error': 'ID Token no proporcionado'}, status=400)

        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
            email = idinfo['email']
            first_name = idinfo.get('given_name', '')
            last_name = idinfo.get('family_name', '')
            picture_url = idinfo.get('picture', None)

            user, created = User.objects.get_or_create(email=email)
            if created:
                user.first_name = first_name
                user.last_name = last_name
                user.google_id = idinfo['sub']
                user.set_unusable_password()
                if picture_url:
                    try:
                        upload_result = cloudinary.uploader.upload(picture_url)
                        user.avatar = upload_result['public_id']
                    except Exception as e:
                        print("Error subiendo avatar desde Google:", e)
                user.save()

                student_group, _ = Group.objects.get_or_create(name='student')
                user.groups.add(student_group)

                active_status, _ = UserStatus.objects.get_or_create(name='active')
                StudentProfile.objects.create(user=user, phone_number='', status=active_status)

            user_data = UserResponseSerializer(user).data
            tokens = generate_tokens_for_user(user)
            return Response({"user": user_data, **tokens}, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({'error': 'Token inválido', 'details': str(e)}, status=400)
        except Exception as e:
            print("ERROR GoogleLoginAPIView:", e)
            return Response({'error': str(e)}, status=500)
