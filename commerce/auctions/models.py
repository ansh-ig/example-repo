from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    categoryName = models.CharField(max_length=100)
    
    def __str__(self):
        return self.categoryName

class Listing(models.Model): 
    tittle = models.CharField(max_length=60)
    description = models.CharField(max_length=600)
    imageurl = models.CharField(max_length=1000)
    price = models.FloatField()
    isActive = models.BooleanField(default=True)
    owner = models.ForeignKey (User, on_delete=models.CASCADE, related_name="user")
    category = models.ForeignKey (Category, on_delete=models.CASCADE, blank=True, related_name="category")
    watchlist = models.ManyToManyField( User, blank=True, null=True, related_name="listingWatchlist")


    def __str__(self):
        return self.tittle