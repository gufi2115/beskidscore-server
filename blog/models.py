from django.db import models
from users.models import UserM
from filesystempack.drf_filesystem.models import FileInfoM


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
    content = models.TextField()
    excerpt = models.TextField(null=True, blank=True)
    author = models.ForeignKey(UserM, on_delete=models.CASCADE)
    published = models.BooleanField(default=False)
    categories = models.ManyToManyField(CategoriesM, related_name='categories', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.title


class BlogAttachmentM(FileInfoM):
    is_headline = models.BooleanField(default=False)
    blog = models.ForeignKey(BlogM, on_delete=models.CASCADE, related_name='blog')

    def __str__(self):
        return str(self.file_uuid)