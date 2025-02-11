from django_filters import rest_framework as filters

from .models import Title


class TitleFilter(filters.FilterSet):
    """Custom filter for Title model."""

    category = filters.CharFilter(
        field_name="category__slug", lookup_expr="iexact"
    )
    genre = filters.CharFilter(field_name="genre__slug", lookup_expr="iexact")
    name = filters.CharFilter(field_name="name", lookup_expr="contains")
    year = filters.NumberFilter(field_name="year", lookup_expr="iexact")

    class Meta:
        model = Title
        fields = ["category", "genre", "name", "year"]
