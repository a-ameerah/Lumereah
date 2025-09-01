from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField(null=True, blank=True)
    skin_type = models.CharField(max_length=50, null=True, blank=False)
    skin_concern = models.CharField(max_length=250, null=True, blank=False)
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
