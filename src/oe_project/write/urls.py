from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('planning', views.planning, name='planning'),
    path('history', views.history, name='history'),
    path('chart', views.chart, name='chart'),
    path('check-plan', views.check_plan, name='check_plan'),
    path('test-input/plan-<str:pk_plan>', views.test_input, name='test_input'),
]
