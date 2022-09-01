import logging

from django.shortcuts import redirect
from django.urls import NoReverseMatch
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from .typing import Any, Dict, RootDictEntry, Type


__all__ = [
    "APIRootView",
    "RedirectView",
]


logger = logging.getLogger(__name__)


class RedirectView(APIView):
    """View that redirects every request to given path."""

    reverse_key = ""
    permanent = False

    schema = None  # exclude from schema
    _ignore_model_permissions = True
    authentication_classes = []  # defined by redirected view
    permission_classes = []  # defined by redirected view

    @classmethod
    def with_args(cls, reverse_key: str, permanent: bool) -> Type["RedirectView"]:
        return type("RedirectView", (cls,), {"reverse_key": reverse_key, "permanent": permanent})  # type: ignore

    def general_reponse(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        namespace = request.resolver_match.namespace
        reverse_key = namespace + ":" + self.reverse_key if namespace else self.reverse_key
        return redirect(reverse_key, *args, permanent=self.permanent, **kwargs)

    def get(self, request, *args, **kwargs):  # pragma: no cover
        return self.general_reponse(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):  # pragma: no cover
        return self.general_reponse(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):  # pragma: no cover
        return self.general_reponse(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):  # pragma: no cover
        return self.general_reponse(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):  # pragma: no cover
        return self.general_reponse(request, *args, **kwargs)

    def head(self, request, *args, **kwargs):  # pragma: no cover pylint: disable=method-hidden
        return self.general_reponse(request, *args, **kwargs)

    def options(self, request, *args, **kwargs):  # pragma: no cover
        return self.general_reponse(request, *args, **kwargs)

    def trace(self, request, *args, **kwargs):  # pragma: no cover
        return self.general_reponse(request, *args, **kwargs)


class APIRootView(APIView):
    """Welcome! This is the API root."""

    api_root_dict: Dict[str, RootDictEntry] = {}

    schema = None  # exclude from schema
    _ignore_model_permissions = True

    authentication_classes = []
    permission_classes = []

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        routes = {}
        namespace = request.resolver_match.namespace

        entry: RootDictEntry
        for key, entry in self.api_root_dict.items() or {}:
            reverse_key = namespace + ":" + entry.reverse_key if namespace else entry.reverse_key
            entry.kwargs.update(kwargs)

            try:
                routes[key] = reverse(
                    viewname=reverse_key,
                    args=args,
                    kwargs=entry.kwargs,
                    request=request,
                    format=kwargs.get("format", None),
                )
            except NoReverseMatch as error:  # pragma: no cover
                logger.info(f"No reverse found for {reverse_key!r} with kwargs {entry.kwargs}.", exc_info=error)
                continue

        return Response(routes)
