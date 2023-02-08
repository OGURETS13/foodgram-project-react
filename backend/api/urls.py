from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import APISubscribe


# router = DefaultRouter()
# router.register('users', SubscribeViewSet)

urlpatterns = [
    # path('users/subscriptions/', SubscriptionList.as_view()),
    path('users/<int:pk>/subscribe/', APISubscribe.as_view()),
    # path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
