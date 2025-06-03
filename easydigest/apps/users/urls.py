from django.urls import path
from .views import *

urlpatterns = [
    path('signup/', signup),
    path('login/', login_view),
    path('logout/', logout_view),
    path('check-username/', check_username),
    path('check-email/', check_email),
    path('me/', get_profile),
    path('me/update/', update_profile),
    path('change-password/', change_password),
    path('auth/google/', google_login),
    path('me/interest/', set_interest)
]