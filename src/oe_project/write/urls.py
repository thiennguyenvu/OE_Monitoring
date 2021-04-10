from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('planning', views.planning, name='planning'),
    path('history', views.history, name='history'),
    path('animation', views.animation, name='animation'),
]
