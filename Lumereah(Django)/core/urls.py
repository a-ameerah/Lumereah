from django.urls import path
from . import views

urlpatterns =[
    path("", views.age, name = "age"),
    path("forms.html", views.show_form , name = "show_form"),
    path("skinconcerns.html/", views.skin_concern , name = "skin_concern"),
    path("budget.html/", views.budget, name = "budget"),
    path("recommendations.html/", views.ai_recommendations, name = "ai_recommendations"),
    #path("myrecommendations/", views.my_recommendations, name = "my_recommendations")
    ]

