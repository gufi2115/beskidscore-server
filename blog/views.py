from rest_framework import mixins, viewsets
from .serializers import BlogSerializer,CategoriesSerializer
from .models import BlogM, CategoriesM
from django_filters.rest_framework import DjangoFilterBackend
from .filters import BlogFilter
from .permission import AdminOrReadOnlyPermission
from rest_framework.response import Response
from django.http import FileResponse
from .helpers import file_system

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
        delete_file = file_system.delete_file(obj.image_uuid)
        microservice_status = file_system.status
        if microservice_status == 204:
            obj.is_deleted = True
            obj.save()
            return Response(status=microservice_status)
        if (status := int(microservice_status[:3])) >= 400:
            return Response(status=status)
        raise Exception(microservice_status)


class PhotoViewsSet(BlogMViewSet):
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        file, content_type = file_system.get_file(instance.image_uuid)
        microservice_status = file_system.status
        if microservice_status == 200:
            file_response = FileResponse(file, content_type=content_type)
            return file_response
        if (status := int(microservice_status[:3])) >= 400:
            return Response(status=status)
        raise Exception(microservice_status)


class CategoriesViewSet(mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    queryset = CategoriesM.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = (AdminOrReadOnlyPermission,)

