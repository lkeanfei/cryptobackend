from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^hello/' ,views.HelloApiView.as_view()),
    url(r'frontpage/', views.FrontPageView.as_view()),
    url(r'hourlydata/', views.HourlyDataView.as_view())

]