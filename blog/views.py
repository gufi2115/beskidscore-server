from rest_framework import mixins, viewsets
from .serializers import BlogSerializer,CategoriesSerializer
from .models import BlogM, CategoriesM
from django_filters.rest_framework import DjangoFilterBackend
from .filters import BlogFilter
from .permission import AdminOrReadOnlyPermission


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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        return super().update(request, *args, **kwargs)


class CategoriesViewSet(mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    queryset = CategoriesM.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = (AdminOrReadOnlyPermission,)


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        return super().create(request, *args, **kwargs)


    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        return super().update(request, *args, **kwargs)
