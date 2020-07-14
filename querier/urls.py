from django.urls import path

from .views import index, validate, query

urlpatterns = [

    path('', index, name="home"),
    path('validate/', validate, name='validate'),
    path('query/', query, name='query'),

]
