from django_filters import rest_framework as filters

from blog.models import BlogM


class BlogFilter(filters.FilterSet):
    category = filters.NumberFilter(method='category_filter')

    class Meta:
        model = BlogM
        fields = ('published', 'is_deleted')


    def category_filter(self, queryset, name, value):
        return queryset.filter(categories__id=value)