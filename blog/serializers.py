from django.db import transaction
from rest_framework import serializers
from .models import BlogM, CategoriesM
from unidecode import unidecode
from beskidscore.settings import MICROSERVICE_TO_SAVE_FILE, MICROSERVICE_TO_SAVE_FILE_API_KEY
import requests

class BlogSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', allow_blank=True, read_only=True)
    image = serializers.FileField(write_only=True, required=True)
    featured_image = serializers.SerializerMethodField()

    class Meta:
        model = BlogM
        fields = ['id', 'title', 'content', 'featured_image', 'excerpt', 'image',
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
        image = validated_data.pop('image')
        headers = {
            'Authorization': f'api-key {MICROSERVICE_TO_SAVE_FILE_API_KEY}'
        }
        response = requests.post(url=f"{MICROSERVICE_TO_SAVE_FILE}", files={'file': (image.name, image, image.content_type)}, headers=headers)
        validated_data['image_uuid'] = response.json()['id']
        return super().create(validated_data)


    def update(self, instance, validated_data):
        with transaction.atomic():
            if categories:= validated_data.pop('categories', None):
                instance.categories.remove(*instance.categories.all())
                for category in categories:
                    instance.categories.add(category)
            return super().update(instance, validated_data)


    def get_featured_image(self, obj):
        url = MICROSERVICE_TO_SAVE_FILE
        return f"{url}{obj.image_uuid}/"


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

