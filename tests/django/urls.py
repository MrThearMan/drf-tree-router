from django.core.management import call_command
from django.urls import include, path
from rest_framework import serializers
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from tree_router import TreeRouter


call_command("makemigrations")
call_command("migrate")


class InputSerializer(serializers.Serializer):
    email = serializers.CharField()


class Viewset(ListModelMixin, CreateModelMixin, GenericViewSet):
    serializer_class = InputSerializer

    def perform_create(self, serializer):
        pass

    def get_queryset(self):
        return {}


class View(APIView):
    serializer_class = InputSerializer

    def get(self, request, *args, **kwargs):
        return Response()

    def post(self, request, *args, **kwargs):
        data = {"email": request.data["email"]}
        return Response(data=data)

    def get_serializer(self, *args, **kwargs):
        kwargs.setdefault("context", {"request": self.request, "format": self.format_kwarg, "view": self})
        return self.serializer_class(*args, **kwargs)


router1 = DefaultRouter()
router2 = TreeRouter(name="route")
router3 = TreeRouter(
    routes={"test1": Viewset},
    subrouters={"plain": router1, "route": router2},
    redirects={"redirect1": "test2"},
)

router1.register(r"test1", Viewset, "route2test1")
router2.register(r"test1", Viewset, "route1test1")
router2.register(r"test2", View, "route1test2")
router3.register(r"test1/(?P<username>.+)", Viewset, "test1-username")
router3.register(r"test2", View, "test2")
router3.register(r"test2/(?P<username>\d+)", View, "test2-username", username=0)
router3.register("test3/<int:username>", View, "test3-username", regex=False, username=1)

router3.redirect(r"redirect2/(?P<username>\d+)", "test2-username", permanent=True, username=0)


urlpatterns = [
    path("", include(router3.urls)),
]
