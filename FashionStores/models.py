from django.db import models


# Create your models here.

class FashionUser(models.Model):
    Id = models.AutoField(db_column='Id', primary_key=True)
    DisplayName = models.CharField(db_column='DisplayName', max_length=225)
    Email = models.CharField(db_column='Email', max_length=225)
    Password = models.CharField(db_column='Password', max_length=20)
    RegisterDate = models.DateTimeField(db_column='RegisterDate')

    class Meta:
        db_table = 'FashionUser'
        app_label = 'FashionStores'


class Store(models.Model):
    Id = models.AutoField(db_column='Id', primary_key=True)
    Name = models.CharField(db_column='Name', max_length=225, default=None, null=True, blank=True)
    Url = models.CharField(db_column='Url', max_length=555, default=None, null=True, blank=True)
    AffiliateUrl = models.CharField(db_column='AffiliateUrl', max_length=555, default=None, null=True, blank=True)
    Description = models.TextField(db_column='Description', default=None, null=True, blank=True)
    ScrapperClassName = models.CharField(db_column='ScrapperClassName', max_length=225, default=None, null=True,
                                         blank=True)
    AUSite = models.IntegerField(db_column='AUSite', default=0)
    NZSite = models.IntegerField(db_column='NZSite', default=0)
    USSite = models.IntegerField(db_column='USSite', default=0)
    MergeProductSize = models.IntegerField(db_column='MergeProductSize', default=0)
    ScrapThreadCount = models.IntegerField(db_column='ScrapThreadCount', default=1)
    DownloadThreadCount = models.IntegerField(db_column='DownloadThreadCount', default=1)
    NoReferrer = models.IntegerField(db_column='NoReferrer', default=0)
    Hidden = models.IntegerField(db_column='Hidden', default=0)
    DateCreated = models.DateTimeField(db_column='DateCreated', default=None, null=True, blank=True)
    DateUpdated = models.DateTimeField(db_column='DateUpdated', default=None, null=True, blank=True)

    class Meta:
        db_table = 'Store'
        app_label = 'FashionStores'


class ScrapType(models.Model):
    Id = models.AutoField(db_column='Id', primary_key=True)
    StoreId = models.ForeignKey('Store', on_delete=models.CASCADE, db_column='StoreId')  # Field name made lowercase.
    Code = models.CharField(db_column='Code', max_length=225, default=None)
    Name = models.CharField(db_column='Name', max_length=225, default=None)

    class Meta:
        db_table = 'ScrapType'
        app_label = 'FashionStores'


class Currency(models.Model):
    Id = models.AutoField(db_column='Id', primary_key=True)
    StoreId = models.ForeignKey('Store', on_delete=models.CASCADE, db_column='StoreId')
    Code = models.CharField(db_column='Code', max_length=225, default=None)
    Name = models.CharField(db_column='Name', max_length=225, default=None)

    class Meta:
        db_table = 'Currency'
        app_label = 'FashionStores'


class ScrapResult(models.Model):
    Id = models.AutoField(db_column='Id', primary_key=True)
    StoreId = models.ForeignKey('Store', on_delete=models.CASCADE, db_column='StoreId')  # Field name made lowercase.
    ScrapTypeId = models.ForeignKey('ScrapType', on_delete=models.CASCADE,
                                    db_column='ScrapTypeId')  # Field name made lowercase.
    StartDateTime = models.DateTimeField(db_column='StartDateTime')
    EndDateTime = models.DateTimeField(db_column='EndDateTime')
    NewProductUrlCount = models.IntegerField(db_column='NewProductUrlCount', default=0)
    ExistingProductUrlCount = models.IntegerField(db_column='ExistingProductUrlCount', default=0)
    TotalDistinctProductUrlCount = models.IntegerField(db_column='TotalDistinctProductUrlCount', default=0)
    ProductAddedCount = models.IntegerField(db_column='ProductAddedCount', default=0)
    ProductUpdatedCount = models.IntegerField(db_column='ProductUpdatedCount', default=0)
    ProductDeletedCount = models.IntegerField(db_column='ProductDeletedCount', default=0)
    ProductMergedCount = models.IntegerField(db_column='ProductMergedCount', default=0)
    SaleProductCount = models.IntegerField(db_column='SaleProductCount', default=0)
    TotalProductCount = models.IntegerField(db_column='TotalProductCount', default=0)
    DownloadThreadCount = models.IntegerField(db_column='DownloadThreadCount', default=0)
    WarningCount = models.IntegerField(db_column='WarningCount', default=0)
    ErrorCount = models.IntegerField(db_column='ErrorCount', default=0)
    DateCreated = models.DateTimeField(db_column='DateCreated')
    ProductWithProductSizeCount = models.IntegerField(db_column='ProductWithProductSizeCount', default=0)
    ProductSizeAvailableCount = models.IntegerField(db_column='ProductSizeAvailableCount', default=0)
    ProductSizeWithColorCount = models.IntegerField(db_column='ProductSizeWithColorCount', default=0)
    TotalProductSizeCount = models.IntegerField(db_column='TotalProductSizeCount', default=0)
    ScrapThreadCount = models.IntegerField(db_column='ScrapThreadCount', default=0)
    ProductWithBrandCount = models.IntegerField(db_column='ProductWithBrandCount', default=0)
    UniqueBrandCount = models.IntegerField(db_column='UniqueBrandCount', default=0)

    class Meta:
        db_table = 'ScrapResult'
        app_label = 'FashionStores'


class ScrapError(models.Model):
    Id = models.AutoField(db_column='Id', primary_key=True)
    ScrapResultId = models.ForeignKey('ScrapResult', on_delete=models.CASCADE, db_column='ScrapResultId')
    Message = models.TextField(db_column='Message', default=None)
    StackTrace = models.TextField(db_column='StackTrace', default=None)
    UrlList = models.TextField(db_column='UrlList', default=None)
    Count = models.IntegerField(db_column='Count', default=0)
    Exception = models.TextField(db_column='Exception', default=None)
    DateCreated = models.DateTimeField(db_column='DateCreated')

    class Meta:
        db_table = 'ScrapError'
        app_label = 'FashionStores'


class ProductMergedAndWarning(models.Model):
    Id = models.AutoField(db_column='Id', primary_key=True)
    ScrapResultId = models.ForeignKey('ScrapResult', on_delete=models.CASCADE, db_column='ScrapResultId')
    DeletedDBList = models.TextField(db_column='DeletedList', default=None)
    DeletedWebList = models.TextField(db_column='DeletedWebList', default=None)
    MergedList = models.TextField(db_column='MergedList', default=None)
    WarningList = models.TextField(db_column='WarningList', default=None)
    DateCreated = models.DateTimeField(db_column='DateCreated', auto_now_add=True)

    class Meta:
        db_table = 'ProductMergedAndWarning'
        app_label = 'FashionStores'


class Product(models.Model):
    Id = models.AutoField(db_column='Id', primary_key=True)
    StoreId = models.ForeignKey('Store', on_delete=models.CASCADE, db_column='StoreId')
    Url = models.CharField(db_column='Url', max_length=555, default=None)
    Name = models.CharField(db_column='Name', max_length=225, default=None)
    Price = models.FloatField(db_column='Price', default=0)
    SalePrice = models.FloatField(db_column='SalePrice', default=0, blank=True)
    Brand = models.CharField(db_column='Brand', max_length=555, default=None)
    ImageUrl = models.TextField(db_column='ImageUrl', default=None, blank=True)
    Category = models.TextField(db_column='Category', default=None)
    Description = models.TextField(db_column='Description', default=None)
    UPC_SKU = models.IntegerField(db_column='UPC_SKU', default=None, blank=True, null=True)
    Deleted = models.IntegerField(db_column='Deleted', default=0)
    UpdatedOrAddedOnLastRun = models.IntegerField(db_column='UpdatedOrAddedOnLastRun', default=0)
    DateCreated = models.DateTimeField(db_column='DateCreated', auto_now_add=True)
    DateUpdated = models.DateTimeField(db_column='DateUpdated', auto_now=True)

    class Meta:
        db_table = 'Product'
        app_label = 'FashionStores'


class ProductSize(models.Model):
    Id = models.AutoField(db_column='Id', primary_key=True)
    ProductId = models.ForeignKey('Product', on_delete=models.CASCADE, db_column='ProductId')
    Color = models.CharField(db_column='Color', max_length=255, default=None)
    FitType = models.CharField(db_column='FitType', max_length=255, default=None)
    Size = models.CharField(db_column='Size', max_length=255, default=None)
    MappedSize = models.CharField(db_column='MappedSize', max_length=255, default=None)
    Available = models.IntegerField(db_column='Available', default=0)
    Price = models.FloatField(db_column='Price', default=0, blank=True)
    SalePrice = models.FloatField(db_column='SalePrice', default=0, blank=True)
    DateCreated = models.DateTimeField(db_column='DateCreated', auto_now_add=True)
    DateUpdated = models.DateTimeField(db_column='DateUpdated', auto_now=True)

    class Meta:
        db_table = 'ProductSize'
        app_label = 'FashionStores'


class ScrapAlertType(models.Model):
    Id = models.AutoField(db_column='Id', primary_key=True)
    Code = models.CharField(db_column='Code', max_length=255, default=None)
    Name = models.CharField(db_column='Name', max_length=255, default=None)

    class Meta:
        db_table = 'ScrapAlertType'
        app_label = 'FashionStores'


class ScrapAlerts(models.Model):
    Id = models.AutoField(db_column='Id', primary_key=True)
    ScrapAlertTypeId = models.ForeignKey('ScrapAlertType', on_delete=models.CASCADE, db_column='ScrapAlertTypeId')
    StoreId = models.ForeignKey('Store', on_delete=models.CASCADE, db_column='StoreId')
    Message = models.TextField(db_column='Message', default=None)
    Resolved = models.IntegerField(db_column='Resolved', default=0)
    Comment = models.TextField(db_column='Comment', default=None)
    DayUntilNextCheck = models.IntegerField(db_column='DayUntilNextCheck', default=0)
    DateCreated = models.DateTimeField(db_column='DateCreated', auto_now_add=True)
    DateUpdated = models.DateTimeField(db_column='DateUpdated', auto_now=True)

    class Meta:
        db_table = 'ScrapAlerts'
        app_label = 'FashionStores'


class CategoryPageFilters(models.Model):
    Id = models.AutoField(db_column='Id', primary_key=True)
    ProductUrl = models.TextField(db_column='ProductUrl')
    Filters = models.TextField(db_column='Filters')
    DateCreated = models.DateTimeField(db_column='DateCreated', auto_now_add=True)
    DateUpdated = models.DateTimeField(db_column='DateUpdated', auto_now=True)

    class Meta:
        db_table = 'CategoryPageFilters'
        app_label = 'FashionStores'


class LockedData(models.Model):
    Id = models.AutoField(db_column='Id', primary_key=True)
    ProductId = models.ForeignKey('Product', on_delete=models.CASCADE, db_column='ProductId')
    ScraperResultID = models.CharField(db_column='ScraperResultID', max_length=255, default=None)
    StoreName = models.CharField(db_column='StoreName', max_length=255, default=None)
    ProductUrl = models.TextField(db_column='ProductUrl', max_length=255)
    Color = models.CharField(db_column='Color', max_length=255, default=None)
    Size = models.CharField(db_column='Size', max_length=255, default=None)
    DressStyle = models.CharField(db_column='DressStyle', max_length=255, default=None)
    Occasion = models.CharField(db_column='Occasion', max_length=255, default=None)
    Material = models.CharField(db_column='Material', max_length=255, default=None)
    MaterialPercentage = models.CharField(db_column='MaterialPercentage', max_length=255, default=None)
    DateCreated = models.DateTimeField(db_column='DateCreated', auto_now_add=True)
    DateUpdated = models.DateTimeField(db_column='DateUpdated', auto_now=True)

    class Meta:
        db_table = 'LockedData'
        app_label = 'FashionStores'


class ProductFilters(models.Model):
    Id = models.AutoField(db_column='Id', primary_key=True)
    ProductUrl = models.TextField(db_column='ProductUrl', max_length=255)
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
    ShowOnly = models.CharField(db_column='ShowOnly', max_length=255, default=None)
    ParentCategory = models.CharField(db_column='ParentCategory', max_length=255, default=None)
    Category = models.CharField(db_column='Category', max_length=255, default=None)
    DateCreated = models.DateTimeField(db_column='DateCreated', auto_now_add=True)
    DateUpdated = models.DateTimeField(db_column='DateUpdated', auto_now=True)

    class Meta:
        db_table = 'ProductFilters'
        app_label = 'FashionStores'


class ProductFilterIDs(models.Model):
    Id = models.AutoField(db_column='Id', primary_key=True)
    ProductUrl = models.CharField(db_column='ProductUrl', max_length=255)
    Character = models.CharField(db_column='Character', max_length=255, default=None)
    Closure = models.CharField(db_column='Closure', max_length=255, default=None)
    DressLength = models.CharField(db_column='DressLength', max_length=255, default=None)
    DressStyle = models.CharField(db_column='DressStyle', max_length=255, default=None)
    Embellishment = models.CharField(db_column='Embellishment', max_length=255, default=None)
    Feature = models.CharField(db_column='Feature', max_length=255, default=None)
    FitType = models.CharField(db_column='FitType', max_length=255, default=None)
    GarmentCare = models.CharField(db_column='GarmentCare', max_length=255, default=None)
    Material = models.CharField(db_column='Material', max_length=255, default=None)
    MaterialPercentage = models.CharField(db_column='MaterialPercentage', max_length=255, default=None)
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
    ShowOnly = models.CharField(db_column='ShowOnly', max_length=255, default=None)
    ParentCategory = models.CharField(db_column='ParentCategory', max_length=255, default=None)
    Category = models.CharField(db_column='Category', max_length=255, default=None)
    DateCreated = models.DateTimeField(db_column='DateCreated', auto_now_add=True)
    DateUpdated = models.DateTimeField(db_column='DateUpdated', auto_now=True)

    class Meta:
        db_table = 'ProductFilterIDs'
        app_label = 'FashionStores'


class OurColor(models.Model):
    Id = models.AutoField(db_column='Id', primary_key=True)
    ColorID = models.IntegerField(db_column='ColorID', default=None, blank=True)
    ColorName = models.CharField(db_column='ColorName', max_length=255, default=None)
    DateCreated = models.DateTimeField(db_column='DateCreated', auto_now_add=True)
    DateUpdated = models.DateTimeField(db_column='DateUpdated', auto_now=True)

    class Meta:
        db_table = 'OurColor'
        app_label = 'FashionStores'


class OurStore(models.Model):
    Id = models.BigAutoField(db_column='Id', primary_key=True)
    StoreID = models.IntegerField(db_column='StoreID', blank=True, null=True, default=None)
    StoreName = models.CharField(db_column='StoreName', max_length=255, blank=True, null=True, default=None)
    StoreUrl = models.TextField(db_column='StoreUrl', blank=True, null=True, default=None)
    Nature = models.CharField(db_column='Nature', max_length=255, default='Store')
    DateCreated = models.DateTimeField(db_column='DateCreated', auto_now_add=True)
    DateUpdated = models.DateTimeField(db_column='DateUpdated', auto_now=True)

    class Meta:
        db_table = 'OurStore'
        app_label = 'FashionStores'
