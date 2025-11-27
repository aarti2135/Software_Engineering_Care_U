from django.urls import path
from . import views

urlpatterns = [
    path("avatar/select/", views.avatar_select, name="avatar_select"),
]