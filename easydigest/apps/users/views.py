from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer, InterestSerializer
import uuid
import requests


User = get_user_model()

# Create your views here.

# 회원가입
@csrf_exempt
@api_view(['POST'])
def signup(request):
    username = request.data.get('username')
    password = request.data.get('password')
    nickname = request.data.get('nickname')
    email = request.data.get('email')
    interest = request.data.get('interest')

    if not username:
        return Response(
            {'message': 'Username is required.'},
            status = status.HTTP_400_BAD_REQUEST
        )
    
    if not password:
        return Response(
            {'message': 'Password is required.'},
            status = status.HTTP_400_BAD_REQUEST
        )
    
    if not nickname:
        return Response(
            {'message': 'Nickname is required.'},
            status = status.HTTP_400_BAD_REQUEST
        )
    
    if not email:
        return Response(
            {'message': 'Email is required.'},
            status = status.HTTP_400_BAD_REQUEST
        )
    
    if User.objects.filter(username=username).exists():
        return Response(
            {'message': 'Username already exists.'},
            status = status.HTTP_400_BAD_REQUEST
        )
    
    if User.objects.filter(email=email).exists():
        return Response(
            {'message': 'Email already exists.'},
            status = status.HTTP_400_BAD_REQUEST
        )

    user = User.objects.create_user(username=username, password=password, nickname=nickname, email=email, interest=interest)
    login(request, user)
    refresh = RefreshToken.for_user(user)
    return Response({
        'message': 'Signup successful and logged in.',
        'nickname': user.nickname,
        'access': str(refresh.access_token),
        'refresh': str(refresh)
    })

# 로그인
@csrf_exempt
@api_view(['POST'])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({'message': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)

    if not user.check_password(password):
        return Response({'message': 'Incorrect password'}, status=status.HTTP_400_BAD_REQUEST)

    login(request, user)
    refresh = RefreshToken.for_user(user)

    return Response({
        'message': 'Login successful',
        'nickname': user.nickname,
        'access': str(refresh.access_token),
        'refresh': str(refresh)
    })

# 로그아웃
@csrf_exempt
@api_view(['POST'])
def logout_view(request):
    logout(request)
    return Response({'message': 'Logged out successfully'})

# 이름 중복 체크
@api_view(['GET'])
def check_username(request):
    username = request.GET.get('username', '')
    exists = User.objects.filter(username=username).exists()
    return Response({'exists': exists})

# 회원정보 조회
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

# 회원정보 수정 (닉네임, 관심분야, 이메일만 변경 가능)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 비밀번호 변경
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    current_password = request.data.get("current_password")
    new_password = request.data.get("new_password")

    if not current_password:
        return Response(
            {"message": "current password is required"},
            status = status.HTTP_400_BAD_REQUEST
        )
    
    if not new_password:
        return Response(
            {"message": "new password is required"},
            status = status.HTTP_400_BAD_REQUEST
        )
    
    if not user.check_password(current_password):
        return Response(
            {"message": "현재 비밀번호가 일치하지 않습니다."},
            status = status.HTTP_400_BAD_REQUEST
        )
    
    user.set_password(new_password)
    user.save()
    return Response(
        {"message": "비밀번호가 성공적으로 변경되었습니다."},
        status = status.HTTP_200_OK
    )

# 구글 소셜 로그인
@api_view(['POST'])
def google_login(request):
    token = request.data.get('token')
    if not token:
        return Response({'message': "No token provided"}, status = status.HTTP_400_BAD_REQUEST)
    
    resp = requests.get(f'https://oauth2.googleapis.com/tokeninfo?id_token={token}')
    if resp.status_code != 200:
        return Response({'message': 'Invalid token'}, status = status.HTTP_400_BAD_REQUEST)
    
    user_info = resp.json()

    email = user_info.get('email')
    name = user_info.get('name')

    User = get_user_model()

    user, created = User.objects.get_or_create(
        email = email,
        defaults= {
            'username': f"{email.split('@')[0]}",
            'nickname': name,
            'password': make_password(None),
            'is_social': True,
        }
    )

    refresh = RefreshToken.for_user(user)

    return Response({
        'message': 'Login successful with google',
        'username': user.username,
        'nickname': user.nickname,
        'email': user.email,
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    })

# 구글 소셜 로그인 후 관심사 필드 설정
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def set_interest(request):
    user = request.user
    serializer = InterestSerializer(user, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Save interest successfully',
            'interest': user.interest
        })
    
    return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)