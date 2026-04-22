from django.db import transaction
from rest_framework import serializers
from .models import BlogM, CategoriesM, BlogAttachmentM
from unidecode import unidecode
from filesystempack.drf_filesystem.serializers import FileSerializer

class BlogSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', allow_blank=True, read_only=True)

    class Meta:
        model = BlogM
        fields = ['id', 'title', 'content', 'excerpt',
                  'author_id','author_name', 'slug', 'updated_at', 'created_at', 'published', 'categories']
        read_only_fields = ('created_at', 'updated_at', 'slug', 'author_id', 'author_name')
        optional_fields = ('categories',)

    def validate(self, attrs):
        method = self.context['request'].method
        slug = unidecode(attrs.get('title').replace(' ', '-').lower())
        attrs['slug'] = slug
        instance = self.instance
        if method == 'POST' and BlogM.objects.filter(slug=slug).exists():
            raise serializers.ValidationError('A blog with this slug already exists.')
        if method == 'PUT' or method == 'PATCH':
            blog_obj = BlogM.objects.filter(slug=slug).first()
            if blog_obj and blog_obj != instance:
                raise serializers.ValidationError('A blog with this slug already exists.')
        return attrs


    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['author'] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        with transaction.atomic():
            if categories:= validated_data.pop('categories', None):
                instance.categories.remove(*instance.categories.all())
                for category in categories:
                    instance.categories.add(category)
            return super().update(instance, validated_data)


class BlogAttachmentSerializer(FileSerializer):
    class Meta:
        model = BlogAttachmentM
        fields =FileSerializer.Meta.fields + ('id', 'blog', 'is_headline')
        read_only_fields = FileSerializer.Meta.read_only_fields + ('id',)
        extra_kwargs = {'blog': {'required': False}, 'is_headline': {'required': False}}


    def create(self, validated_data):
        with transaction.atomic():
            blog = validated_data['blog']
            if validated_data['is_headline'] and len(attachment_obj := BlogAttachmentM.objects.filter(is_headline=True, blog_id=blog)) > 0:
                attachment_obj[0].is_headline = False
                attachment_obj[0].save()
        return super().create(validated_data)

class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriesM
        fields = ['id', 'name', 'slug']
        read_only_fields = ('id', 'slug')


    def validate(self, attrs):
        method = self.context['request'].method
        slug = unidecode(attrs.get('name').replace(' ', '-').lower())
        attrs['slug'] = slug
        instance = self.instance
        if method == 'POST' and CategoriesM.objects.filter(slug=slug).exists():
            raise serializers.ValidationError('A blog with this slug already exists.')
        if method == 'PUT' or method == 'PATCH':
            category_obj = CategoriesM.objects.filter(slug=slug).first()
            if category_obj and category_obj != instance:
                raise serializers.ValidationError('A blog with this slug already exists.')
        return attrs

