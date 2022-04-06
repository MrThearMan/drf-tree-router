import logging

from django.urls import NoReverseMatch
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from .typing import Any, Dict, Tuple


__all__ = ["APIRootView"]


logger = logging.getLogger(__name__)


class APIRootView(APIView):
    """Welcome! This is the API root."""

    api_root_dict: Dict[str, Tuple[str, Dict[str, Any]]] = {}
    _ignore_model_permissions = False
    schema = None  # exclude from schema

    authentication_classes = []
    permission_classes = []

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        routes = {}
        namespace = request.resolver_match.namespace
        for key, (url_name, params) in self.api_root_dict.items() or {}:
            url_name = namespace + ":" + url_name if namespace else url_name
            params.update(kwargs)
            try:
                routes[key] = reverse(
                    viewname=url_name,
                    args=args,
                    kwargs=params,
                    request=request,
                    format=kwargs.get("format", None),
                )
            except NoReverseMatch:  # pragma: no cover
                logger.info(f"No reverse found for {url_name} with kwargs {params}.")
                continue

        return Response(routes)
