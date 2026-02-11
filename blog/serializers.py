from django.db import transaction
from rest_framework import serializers
from .models import BlogM, CategoriesM
from unidecode import unidecode
from .helpers import file_system

class BlogSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', allow_blank=True, read_only=True)
    image = serializers.FileField(write_only=True, required=True)

    class Meta:
        model = BlogM
        fields = ['id', 'title', 'content', 'excerpt', 'image',
                  'author_id','author_name', 'slug', 'updated_at', 'created_at', 'published', 'categories', 'is_deleted']
        read_only_fields = ('created_at', 'updated_at', 'slug', 'author_id', 'author_name', 'is_deleted')
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
        image = validated_data.pop('image')
        uuid = file_system.save_file(file=image, content_type=image.content_type)
        status = file_system.status
        if status == 201:
            validated_data['image_uuid'] = uuid
            return super().create(validated_data)
        else:
            raise Exception(status)

    def update(self, instance, validated_data):
        with transaction.atomic():
            if categories:= validated_data.pop('categories', None):
                instance.categories.remove(*instance.categories.all())
                for category in categories:
                    instance.categories.add(category)
            return super().update(instance, validated_data)

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

