from django.db import models
from users.models import UserM

class CategoriesM(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.name


class BlogM(models.Model):
    title = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True)
    image_uuid = models.UUIDField(unique=True, editable=False, null=True, blank=True)
    content = models.TextField()
    excerpt = models.TextField(null=True, blank=True)
    author = models.ForeignKey(UserM, on_delete=models.CASCADE)
    published = models.BooleanField(default=False)
    categories = models.ManyToManyField(CategoriesM, related_name='categories', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)


    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.title