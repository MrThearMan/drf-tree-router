from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type, Union

from django.urls import URLPattern, URLResolver
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSetMixin


__all__ = [
    "Any",
    "Dict",
    "Optional",
    "Set",
    "Type",
    "Union",
    "Callable",
    "Tuple",
    "UrlsType",
    "ViewType",
    "List",
]


UrlsType = List[Union[URLResolver, URLPattern]]
ViewType = Union[Type[APIView], Type[ViewSetMixin]]
