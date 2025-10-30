from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('get_data', views.get_data, name='get_data'),
    path('get_filtered_data', views.get_filtered_data, name='get_filtered_data'),
    path('get_chart_data', views.get_chart_data, name='get_chart_data'),
    path('get_unique_values', views.get_unique_values, name='get_unique_values'),
]
