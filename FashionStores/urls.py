from django.urls import path

from FashionStores import views

urlpatterns = [
    # path('', views.Login_Admin, name= ''),
    path('login_admin/', views.Login_Admin, name='login_admin'),
    path('login_authentication_admin/', views.Authenticate, name='login_authentication_admin'),
    path('logout_admin/', views.Logout, name='logout_admin'),
    path('admin_index/', views.Index, name='admin_index'),
    path('scrape/', views.Scrap, name='scrape'),
    path('scrape/GetProductResults', views.GetProductResultsAjax),
    path('ScrapeResultList/', views.ScrapResults, name='ScrapeResultList'),
    path('brand_list/', views.Brand_list, name='brand_list'),
    path('product_list/', views.Product_List, name='product_list'),
    path('product_list/GetProductFilter', views.GetProductFilterAjax),
    path('product_size_list/', views.Product_size, name='product_size_list'),
    path('StoreList/', views.Store_List, name='StoreList'),
    path('Store/', views.Stores, name='Store'),
    path('StoreUpdate/', views.StoresUpdate, name='StoreUpdate'),
    path('ScrapAlert/', views.Scrap_Alert, name='ScrapAlert'),
    path('ScrapAlertList/', views.ScrapAlert_List, name='ScrapAlertList'),
    path('ScrapeError/', views.ScrapResultsError, name='ScrapeError'),

]
