import logging

from django.http.response import HttpResponseRedirectBase
from django.shortcuts import redirect
from django.urls import NoReverseMatch
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.utils.urls import replace_query_param
from rest_framework.views import APIView

from .typing import Any, ClassVar, Dict, RootDictEntry, Type

__all__ = [
    "APIRootView",
    "RedirectView",
]


logger = logging.getLogger(__name__)


class RedirectView(APIView):
    """View that redirects every request to given path."""

    reverse_key: str = ""
    permanent: bool = False
    query_string: bool = True

    schema = None  # exclude from schema
    _ignore_model_permissions = True
    authentication_classes = []  # noqa: RUF012
    permission_classes = []  # noqa: RUF012

    @classmethod
    def with_args(cls, reverse_key: str, permanent: bool = False, query_string: bool = True) -> Type["RedirectView"]:
        data = {"reverse_key": reverse_key, "permanent": permanent, "query_string": query_string}
        return type(cls.__name__, (cls,), data)  # type: ignore[return-value]

    def general_response(self, request: Request, *args: Any, **kwargs: Any) -> HttpResponseRedirectBase:
        namespace = request.resolver_match.namespace
        reverse_key = namespace + ":" + self.reverse_key if namespace else self.reverse_key
        url = reverse(reverse_key, args=args, kwargs=kwargs, request=request)

        if self.query_string:
            for param, value in request.query_params.items():
                url = replace_query_param(url, param, value)

        return redirect(url, *args, permanent=self.permanent, **kwargs)

    def get(self, request: Request, *args: Any, **kwargs: Any) -> HttpResponseRedirectBase:  # pragma: no cover
        return self.general_response(request, *args, **kwargs)

    def post(self, request: Request, *args: Any, **kwargs: Any) -> HttpResponseRedirectBase:  # pragma: no cover
        return self.general_response(request, *args, **kwargs)

    def put(self, request: Request, *args: Any, **kwargs: Any) -> HttpResponseRedirectBase:  # pragma: no cover
        return self.general_response(request, *args, **kwargs)

    def patch(self, request: Request, *args: Any, **kwargs: Any) -> HttpResponseRedirectBase:  # pragma: no cover
        return self.general_response(request, *args, **kwargs)

    def delete(self, request: Request, *args: Any, **kwargs: Any) -> HttpResponseRedirectBase:  # pragma: no cover
        return self.general_response(request, *args, **kwargs)

    def head(self, request: Request, *args: Any, **kwargs: Any) -> HttpResponseRedirectBase:  # pragma: no cover
        return self.general_response(request, *args, **kwargs)

    def options(self, request: Request, *args: Any, **kwargs: Any) -> HttpResponseRedirectBase:  # pragma: no cover
        return self.general_response(request, *args, **kwargs)

    def trace(self, request: Request, *args: Any, **kwargs: Any) -> HttpResponseRedirectBase:  # pragma: no cover
        return self.general_response(request, *args, **kwargs)


class APIRootView(APIView):
    """Welcome! This is the API root."""

    api_root_dict: ClassVar[Dict[str, RootDictEntry]] = {}

    schema = None  # exclude from schema
    _ignore_model_permissions = True

    authentication_classes = []  # noqa: RUF012
    permission_classes = []  # noqa: RUF012

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
                    format=kwargs.get("format"),
                )
            except NoReverseMatch as error:  # pragma: no cover
                logger.info(f"No reverse found for {reverse_key!r} with kwargs {entry.kwargs}.", exc_info=error)
                continue

        return Response(routes)
