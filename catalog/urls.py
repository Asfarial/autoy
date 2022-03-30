from django.urls import path
from . import views
from . import models

app_name="catalog"

urlpatterns = [
    path('', views.IndexView.as_view(), name='home')
]

#adding catalog urls
urlpatterns += [
    path("catalog/", views.CarsListView.as_view(), name="catalog")
]

urlpatterns += [
    path("catalog/search/", views.CarsSearchView.as_view(), name="search")
]


urlpatterns += [
    path("catalog/category/<slug:category>/", views.CarsByCategoryListView.as_view(), name="category")
]


urlpatterns += [
    path("car/<slug:slug>/", views.CarDetailView.as_view(), name="car")
]

urlpatterns += [
    path("rate/<int:pk>", views.rate, name="rate")
]



