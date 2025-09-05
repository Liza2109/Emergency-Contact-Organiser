
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('contacts/', views.contact_list, name='contact_list'),
    path('contacts/add/', views.contact_add, name='contact_add'),
    path('contacts/<int:pk>/edit/', views.contact_edit, name='contact_edit'),
    path('contacts/<int:pk>/delete/', views.contact_delete, name='contact_delete'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('import/', views.import_csv, name='import_csv'),
    path('export/', views.export_csv, name='export_csv'),
    path('ml_prioritize/', views.ml_prioritize, name='ml_prioritize'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_add, name='category_add'),
    path('api/', views.api_view, name='api'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
]
