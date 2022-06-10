"""FashionAppAPI URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include

from ServerAPIs import SaveProducts, FetchAllCategories, FetchAllFilters, FetchAllStores, RegisterEmailAPI, LoginApi, \
    ForgetPassword, TokenVerification, SetNewPassword, GetFavouritAds, UserEmailAlert, ProfileUpdate, UpdateEmailAlert, \
    ChangePassword, StoresDetails, BrandDetails, SaveCsvOurFilters, SaveCsvCategories, SaveCsvStores, \
    SaveMatchedProducts, SaveSimilarProducts, GetMatchedProducts, GetMatchedProductFilter, GetSimilarProduct, \
    GetSimilarProductFilter, Search, TopStores, PromosCount, FetchSearchWords, \
    Articles, ArticleCommants, GetArticalDetail, ArticlesList, GetUserInfo, SaveSeoCategoryData, SaveSeoFilterData

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('fetch_all_stores', FetchAllStores.fetch_all_stores, name='fetch_all_stores'),
    path('fetch_all_categories', FetchAllCategories.fetch_all_categories, name='fetch_all_categories'),
    path('fetch_all_filters', FetchAllFilters.fetch_all_filters, name='fetch_all_filters'),
    path('save_products', SaveProducts.save_products, name='save_products'),

    path('get_matched_products', GetMatchedProducts.get_matched_products, name='get_matched_products'),
    path('get_matched_product_filter', GetMatchedProductFilter.GetMatchedProductFilter,
         name='get_matched_product_filter'),
    path('get_similar_products', GetSimilarProduct.get_similar_products, name='get_similar_products'),
    path('get_similar_product_filter', GetSimilarProductFilter.get_similar_product_filter,
         name='get_similar_product_filter'),

    path('save_similar_products', SaveSimilarProducts.save_similar_products, name='save_similar_products'),
    path('save_matched_products', SaveMatchedProducts.save_matched_products, name='save_matched_products'),

    path('top_stores', TopStores.top_stores, name='top_stores'),
    path('promos_count', PromosCount.promos_count, name='promos_count'),

    # ====== Farhan ===#
    path('register_email', RegisterEmailAPI.register_email, name='register_email'),
    path('login_Api', LoginApi.login_Api, name='login_Api'),
    path('reset_password', ForgetPassword.reset_password, name='reset_password'),
    path('token_verify', TokenVerification.token_verify, name='token_verify'),
    path('setNewPassword', SetNewPassword.setNewPassword, name='setNewPassword'),
    path('get_Favourite_Ads', GetFavouritAds.get_Favourits_Ads, name='get_Favourite_Ads'),
    path('userEmailAlert', UserEmailAlert.userEmailAlert, name='userEmailAlert'),
    path('profile_update', ProfileUpdate.profile_update, name='profile_update'),
    path('userInformation', GetUserInfo.userInformation, name='userInformation'),
    path('updateEmailAlert', UpdateEmailAlert.updateEmailAlert, name='updateEmailAlert'),
    path('save_seo_category', SaveSeoCategoryData.save_seo_category, name='save_seo_category'),
    path('save_seo_filter', SaveSeoFilterData.save_seo_filter, name='save_seo_filter'),
    path('changePassword', ChangePassword.changePassword, name='changePassword'),
    path('storeDetails', StoresDetails.storeDetails, name='storeDetails'),
    path('brandDetails', BrandDetails.brandDetails, name='brandDetails'),
    path('csvReader', SaveCsvOurFilters.csvReader, name='csvReader'),
    path('saveCsvCategory', SaveCsvCategories.saveCsvCategory, name='saveCsvCategory'),
    path('saveCsvStore', SaveCsvStores.saveCsvStore, name='saveCsvStore'),
    path('fetch_search_words', FetchSearchWords.fetch_search_words, name='fetch_search_words'),
    path('search', Search.search, name='search'),
    path('articles', Articles.articles, name='articles'),
    path('articleCommants', ArticleCommants.article_commants, name='articleCommants'),
    path('articleDetail', GetArticalDetail.articleDetail, name='articleDetail'),
    path('articlesList', ArticlesList.articlesList, name='articlesList'),

    # ===== Ammar =====#
    path('', include('ServerAPIs.ammar_api_urls')),

]
