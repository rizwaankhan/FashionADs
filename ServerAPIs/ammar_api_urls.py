# """Business API's URL Configuration"""

from django.urls import path

from ServerAPIs import views

urlpatterns = [
    path('GetProductsListing', views.GetProductsListing, name='GetProductsListing'),
    path('GetProductsFilters', views.GetProductsFilters, name='GetProductsFilters'),
    path('GetProductsDetail', views.GetProductsDetail, name='GetProductsDetail'),
    path('SetProductAlert', views.SetProductAlert, name='SetProductAlert'),
    path('RemoveProductAlert', views.RemoveProductAlert, name='RemoveProductAlert'),
    path('MarkProdcutFavoruite', views.MarkProdcutFavoruite, name='MarkProdcutFavoruite'),
    path('RemoveProdcutFromFavoruite', views.RemoveProdcutFromFavoruite, name='RemoveProdcutFromFavoruite'),
    path('GetSimilarProducts', views.GetSimilarProducts, name='GetSimilarProducts'),
    path('GetPriceHistory', views.GetPriceHistory, name='GetPriceHistory'),
    path('GetBusinessListing', views.GetBusinessListing, name='GetBusinessListing'),
    path('GetBusinessDetails', views.GetBusinessDetails, name='GetBusinessDetails'),
    path('SaveReview', views.SaveReview, name='SaveReview'),
    path('UpdateReview', views.UpdateReview, name='UpdateReview'),
    path('DeleteReview', views.DeleteReview, name='DeleteReview'),

]
