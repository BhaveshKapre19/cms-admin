from django.contrib import admin
from .models import UserModel,EmailOtp
# Register your models here.

admin.site.register(EmailOtp)
admin.site.register(UserModel)