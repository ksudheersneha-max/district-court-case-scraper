from django.urls import path
from . import views

urlpatterns = [
    path('', views.search_case, name='search_case'),
    # path('captcha-proxy/', views.captcha_proxy, name='captcha_proxy'),
    path('result/', views.result_page, name='result_page'),
    path('download-pdf/', views.download_pdf, name='download_pdf'),
  # optional
]



