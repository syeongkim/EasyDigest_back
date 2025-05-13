from django.urls import path
from .views import signup, login_view, logout_view, check_username, get_profile, update_profile, change_password

urlpatterns = [
    path('signup/', signup),
    path('login/', login_view),
    path('logout/', logout_view),
    path('check-username/', check_username),
    path('me/', get_profile),
    path('me/update/', update_profile),
    path('change-password/', change_password)
]