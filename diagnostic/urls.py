# diagnostic/urls.py
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.tableau_de_bord, name='dashbord'),
    path('dashbord/', views.tableau_de_bord, name='dashbord'),
    path('vehicule/', views.vehicule_list, name='vehicule_list'),
    path('ajouter_vehicule/', views.ajouter_vehicule, name='ajouter_vehicule'),
    path('modifier_vehicule/<int:pk>/', views.vehicule_update, name='vehicule_update'),
    path('supprimer_vehicule/<int:pk>/', views.vehicule_delete, name='vehicule_delete'),
    
    # Routes des API
    path('api_vehicule_list/', views.api_vehicule_list, name='vehicule_list'),
    path('api_add_vehicule/', views.api_add_vehicule, name='api_add_vehicule'),
    path('api_login/', views.api_login, name='api_login'),
    path('api_refresh_token/', views.api_refresh_token, name='api_refresh_token'),
]
