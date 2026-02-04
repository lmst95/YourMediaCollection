"""
Views for accounts app.
"""

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import User
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    UserUpdateSerializer,
    PasswordChangeSerializer,
)


@extend_schema_view(
    post=extend_schema(
        summary="Register new user",
        description="Create a new user account with username, email, and password.",
        tags=["Authentication"],
    )
)
class UserRegistrationView(generics.CreateAPIView):
    """
    User registration endpoint.
    POST /api/auth/register/
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            'user': UserSerializer(user).data,
            'message': 'User registered successfully. Please login to continue.'
        }, status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(
        summary="Get current user profile",
        description="Retrieve the authenticated user's profile information.",
        tags=["Users"],
    ),
    patch=extend_schema(
        summary="Update current user profile",
        description="Update the authenticated user's profile information.",
        tags=["Users"],
    ),
)
class CurrentUserView(generics.RetrieveUpdateAPIView):
    """
    Get or update current user profile.
    GET/PATCH /api/users/me/
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return UserUpdateSerializer
        return UserSerializer


@extend_schema_view(
    post=extend_schema(
        summary="Change password",
        description="Change the authenticated user's password.",
        tags=["Users"],
        request=PasswordChangeSerializer,
        responses={200: {'type': 'object', 'properties': {'message': {'type': 'string'}}}},
    )
)
class PasswordChangeView(APIView):
    """
    Change user password.
    POST /api/users/password/change/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Password changed successfully.'
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Get user by ID",
    description="Retrieve public profile information for a specific user.",
    tags=["Users"],
)
class UserDetailView(generics.RetrieveAPIView):
    """
    Get user profile by ID.
    GET /api/users/{id}/
    """
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
