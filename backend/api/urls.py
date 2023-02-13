from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    APIFavorite,
    APISubscribe,
    APIToShoppingCart,
    CustomUserViewSet,
    GetShoppingCart,
    IngredientViewSet,
    RecipeViewset,
    SubscriptionList,
    TagViewSet
)


router = DefaultRouter()
router.register(r'recipes', RecipeViewset, basename='recipe')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'ingredients', IngredientViewSet, basename='ingredient')
router.register(r'users', CustomUserViewSet, basename='user')

urlpatterns = [
    path('recipes/download_shopping_cart/', GetShoppingCart.as_view()),
    path('recipes/<int:pk>/favorite/', APIFavorite.as_view()),
    path('recipes/<int:pk>/shopping_cart/', APIToShoppingCart.as_view()),
    path('users/<int:pk>/subscribe/', APISubscribe.as_view()),
    path('users/subscriptions/', SubscriptionList.as_view()),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
