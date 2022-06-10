from django.db import models


# Create your models here.
class Users(models.Model):
    id = models.BigAutoField(db_column='id', primary_key=True)
    email = models.CharField(unique=True, max_length=255, db_column='email', default=None)
    # api_token = models.ForeignKey('Api_Token', on_delete=models.CASCADE, db_column='api_token', max_length=80,
    #                               null=True, default=None)
    first_name = models.CharField(db_column='first_name', max_length=255, blank=True, null=True, default=None)
    last_name = models.CharField(db_column='last_name', max_length=255, blank=True, null=True, default=None)
    display_name = models.CharField(db_column='display_name', max_length=255, blank=True, null=True, default=None)
    gender = models.CharField(db_column='gender', max_length=255, default=None)
    date_of_birth = models.DateField(db_column='date_of_birth', blank=True, null=True, default=None)
    street_address = models.CharField(db_column='street_address', max_length=255, blank=True, null=True, default=None)
    city = models.CharField(db_column='city', max_length=255, blank=True, null=True, default=None)
    state = models.CharField(db_column='state', max_length=255, blank=True, null=True, default=None)
    zip_code = models.CharField(db_column='zip_code', max_length=255, blank=True, null=True, default=None)
    country = models.CharField(db_column='country', max_length=255, blank=True, null=True, default=None)
    latitude = models.CharField(db_column='latitude', max_length=255, blank=True, null=True, default=None)
    longitude = models.CharField(db_column='longitude', max_length=255, blank=True, null=True, default=None)
    email_verified_at = models.DateTimeField(db_column='email_verified_at', blank=True, null=True, auto_now_add=True)
    password = models.CharField(db_column='password', max_length=255, default=None)
    display_image = models.CharField(db_column='display_image', max_length=255, default='default.png')
    is_active = models.SmallIntegerField(db_column='is_active', default=0)
    activation_code = models.CharField(db_column='activation_code', max_length=255, blank=True, null=True, default=None)
    identification_code = models.CharField(db_column='identification_code', max_length=255, blank=True, null=True,
                                           default=None)
    identification_code_expiry = models.CharField(db_column='identification_code_expiry', max_length=255, blank=True,
                                                  null=True,
                                                  default=None)
    reset_token = models.CharField(db_column='reset_token', max_length=255, blank=True, null=True, default=None)
    reset_token_expiry = models.CharField(db_column='reset_token_expiry', max_length=255, blank=True, null=True,
                                          default=None)
    role = models.CharField(db_column='role', max_length=255, default='User')
    remember_token = models.CharField(db_column='remember_token', max_length=100, blank=True, null=True, default=None)
    created_at = models.DateTimeField(db_column='created_at', auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updated_at', auto_now=True)

    class Meta:
        db_table = 'Users'
        app_label = 'ServerAPIs'


class Businesses(models.Model):
    id = models.BigAutoField(db_column='id', primary_key=True)
    name = models.CharField(db_column='name', max_length=255, null=False, default=0)
    service_store_slug = models.TextField(db_column='service_store_slug', blank=True, null=True, default=None)
    street_address = models.CharField(db_column='street_address', max_length=255, default=None)
    city = models.CharField(db_column='city', null=False, max_length=255, default=None)
    state = models.CharField(db_column='state', null=False, max_length=255, default=None)
    country = models.CharField(db_column='country', max_length=255, blank=True, null=True, default=None)
    zip_code = models.CharField(db_column='zip_code', max_length=255, default=None)
    latitude = models.CharField(db_column='latitude', max_length=255, default=None)
    longitude = models.CharField(db_column='longitude', max_length=255, default=None)
    time_zone = models.CharField(db_column='time_zone', max_length=255, blank=True, null=True, default=None)
    ds_active = models.IntegerField(db_column='ds_active', default=0)
    phone = models.CharField(db_column='phone', max_length=255, default=None)
    email = models.CharField(db_column='email', max_length=255, default=None)
    industry = models.CharField(db_column='industry', max_length=255, default=None)
    password = models.CharField(db_column='password', max_length=255, default=None)
    website = models.CharField(db_column='website', max_length=255, blank=True, null=True, default=None)
    image_url = models.TextField(db_column='image_url', blank=True, null=True, default=None)
    opening_closing = models.CharField(db_column='opening_closing', max_length=255, blank=True, null=True, default=None)
    opening_closing_hours_meta = models.TextField(db_column='opening_closing_hours_meta', blank=True, null=True,
                                                  default=None)
    off_days = models.TextField(db_column='off_days', blank=True, null=True, default=None)
    opening_closing_change = models.TextField(db_column='opening_closing_change', blank=True, null=True, default=None)
    description = models.TextField(db_column='description', blank=True, null=True, default=None)
    payment_methods = models.CharField(db_column='payment_methods', max_length=255, blank=True, null=True, default=None)
    types = models.CharField(db_column='types', max_length=255, default='Service')
    social_links = models.CharField(db_column='social_links', max_length=255, blank=True, null=True, default=None)
    rating = models.IntegerField(db_column='rating', blank=True, null=False, default=0)
    categories = models.CharField(db_column='categories', max_length=255, blank=True, null=True, default=None)
    store_url = models.TextField(db_column='store_url', blank=True, null=True, default=None)
    done_status = models.CharField(db_column='done_status', max_length=255, blank=True, null=True, default=None)
    years_in_business = models.IntegerField(db_column='years_in_business', blank=True, null=True, default=None)
    group_gender = models.TextField(db_column='group_gender', default=None)
    created_at = models.DateTimeField(db_column='created_at', auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updated_at', auto_now=True)

    class Meta:
        db_table = 'Businesses'
        app_label = 'ServerAPIs'


class Articles(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    title = models.CharField(db_column='title', max_length=225, default=None)
    content = models.TextField(db_column='content', default=None)
    author = models.CharField(db_column='author', max_length=255, default=None)
    audience = models.CharField(db_column='audience', max_length=50, default='User')
    likes = models.IntegerField(db_column='likes', default=0)
    status = models.CharField(db_column='status', max_length=10, default='Active')
    created_at = models.DateTimeField(db_column='created_at', auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updated_at', auto_now=True)

    class Meta:
        db_table = 'Articles'
        app_label = 'ServerAPIs'


class Article_Comments(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    article_id = models.ForeignKey('Products', on_delete=models.CASCADE, db_column='article_id')
    user_id = models.ForeignKey('Users', on_delete=models.CASCADE, db_column='user_id')
    comment_text = models.TextField(db_column='comment_text', default=None)
    status = models.CharField(db_column='status', max_length=10, default='Active')
    parent_id = models.IntegerField(db_column='parent_id', blank=True, null=True, default=None)
    created_at = models.DateTimeField(db_column='created_at', auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updated_at', auto_now=True)

    class Meta:
        db_table = 'Article_Comments'
        app_label = 'ServerAPIs'


class Business_Claims(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    first_name = models.CharField(db_column='first_name', max_length=255, default=None)
    last_name = models.CharField(db_column='last_name', max_length=255, default=None)
    business_name = models.CharField(db_column='business_name', max_length=255, default=None)
    industry = models.CharField(db_column='industry', max_length=255, default=None)
    business_address = models.CharField(db_column='business_address', max_length=255, default=None)
    city = models.CharField(db_column='city', max_length=255, default=None)
    state = models.CharField(db_column='state', max_length=255, default=None)
    zip_code = models.CharField(db_column='zip_code', max_length=255, default=None)
    country = models.CharField(db_column='country', max_length=255, default=None)
    email = models.CharField(db_column='email', max_length=255, default=None)
    phone = models.CharField(db_column='phone', max_length=255, default=None)
    message = models.TextField(db_column='message', blank=True, null=True, default=None)
    status = models.CharField(db_column='status', max_length=255, default='Pending')
    remarks = models.TextField(db_column='remarks', blank=True, null=True, default=None)
    claim_considered_on = models.DateTimeField(db_column='claim_considered_on', blank=True, null=True, default=None)
    created_at = models.DateTimeField(db_column='created_at', auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updated_at', auto_now=True)

    class Meta:
        db_table = 'Business_Claims'
        app_label = 'ServerAPIs'


class Email_Alerts(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    user_id = models.ForeignKey('Users', on_delete=models.CASCADE, db_column='user_id')
    product_id = models.ForeignKey('Products', on_delete=models.CASCADE, db_column='product_id')
    parent_category_id = models.CharField(db_column='parent_category_id', max_length=11, blank=True, null=True,
                                          default=None)
    our_category_id = models.CharField(db_column='our_category_id', max_length=11, blank=True, null=True, default=None)
    store_id = models.CharField(db_column='store_id', max_length=11, blank=True, null=True, default=None)
    alert_type = models.CharField(db_column='alert_type', max_length=255, default='Product')
    email_address = models.CharField(db_column='email_address', max_length=255, blank=True, null=True, default=None)
    name = models.CharField(db_column='name', max_length=255, blank=True, null=True, default=None)
    alert_status = models.CharField(db_column='alert_status', max_length=255, default='Active')
    alert_nature = models.CharField(db_column='alert_nature', max_length=255, default='Weekly')
    created_at = models.DateTimeField(db_column='created_at', auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updated_at', auto_now=True)

    class Meta:
        db_table = 'Email_Alerts'
        app_label = 'ServerAPIs'


class Favourite_Ads(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    user_id = models.ForeignKey('Users', on_delete=models.CASCADE, db_column='user_id')
    product_id = models.ForeignKey('Products', on_delete=models.CASCADE, db_column='product_id')
    created_at = models.DateTimeField(db_column='created_at', auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updated_at', auto_now=True)

    class Meta:
        db_table = 'Favourite_Ads'
        app_label = 'ServerAPIs'


class Our_Categories(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    parent_category_id = models.IntegerField(db_column='parent_category_id', blank=True, null=True, default=None)
    parent_category_name = models.CharField(db_column='parent_category_name', max_length=255, blank=True, null=True,
                                            default=None)
    category_name = models.CharField(db_column='category_name', max_length=255, blank=True, null=True, default=None)
    category_slug = models.CharField(db_column='category_slug', max_length=255, blank=True, null=True, default=None)
    age = models.CharField(db_column='age', max_length=255, blank=True, null=True, default=None)
    description = models.TextField(db_column='description', default=None)
    keywords = models.TextField(db_column='keywords', default=None)
    seo_keywords = models.TextField(db_column='seo_keywords', default=None)
    suggestion_keywords = models.TextField(db_column='suggestion_keywords', default=None)
    suggestion_dict = models.TextField(db_column='suggestion_dict', default=None)
    products_count = models.IntegerField(db_column='products_count', default=0)
    parent_id = models.IntegerField(db_column='parent_id', blank=True, null=True, default=None)
    created_at = models.DateTimeField(db_column='created_at', auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updated_at', auto_now=True)

    class Meta:
        db_table = 'Our_Categories'
        app_label = 'ServerAPIs'


class Our_Filters(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    parent_category_id = models.IntegerField(db_column='parent_category_id', blank=True, null=True, default=None)
    parent_category_name = models.CharField(db_column='parent_category_name', max_length=255, blank=True, null=True,
                                            default=None)
    parent_category_slug = models.CharField(db_column='parent_category_slug', max_length=255, blank=True, null=True,
                                            default=None)
    category_type = models.CharField(db_column='category_type', max_length=255, blank=True, null=True, default=None)
    body_type = models.CharField(db_column='body_type', max_length=255, blank=True, null=True, default=None)
    filter_type = models.CharField(db_column='filter_type', max_length=255, blank=True, null=True, default=None)
    filter_name = models.TextField(db_column='filter_name', blank=True, null=True, default=None)
    description = models.TextField(db_column='description', default=None)
    keywords = models.TextField(db_column='keywords', default=None)
    seo_keywords = models.TextField(db_column='seo_keywords', default=None)
    suggestion_keywords = models.TextField(db_column='suggestion_keywords', default=None)
    suggestion_dict = models.TextField(db_column='suggestion_dict', default=None)
    created_at = models.DateTimeField(db_column='created_at', auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updated_at', auto_now=True)

    class Meta:
        db_table = 'Our_Filters'
        app_label = 'ServerAPIs'


class Parent_Categories(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    main_category_id = models.IntegerField(db_column='main_category_id', blank=True, null=True, default=None)
    parent_category_name = models.CharField(db_column='parent_category_name', max_length=255, default=None)
    parent_category_slug = models.CharField(db_column='parent_category_slug', blank=True, null=True, max_length=255,
                                            default=None)
    display_order = models.IntegerField(db_column='display_order', default=None)
    products_count = models.IntegerField(db_column='products_count', default=0)
    created_at = models.DateTimeField(db_column='created_at', auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updated_at', auto_now=True)

    class Meta:
        db_table = 'Parent_Categories'
        app_label = 'ServerAPIs'


class Price_Histories(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    product_id = models.ForeignKey('Products', on_delete=models.CASCADE, db_column='product_id')
    price = models.FloatField(db_column='price', default=None)
    sale_price = models.FloatField(db_column='sale_price', blank=True, null=True, default='0.0')
    created_at = models.DateTimeField(db_column='created_at', auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updated_at', auto_now=True)

    class Meta:
        db_table = 'Price_Histories'
        app_label = 'ServerAPIs'


class Products(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    scrapper_result_id = models.IntegerField(db_column='scrapper_result_id', default=None)
    scrapper_product_id = models.IntegerField(db_column='scrapper_product_id', default=None)
    name = models.CharField(db_column='name', max_length=255, default=None)
    product_slug = models.CharField(db_column='product_slug', max_length=255, blank=True, null=True, default=None)
    description = models.TextField(db_column='description', blank=True, null=True, default=None)
    image = models.TextField(db_column='image', blank=True, null=False, default=None)
    all_images = models.TextField(db_column='all_images', blank=True, null=True, default=None)
    regular_size = models.TextField(db_column='regular_size', blank=True, null=True, default=None)
    petite_size = models.TextField(db_column='petite_size', blank=True, null=True, default=None)
    plus_size = models.TextField(db_column='plus_size', blank=True, null=True, default=None)
    tall_size = models.TextField(db_column='tall_size', blank=True, null=True, default=None)
    short_size = models.TextField(db_column='short_size', blank=True, null=True, default=None)
    long_size = models.TextField(db_column='long_size', blank=True, null=True, default=None)
    x_long_size = models.TextField(db_column='x_long_size', blank=True, null=True, default=None)
    color = models.TextField(db_column='color', blank=True, null=True, default=None)
    multicolor = models.IntegerField(db_column='multicolor', default=0)
    display_color = models.TextField(db_column='display_color', blank=True, null=True, default=None)
    material = models.TextField(db_column='material', blank=True, null=True, default=None)
    fit_type = models.CharField(db_column='fit_type', max_length=255, blank=True, null=True, default=None)
    characters = models.TextField(db_column='characters', blank=True, null=True, default=None)
    closure = models.TextField(db_column='closure', blank=True, null=True, default=None)
    dress_length = models.TextField(db_column='dress_length', blank=True, null=True, default=None)
    dress_style = models.TextField(db_column='dress_style', blank=True, null=True, default=None)
    embellishment = models.TextField(db_column='embellishment', blank=True, null=True, default=None)
    feature = models.TextField(db_column='feature', blank=True, null=True, default=None)
    season = models.TextField(db_column='season', blank=True, null=True, default=None)
    garment_care = models.TextField(db_column='garment_care', blank=True, null=True, default=None)
    pattern = models.TextField(db_column='pattern', blank=True, null=True, default=None)
    neckline = models.TextField(db_column='neckline', blank=True, null=True, default=None)
    occasion = models.TextField(db_column='occasion', blank=True, null=True, default=None)
    sleeve_length = models.TextField(db_column='sleeve_length', blank=True, null=True, default=None)
    sleeve_type = models.TextField(db_column='sleeve_type', blank=True, null=True, default=None)
    theme = models.TextField(db_column='theme', blank=True, null=True, default=None)
    fastening_type = models.CharField(db_column='fastening_type', max_length=255, blank=True, null=True, default=None)
    cuff_style = models.CharField(db_column='cuff_style', max_length=255, blank=True, null=True, default=None)
    collar = models.CharField(db_column='collar', max_length=255, blank=True, null=True, default=None)
    price = models.FloatField(db_column='price', blank=True, null=True, default=None)
    price_highest = models.FloatField(db_column='price_highest', blank=True, null=True, default=None)
    sale_price = models.FloatField(db_column='sale_price', default='0.0')
    sale_price_highest = models.FloatField(db_column='sale_price_highest', blank=True, null=True, default=None)
    discount_percentage = models.CharField(db_column='discount_percentage', max_length=255, blank=True, null=True,
                                           default=None)
    discount_percentage_highest = models.CharField(db_column='discount_percentage_highest', max_length=255, blank=True,
                                                   null=True, default=None)
    currency = models.CharField(db_column='currency', max_length=255, default='$')
    brand_id = models.IntegerField(db_column='brand_id', null=True, default=None)
    brand = models.CharField(db_column='brand', max_length=255, blank=True, null=True, default=None)
    brand_slug = models.CharField(db_column='brand_slug', max_length=255, blank=True, null=True, default=None)
    product_url = models.TextField(db_column='product_url', blank=True, null=True, default=None)
    store_name = models.CharField(db_column='store_name', max_length=255, default=None)
    store_logo = models.CharField(db_column='store_logo', max_length=255, default='store_default_logo.png')
    store_url = models.TextField(db_column='store_url', default=None)
    keywords = models.TextField(db_column='keywords', blank=True, null=True, default=None)
    store_id = models.IntegerField(db_column='store_id', default=None)
    our_category_id = models.IntegerField(db_column='our_category_id', default=None)
    our_category_id_2 = models.IntegerField(db_column='our_category_id_2', blank=True, null=True, default=None)
    our_category_name_2 = models.CharField(db_column='our_category_name_2', max_length=255, blank=True, null=True,
                                           default=None)
    our_category_name = models.CharField(db_column='our_category_name', max_length=255, null=True, default=None)
    parent_category_id = models.IntegerField(db_column='parent_category_id', null=True, default=None)
    parent_category_name = models.CharField(db_column='parent_category_name', max_length=255, null=True, default=None)
    parent_category_id_2 = models.IntegerField(db_column='parent_category_id_2', null=True, default=None)
    parent_category_name_2 = models.CharField(db_column='parent_category_name_2', max_length=255, null=True,
                                              default=None)
    promo_offer_type = models.TextField(db_column='promo_offer_type', blank=True, null=True, default=None)
    promo_offer_label = models.TextField(db_column='promo_offer_label', blank=True, null=True, default=None)
    price_offer_type = models.TextField(db_column='price_offer_type', blank=True, null=True, default=None)
    price_offer_label = models.TextField(db_column='price_offer_label', blank=True, null=True, default=None)
    shipping_offer_type = models.TextField(db_column='shipping_offer_type', blank=True, null=True, default=None)
    shipping_offer_label = models.TextField(db_column='shipping_offer_label', blank=True, null=True, default=None)
    other_offer_type = models.TextField(db_column='other_offer_type', blank=True, null=True, default=None)
    other_offer_label = models.TextField(db_column='other_offer_label', blank=True, null=True, default=None)
    promo_dict = models.TextField(db_column='promo_dict', blank=True, null=True, default=None)
    returns_accepted = models.SmallIntegerField(db_column='returns_accepted', default=0)
    benefits_charity = models.SmallIntegerField(db_column='benefits_charity', null=False, default=0)
    climate_pledge_friendly = models.SmallIntegerField(db_column='climate_pledge_friendly', default=0)
    authenticity_guarantee = models.SmallIntegerField(db_column='authenticity_guarantee', default=0)
    is_deleted = models.SmallIntegerField(db_column='is_deleted', default=0)
    last_scrapper_update = models.DateField(db_column='last_scrapper_update', blank=True, null=True, default=None)
    user = models.CharField(db_column='user', max_length=255, default=None)
    created_at = models.DateTimeField(db_column='created_at', auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updated_at', auto_now=True)

    class Meta:
        db_table = 'Products'
        app_label = 'ServerAPIs'


class Product_Color_Sizes(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    product_id = models.ForeignKey('Products', on_delete=models.CASCADE, db_column='product_id')
    color_map_id = models.IntegerField(db_column='color_map_id', default=None)
    color_name = models.CharField(db_column='color_name', max_length=255, blank=True, null=True, default=None)
    color_price = models.CharField(db_column='color_price', max_length=255, default=None)
    size_map_id = models.CharField(db_column='size_map_id', max_length=255, default=None)
    size_type = models.CharField(db_column='size_type', max_length=255, blank=True, null=True, default=None)
    price = models.CharField(db_column='price', max_length=255, blank=True, null=True, default=None)
    sale_price = models.CharField(db_column='sale_price', max_length=255, blank=True, null=True, default=None)
    created_at = models.DateTimeField(db_column='created_at', auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updated_at', auto_now=True)

    class Meta:
        db_table = 'Product_Color_Sizes'
        app_label = 'ServerAPIs'


class Business_Reviews(models.Model):
    id = models.BigAutoField(db_column='id', primary_key=True)
    business_id = models.ForeignKey('Businesses', on_delete=models.CASCADE, db_column='business_id')
    user_id = models.ForeignKey('Users', on_delete=models.CASCADE, db_column='user_id')
    rating = models.IntegerField(db_column='rating', default=0)
    rating_text = models.CharField(db_column='rating_text', max_length=255, blank=True, null=True, default=None)
    review_title = models.CharField(db_column='review_title', max_length=255, default=None)
    review_text = models.TextField(db_column='review_text', default=None)
    review_images = models.TextField(db_column='review_images', blank=True, null=True, default=None)
    parent_id = models.IntegerField(db_column='parent_id', blank=True, null=True, default=None)
    status = models.CharField(db_column='status', max_length=255, default='Active')
    created_at = models.DateTimeField(db_column='created_at', auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updated_at', auto_now=True)

    class Meta:
        db_table = 'Business_Reviews'
        app_label = 'ServerAPIs'


class Settings(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    site_name = models.CharField(db_column='site_name', max_length=255, default='Webinars Admin')
    timezone = models.CharField(db_column='timezone', max_length=255, blank=True, null=True, default=None)
    smtp_host = models.CharField(db_column='smtp_host', max_length=255, blank=True, null=True, default=None)
    smtp_user = models.CharField(db_column='smtp_user', max_length=255, blank=True, null=True, default=None)
    smtp_password = models.CharField(db_column='smtp_password', max_length=255, blank=True, null=True, default=None)
    stripe_key = models.CharField(db_column='stripe_key', max_length=255, blank=True, null=True, default=None)
    auto_posting = models.SmallIntegerField(db_column='auto_posting', default=1)
    created_at = models.DateTimeField(db_column='created_at', auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updated_at', auto_now=True)

    class Meta:
        db_table = 'Settings'
        app_label = 'ServerAPIs'


class Size_Maps(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    our_size = models.CharField(db_column='our_size', max_length=255, blank=True, null=True, default=None)
    our_size_slug = models.CharField(db_column='our_size_slug', max_length=255, blank=True, null=True, default=None)
    size_type = models.CharField(db_column='size_type', max_length=255, blank=True, null=True, default=None)
    size_name = models.CharField(db_column='size_name', max_length=255, default=None)
    size_map_slug = models.TextField(db_column='size_map_slug', default=None)
    created_at = models.DateTimeField(db_column='created_at', auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updated_at', auto_now=True)

    class Meta:
        db_table = 'Size_Maps'
        app_label = 'ServerAPIs'


class Stores(models.Model):
    id = models.BigAutoField(db_column='id', primary_key=True)
    store_name = models.CharField(db_column='store_name', max_length=255, default=None)
    store_slug = models.CharField(db_column='store_slug', max_length=255, blank=True, null=True, default=None)
    store_category = models.CharField(db_column='store_category', max_length=255, blank=True, null=True, default=None)
    parent_category = models.CharField(db_column='parent_category', max_length=255, blank=True, null=True, default=None)
    description = models.TextField(db_column='description', blank=True, null=True, default=None)
    store_logo = models.CharField(db_column='store_logo', max_length=255, default='store_default_logo.png')
    store_url = models.TextField(db_column='store_url', blank=True, null=True, default=None)
    affiliate_url = models.TextField(db_column='affiliate_url', blank=True, null=True, default=None)
    currency = models.CharField(db_column='currency', max_length=255, default='$')
    status = models.CharField(db_column='status', max_length=255, default='Unassigned')
    nature = models.CharField(db_column='nature', max_length=255, default='Store')
    issue_type = models.CharField(db_column='issue_type', max_length=255, default='Other')
    proxy = models.CharField(db_column='proxy', max_length=255, default='No')
    scrapping_type = models.CharField(db_column='scrapping_type', max_length=255, blank=True, null=True, default=None)
    developer_comments = models.CharField(db_column='developer_comments', max_length=255, blank=True, null=True,
                                          default=None)
    site_development_type = models.CharField(db_column='site_development_type', max_length=255, blank=True, null=True,
                                             default=None)
    ap_user_id = models.CharField(db_column='ap_user_id', max_length=255, blank=True, null=True, default=None)
    assigned_on = models.DateTimeField(db_column='assigned_on', blank=True, null=True, auto_now=True)
    completed_on = models.DateTimeField(db_column='completed_on', blank=True, null=True, auto_now=True)
    products_count = models.IntegerField(db_column='products_count', default=0)
    promotions = models.TextField(db_column='promotions', blank=True, null=True, default=None)
    discount_percentage = models.FloatField(db_column='discount_percentage', default=0, blank=True)
    created_at = models.DateTimeField(db_column='created_at', auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updated_at', auto_now=True)

    class Meta:
        db_table = 'Stores'
        app_label = 'ServerAPIs'


class Time_Zones(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    state = models.CharField(db_column='state', max_length=255, blank=True, null=True, default=None)
    city = models.CharField(db_column='city', max_length=255, blank=True, null=True, default=None)
    time_zone = models.CharField(db_column='time_zone', max_length=255, blank=True, null=True, default=None)
    ds_active = models.IntegerField(db_column='ds_active', default=None)
    created_at = models.DateTimeField(db_column='created_at', auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updated_at', auto_now=True)

    class Meta:
        db_table = 'Time_Zones'
        app_label = 'ServerAPIs'


class ProductMatched(models.Model):
    Id = models.AutoField(db_column='Id', primary_key=True)
    ProductId = models.ForeignKey('Products', on_delete=models.CASCADE, db_column='ProductId')
    GroupId = models.IntegerField(db_column='GroupId', default=0)
    Character = models.CharField(db_column='Character', max_length=255, default=None)
    Closure = models.CharField(db_column='Closure', max_length=255, default=None)
    DressLength = models.CharField(db_column='DressLength', max_length=255, default=None)
    DressStyle = models.CharField(db_column='DressStyle', max_length=255, default=None)
    Embellishment = models.CharField(db_column='Embellishment', max_length=255, default=None)
    Feature = models.CharField(db_column='Feature', max_length=255, default=None)
    FitType = models.CharField(db_column='FitType', max_length=255, default=None)
    GarmentCare = models.CharField(db_column='GarmentCare', max_length=255, default=None)
    Material = models.CharField(db_column='Material', max_length=255, default=None)
    Neckline = models.CharField(db_column='Neckline', max_length=255, default=None)
    Occasion = models.CharField(db_column='Occasion', max_length=255, default=None)
    Pattern = models.CharField(db_column='Pattern', max_length=255, default=None)
    FasteningType = models.CharField(db_column='FasteningType', max_length=255, default=None)
    CuffStyle = models.CharField(db_column='CuffStyle', max_length=255, default=None)
    Collar = models.CharField(db_column='Collar', max_length=255, default=None)
    SleeveLength = models.CharField(db_column='SleeveLength', max_length=255, default=None)
    SleeveType = models.CharField(db_column='SleeveType', max_length=255, default=None)
    Themes = models.CharField(db_column='Themes', max_length=255, default=None)
    Season = models.CharField(db_column='Season', max_length=255, default=None)
    ColorMatched = models.IntegerField(db_column='ColorMatched', default=0)
    ParentProductId = models.IntegerField(db_column='ParentProductId', default=0)
    MatchedPercentage = models.FloatField(db_column='MatchedPercentage', default=0)
    DateCreated = models.DateTimeField(db_column='DateCreated', auto_now_add=True)
    DateUpdated = models.DateTimeField(db_column='DateUpdated', auto_now=True)

    class Meta:
        db_table = 'ProductMatched'
        app_label = 'ServerAPIs'


class ProductSimilarity(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    ProductId = models.ForeignKey('Products', on_delete=models.CASCADE, db_column='ProductId')
    GroupId = models.IntegerField(db_column='GroupId', default=0)
    Character = models.CharField(db_column='Character', max_length=255, default=None)
    Closure = models.CharField(db_column='Closure', max_length=255, default=None)
    DressLength = models.CharField(db_column='DressLength', max_length=255, default=None)
    DressStyle = models.CharField(db_column='DressStyle', max_length=255, default=None)
    Embellishment = models.CharField(db_column='Embellishment', max_length=255, default=None)
    Feature = models.CharField(db_column='Feature', max_length=255, default=None)
    FitType = models.CharField(db_column='FitType', max_length=255, default=None)
    GarmentCare = models.CharField(db_column='GarmentCare', max_length=255, default=None)
    Material = models.CharField(db_column='Material', max_length=255, default=None)
    Neckline = models.CharField(db_column='Neckline', max_length=255, default=None)
    Occasion = models.CharField(db_column='Occasion', max_length=255, default=None)
    Pattern = models.CharField(db_column='Pattern', max_length=255, default=None)
    FasteningType = models.CharField(db_column='FasteningType', max_length=255, default=None)
    CuffStyle = models.CharField(db_column='CuffStyle', max_length=255, default=None)
    Collar = models.CharField(db_column='Collar', max_length=255, default=None)
    SleeveLength = models.CharField(db_column='SleeveLength', max_length=255, default=None)
    SleeveType = models.CharField(db_column='SleeveType', max_length=255, default=None)
    Themes = models.CharField(db_column='Themes', max_length=255, default=None)
    Season = models.CharField(db_column='Season', max_length=255, default=None)
    ParentProductId = models.IntegerField(db_column='ParentProductId', default=0)
    DateCreated = models.DateTimeField(db_column='DateCreated', auto_now_add=True)
    DateUpdated = models.DateTimeField(db_column='DateUpdated', auto_now=True)

    class Meta:
        db_table = 'ProductSimilarity'
        app_label = 'ServerAPIs'
