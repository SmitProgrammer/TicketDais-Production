"""TicketDais URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import lthe include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

import Main.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', Main.views.index),
    path('register', Main.views.register),
    path('login', Main.views.login),
    path('forgot-password', Main.views.forgot_psw),
    path('edit', Main.views.edit),
    path('about', Main.views.about),
    path('contact', Main.views.contact)
]
