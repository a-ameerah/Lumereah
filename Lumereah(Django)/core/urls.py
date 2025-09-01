from django.urls import path
from . import views

urlpatterns =[
    #path('', views.signup, name='signup'),
    #path('skin_profile/', views.profile, name='skin_profile'),
    path("", views.age, name = "age"),
    path("forms/", views.show_form , name = "show_form"),
    path("skinconcerns.html/", views.skin_concern , name = "skin_concern"),
    path("budget/", views.budget, name = "budget"),
    path("recommendations.html/", views.my_recommendations, name = "my_recommendations"),
    #path("myrecommendations/", views.my_recommendations, name = "my_recommendations")
    ]

