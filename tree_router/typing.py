from typing import Any, Callable, Dict, List, NamedTuple, Optional, Set, Tuple, Type, Union

from django.urls import URLPattern, URLResolver
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSetMixin

__all__ = [
    "Any",
    "Callable",
    "Dict",
    "List",
    "Optional",
    "RegistryEntry",
    "RootDictEntry",
    "Set",
    "Tuple",
    "Type",
    "Union",
    "UrlsType",
    "ViewType",
]


UrlsType = List[Union[URLResolver, URLPattern]]
ViewType = Union[Type[APIView], Type[ViewSetMixin]]


class RegistryEntry(NamedTuple):
    path: str
    view: ViewType
    reverse_key: str
    kwargs: Dict[str, Any]


class RootDictEntry(NamedTuple):
    reverse_key: str
    kwargs: Dict[str, Any]
