from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser,Group,Permission

class CustomUser(AbstractUser):
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], null=True, blank=True)
    medical_history = models.TextField(null=True, blank=True) 
    medications = models.TextField(null=True, blank=True) 
    groups = models.ManyToManyField(Group, related_name="customuser_groups")
    user_permissions = models.ManyToManyField(Permission, related_name="customuser_permissions")

    def __str__(self):
        return self.username