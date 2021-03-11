from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from .manager import UserManager
from .validators import not_me_validator, less_than_current


class Roles(models.TextChoices):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"


class User(AbstractBaseUser, PermissionsMixin):
    """User model with email as username field."""

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        verbose_name="username",
        max_length=150,
        unique=True,
        null=True,
        blank=True,
        validators=[username_validator, not_me_validator],
        error_messages={"unique": "A user with that username already exists."},
    )
    email = models.EmailField(verbose_name="email address", unique=True)
    first_name = models.CharField(
        verbose_name="first name", max_length=30, blank=True
    )
    last_name = models.CharField(
        verbose_name="last name", max_length=30, blank=True
    )
    date_joined = models.DateTimeField(
        verbose_name="date joined", auto_now_add=True
    )
    is_active = models.BooleanField(verbose_name="active", default=True)
    is_staff = models.BooleanField(verbose_name="staff status", default=False)
    bio = models.TextField(
        verbose_name="biography", max_length=500, blank=True
    )
    role = models.CharField(
        verbose_name="user role",
        max_length=20,
        choices=Roles.choices,
        default=Roles.USER,
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    @property
    def is_admin(self):
        return self.role == Roles.ADMIN

    @property
    def is_moderator(self):
        return self.role == Roles.MODERATOR

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ["-id"]


class Category(models.Model):
    """Category model."""

    name = models.CharField(verbose_name="category name", max_length=200)
    slug = models.SlugField(verbose_name="category slug", unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"
        ordering = ["-id"]


class Genre(models.Model):
    """Genre model."""

    name = models.CharField(verbose_name="genre name", max_length=200)
    slug = models.SlugField(verbose_name="genre slug", unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "genre"
        verbose_name_plural = "genres"
        ordering = ["-id"]


class Title(models.Model):
    """Title model."""

    name = models.CharField(verbose_name="title name", max_length=200)
    year = models.IntegerField(
        verbose_name="title year",
        blank=True,
        null=True,
        validators=[less_than_current],
        db_index=True
    )
    description = models.TextField(verbose_name="title description", null=True)
    genre = models.ManyToManyField(Genre, related_name="title_genre")
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name="title_category",
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "title"
        verbose_name_plural = "titles"
        ordering = ["-id"]


class Review(models.Model):
    """Review model."""

    text = models.TextField(verbose_name="review text")
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name="reviews_title"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="review_user"
    )
    score = models.IntegerField(
        verbose_name="review score",
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    pub_date = models.DateTimeField(
        verbose_name="publication date", auto_now_add=True, db_index=True
    )

    class Meta:
        verbose_name = "review"
        verbose_name_plural = "reviews"
        ordering = ["-id"]


class Comment(models.Model):
    """Comment model."""

    text = models.TextField(verbose_name="comment text")
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name="comments_review"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comment_user"
    )
    pub_date = models.DateTimeField(
        verbose_name="publication date", auto_now_add=True
    )

    class Meta:
        ordering = ["-id"]
