from http.client import responses

from rest_framework import mixins, viewsets, status
from .serializers import BlogSerializer,CategoriesSerializer
from .models import BlogM, CategoriesM
from django_filters.rest_framework import DjangoFilterBackend
from .filters import BlogFilter
from .permission import AdminOrReadOnlyPermission
from rest_framework.response import Response
from beskidscore.settings import MICROSERVICE_TO_SAVE_FILE, MICROSERVICE_TO_SAVE_FILE_API_KEY
import requests

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

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        headers = {'Authorization': f'api-key {MICROSERVICE_TO_SAVE_FILE_API_KEY}'}
        response = requests.delete(url=f'{MICROSERVICE_TO_SAVE_FILE}{obj.image_uuid}/', headers=headers)
        if response.status_code == 204:
            obj.is_deleted = True
            obj.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


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
