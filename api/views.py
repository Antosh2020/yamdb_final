from smtplib import SMTPException

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework import viewsets, mixins
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS, AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_500_INTERNAL_SERVER_ERROR
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_simplejwt.exceptions import InvalidToken

from api_yamdb.settings import FROM_EMAIL
from .filters import TitleFilter
from .models import Category, Genre, Title, Review, User
from .permissions import (
    IsAdmin,
    IsAdminOrReadOnly,
    IsModeratorOrOwnerOrReadOnly,
)
from .serializers import (CategorySerializer, GenreSerializer,
                          CommentSerializer, GetTitleSerializer,
                          CreateTitleSerializer, CreateReviewSerializer,
                          ReviewSerializer, CustomTokenObtainPairSerializer,
                          UserSerializer, CreateUserSerializer,
                          AdminSerializer)


@api_view(['POST'])
@permission_classes((AllowAny,))
def send_password(request):
    """View for mailing token"""
    serializer = CreateUserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    token_generator = PasswordResetTokenGenerator()
    user = get_object_or_404(User, email=request.POST.get("email"))
    password = token_generator.make_token(user=user)
    try:
        send_mail(
            subject="Your password reset token",
            message=password,
            from_email=FROM_EMAIL,
            recipient_list=[request.POST.get("email")],
            fail_silently=False,
        )
    except SMTPException as e:
        return Response(
            data="There was an error sending an email.",
            status=HTTP_500_INTERNAL_SERVER_ERROR,
            exception=e,
        )
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes((AllowAny,))
def send_token(request):
    """View for token obtaining"""
    serializer = CustomTokenObtainPairSerializer(data=request.data)
    user = get_object_or_404(User, email=request.POST.get('email'))
    token_generator = PasswordResetTokenGenerator()
    if token_generator.check_token(
            user=user,
            token=request.data['confirmation_code']
    ):
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
    raise InvalidToken()


class UserViewSet(ModelViewSet):
    """Model view for user endpoints."""

    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsAdmin]
    lookup_field = "username"

    def get_serializer_class(self):
        if self.request.user.is_admin or self.request.user.is_staff:
            return AdminSerializer
        return UserSerializer

    @action(detail=False, methods=['PATCH', 'GET'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        user = get_object_or_404(User, username=self.request.user.username)
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class NotPatchViewSet(
    GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
):
    pass


class CategoryViewSet(NotPatchViewSet):
    """View set for category endpoints."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "slug"
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter]
    search_fields = ["=name"]
    pagination_class = PageNumberPagination


class GenreViewSet(NotPatchViewSet):
    """View set for genre endpoints."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = "slug"
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter]
    search_fields = ["=name"]
    pagination_class = PageNumberPagination


class TitleViewSet(viewsets.ModelViewSet):
    """View set for title endpoints."""

    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter

    def get_queryset(self):
        queryset = Title.objects.all().annotate(
            rating=Avg("reviews_title__score")
        )
        return queryset.order_by("-id")

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return GetTitleSerializer
        return CreateTitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """View set for review endpoints."""

    permission_classes = [IsModeratorOrOwnerOrReadOnly]

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get("title_id"))
        return title.reviews_title.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get("title_id"))
        serializer.save(author=self.request.user, title=title)

    def get_serializer_class(self):
        if self.request.method != "POST":
            return ReviewSerializer
        return CreateReviewSerializer


class CommentViewSet(viewsets.ModelViewSet):
    """View set for comment endpoints."""

    serializer_class = CommentSerializer
    permission_classes = [IsModeratorOrOwnerOrReadOnly]

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            title_id=self.kwargs.get("title_id"),
            pk=self.kwargs.get("review_id")
        )
        serializer.save(author=self.request.user, review=review)

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            title_id=self.kwargs.get("title_id"),
            pk=self.kwargs.get("review_id")
        )
        return review.comments_review.all()
