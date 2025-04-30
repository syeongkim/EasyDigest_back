from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

User = get_user_model()

# Create your views here.
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
    return Response({'message': 'Signup successful and logged in.'})

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
    return Response({
        'message': 'Login successful',
        'nickname': user.nickname  # 👈 여기를 추가
    })


@csrf_exempt
@api_view(['POST'])
def logout_view(request):
    logout(request)
    return Response({'message': 'Logged out successfully'})

@api_view(['GET'])
def check_username(request):
    username = request.GET.get('username', '')
    exists = User.objects.filter(username=username).exists()
    return Response({'exists': exists})