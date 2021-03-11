from rest_framework import exceptions, serializers
from rest_framework.validators import UniqueValidator
from rest_framework.generics import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Category, Genre, Title, Review, Comment


class CustomTokenObtainSerializer(serializers.Serializer):
    """Higher serializer for token obtaining."""

    username_field = User.USERNAME_FIELD

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields[self.username_field] = serializers.CharField()

        self.fields['confirmation_code'] = serializers.CharField()

    def validate(self, attrs):
        self.user = get_object_or_404(User, email=attrs[self.username_field])

        if not self.user:
            raise exceptions.AuthenticationFailed('The user is not valid.')

        return {}


class CustomTokenObtainPairSerializer(CustomTokenObtainSerializer):
    """Serializer for token obtaining."""
    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def validate(self, attrs):
        data = super(CustomTokenObtainPairSerializer, self).validate(attrs)

        refresh = self.get_token(self.user)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        return data


class CreateUserSerializer(serializers.ModelSerializer):
    """Serializer for user creation action."""

    class Meta:
        fields = ("email",)
        model = User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user endpoints with forbid role changes."""

    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())],
        required=True,
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())],
        required=True,
    )

    class Meta:
        fields = (
            "id",
            "first_name",
            "last_name",
            "username",
            "bio",
            "email",
            "role",
        )
        model = User
        read_only_fields = ("email", "role")


class AdminSerializer(serializers.ModelSerializer):
    """Serializer for user endpoints with allowed role changes."""

    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())],
        required=True,
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())],
        required=True,
    )

    class Meta:
        fields = (
            "id",
            "first_name",
            "last_name",
            "username",
            "bio",
            "email",
            "role",
        )
        model = User
        read_only_fields = ("email",)


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for category endpoints."""

    name = serializers.CharField(required=True)

    class Meta:
        exclude = ("id",)
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    """Serializer for genre endpoints."""

    name = serializers.CharField(required=True)

    class Meta:
        fields = ("name", "slug")
        model = Genre


class GetTitleSerializer(serializers.ModelSerializer):
    """Serializer for title GET endpoints."""

    name = serializers.CharField(required=True)
    genre = GenreSerializer(many=True, required=False)
    category = CategorySerializer(required=False)
    rating = serializers.IntegerField(read_only=True, default=None)

    class Meta:
        fields = "__all__"
        model = Title


class CreateTitleSerializer(serializers.ModelSerializer):
    """Serializer for title POST, PATCH, DELETE endpoints."""

    name = serializers.CharField(required=True)
    genre = serializers.SlugRelatedField(
        many=True,
        queryset=Genre.objects.all(),
        slug_field="slug",
        required=False,
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field="slug", required=False
    )
    rating = serializers.IntegerField(read_only=True, default=None)

    class Meta:
        fields = "__all__"
        model = Title


class CreateReviewSerializer(serializers.ModelSerializer):
    """Serializer for title POST endpoints."""

    text = serializers.CharField(required=True)
    score = serializers.ChoiceField(
        choices=[(i, i) for i in range(1, 11)], required=True
    )
    author = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    title = serializers.SlugRelatedField(
        required=False, slug_field="pk", queryset=Title.objects.all()
    )

    class Meta:
        fields = "__all__"
        model = Review

    def validate(self, data):
        """Check that authors review already exists."""
        title = self.context["view"].kwargs.get("title_id")
        author = self.context["request"].user
        message = "Authors review already exists"
        if Review.objects.filter(title=title, author=author).exists():
            raise serializers.ValidationError(message)
        return data


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for title GET, PATCH, DELETE endpoints."""

    text = serializers.CharField(required=True)
    score = serializers.ChoiceField(
        choices=[(i, i) for i in range(1, 11)], required=True
    )
    author = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    title = serializers.SlugRelatedField(
        required=False, slug_field="pk", queryset=Title.objects.all()
    )

    class Meta:
        fields = "__all__"
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comment endpoints."""

    text = serializers.CharField(required=True)
    author = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    title = serializers.SlugRelatedField(
        required=False, slug_field="pk", queryset=Title.objects.all()
    )
    review = serializers.SlugRelatedField(
        required=False, slug_field="pk", queryset=Review.objects.all()
    )

    class Meta:
        fields = "__all__"
        model = Comment
