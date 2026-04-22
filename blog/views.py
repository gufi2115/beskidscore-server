from rest_framework import mixins, viewsets
from .serializers import BlogSerializer, CategoriesSerializer, BlogAttachmentSerializer
from .models import BlogM, CategoriesM, BlogAttachmentM
from django_filters.rest_framework import DjangoFilterBackend
from .filters import BlogFilter
from .permission import AdminOrReadOnlyPermission
from rest_framework.response import Response
from filesystempack.drf_filesystem.views import FileViewSet


class BlogMViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    queryset = BlogM.objects.all()
    serializer_class = BlogSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = BlogFilter
    permission_classes = (AdminOrReadOnlyPermission,)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.is_deleted = True
        obj.save()
        return Response(status=204)


class BlogAttachmentViewSet(FileViewSet):
    queryset = BlogAttachmentM.objects.all()
    serializer_class = BlogAttachmentSerializer

    def get_queryset(self):
        blog_pk = self.kwargs.get('blog_pk')
        if blog_pk:
            return BlogAttachmentM.objects.filter(blog_id=blog_pk)
        return super().get_queryset()

    def create(self, request, *args, **kwargs):
        blog_pk = self.kwargs.get('blog_pk')
        request.data['blog'] = blog_pk
        return super().create(request, *args, **kwargs)

class CategoriesViewSet(mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    queryset = CategoriesM.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = (AdminOrReadOnlyPermission,)

