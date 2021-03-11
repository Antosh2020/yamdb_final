from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import UserViewSet, CategoryViewSet, GenreViewSet, TitleViewSet, \
    ReviewViewSet, CommentViewSet, send_password, send_token


router = DefaultRouter()
router.register("users", UserViewSet)
router.register("categories", CategoryViewSet)
router.register("genres", GenreViewSet)
router.register("titles", TitleViewSet, basename="title")
router.register(
    r"titles/(?P<title_id>\d+)/reviews", ReviewViewSet, basename="review"
)
router.register(
    r"titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments",
    CommentViewSet,
    basename="comment",
)

urlpatterns = [
    path(
        "v1/",
        include(
            [
                path(
                    "auth/email/",
                    send_password,
                    name="conf_obtain",
                ),
                path(
                    "auth/token/",
                    send_token,
                    name="token_obtain",
                ),
                path(
                    "token/refresh/",
                    TokenRefreshView.as_view(),
                    name="token_refresh",
                ),
                path("", include(router.urls)),
            ]
        ),
    ),
]
