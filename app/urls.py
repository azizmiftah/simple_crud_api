"""simple_crud_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from views import *

urlpatterns = [
    url(r'^login/$', ObtainTokenView.as_view()),
    url(r'^register/$', RegisterView.as_view()),
    url(r'^user/(?P<id>[0-9]+)/$', UserView.as_view()),
    url(r'^user/$', UserView.as_view()),
    url(r'^article/(?P<id>[0-9]+)/$', ArticleView.as_view()),
    url(r'^article/$',ArticleView.as_view()),
    url(r'^activate/$', ActivateView.as_view()),
]
