from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^hello/' ,views.HelloApiView.as_view()),
    url(r'frontpage/', views.FrontPageView.as_view()),
    url(r'coin/', views.CoinView.as_view()),
    url(r'coinpair/', views.CoinPairView.as_view()),
    url(r'archive/', views.ArchiveFrontPageView.as_view()),
    url(r'getavailmarkets/', views.AvailableMarketsView.as_view()),
    url(r'getavailcoinpairs/' , views.AvailableCoinPairsView.as_view()),
    url(r'technicalssummary/', views.TechnicalsSummaryView.as_view()),

    url(r'hourlydata/', views.HourlyDataView.as_view())

]


# url(r'coinpairsummary/' , views.CoinPairSummaryView.as_view()),