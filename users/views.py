from rest_framework import status, serializers
from .serializers import RegisterSerializer
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .permissions import IsPatient, IsDoctor, IsAdmin
from rest_framework.permissions import IsAuthenticated


class LoginView(APIView):
    class LoginSerializer(serializers.Serializer):
        email = serializers.EmailField()
        password = serializers.CharField(write_only=True)

    def post(self, request):
        serializer = self.LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            user = authenticate(email=email, password=password)

            if user is None:
                return Response({
                    "success": False,
                    "message": "Invalid email or password"
                }, status=status.HTTP_200_OK)

            if not user.is_active:
                return Response({
                    "success": False,
                    "message": "Your account is inactive"
                }, status=status.HTTP_200_OK)

            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            return Response({
                'access': str(access_token),
                "message": "Login successful",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "role": user.role
                }
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "errors": serializer.errors
            }, status=status.HTTP_200_OK)

        self.perform_create(serializer)
        user_data = serializer.data
        return Response({
            "success": True,
            "message": "User registered successfully!",
            "user": user_data
        }, status=status.HTTP_201_CREATED)

class PatientDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsPatient]

    def get(self, request):
        return Response({
            "message": "Welcome to the Patient Dashboard",
            "user": {
                "email": request.user.email,
                "role": request.user.role
            }
        })
    
class DoctorDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsDoctor]

    def get(self, request):
        print(request)
        return Response({
            "message": "Welcome",
            "user": {
                "email": request.user.email,
                "role": request.user.role
            }
        })
      
class AdminDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        print(request)
        return Response({
            "message": "Welcome to the Admin Dashboard",
            "user": {
                "email": request.user.email,
                "role": request.user.role
            }
        })