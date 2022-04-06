import logging
import re

from django.urls import include, re_path
from django.urls.resolvers import URLPattern, URLResolver
from rest_framework.routers import DefaultRouter, Route
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSetMixin

from .typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union, UrlsType, ViewType
from .views import APIRootView as RootView


__all__ = ["TreeRouter"]


logger = logging.getLogger(__name__)


def _new_root_view(name: str, type_: Type[APIView], docstring: Optional[str]) -> Type[APIView]:
    root_view: Type[APIView] = type(name, (type_,), {})  # noqa
    root_view.__doc__ = docstring
    return root_view


class TreeRouter(DefaultRouter):
    """A Router that can nest itself. Also accepts APIViews in addition to ViewSets."""

    registry: List[Tuple[str, ViewType, str, Dict[str, Any]]]
    APIRootView: Type[APIView] = RootView

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        documentation: Optional[str] = None,
        routes: Optional[Dict[str, ViewType]] = None,
        subrouters: Optional[Dict[str, DefaultRouter]] = None,
        **kwargs: Any,
    ):
        """New TreeRouter with given subroutes.

        :param name: Name of the router.
        :param documentation: Router documentation.
        :param routes: Register these routes
        :param subrouters: Nested routers containing more routes.
        :param kwargs: Additional arguments passed to DefaultRouter.
        """

        name = name if name is not None else self.APIRootView.__name__
        self.root_view_name = name
        self.APIRootView = _new_root_view(name, self.APIRootView, documentation)  # pylint: disable=C0103
        self.subroutes: Dict[str, DefaultRouter] = subrouters or {}

        super().__init__(**kwargs)

        if routes:
            for path, view in routes.items():
                self.register(path, view, path)

    def register(self, path: str, view: ViewType, reverse_key: str = None, **kwargs: Any):  # pylint: disable=W0237
        if reverse_key is None:
            reverse_key = self.get_default_basename(view)  # pragma: no cover

        # Construct default values for regex parts
        params = {key: "..." for key in re.compile(path).groupindex}
        params.update(kwargs)
        self.registry.append((path, view, reverse_key, params))

        # Invalidate the urls cache
        if hasattr(self, "_urls"):  # pragma: no cover
            del self._urls

    def get_routes(self, viewset: ViewType) -> List[Route]:
        if issubclass(viewset, ViewSetMixin):
            return super().get_routes(viewset)
        return []  # pragma: no cover

    def get_api_root_view(self, api_urls: UrlsType = None) -> Callable[..., Any]:
        api_root_dict: Dict[str, Tuple[str, Dict[str, Any]]] = {}
        list_name = self.routes[0].name

        for prefix, viewset, basename, kwargs in self.registry:
            if issubclass(viewset, ViewSetMixin):
                api_root_dict[prefix] = list_name.format(basename=basename), kwargs
            else:
                api_root_dict[prefix] = basename, kwargs

        for basename in self.subroutes:
            api_root_dict[rf"{basename}"] = basename, {}

        return self.APIRootView.as_view(api_root_dict=api_root_dict)

    def format_regex(self, url: str, prefix: str, lookup: str = "") -> str:
        regex = url.format(prefix=prefix, lookup=lookup, trailing_slash=self.trailing_slash)
        if not prefix and regex[:2] == "^/":  # pragma: no cover
            regex = "^" + regex[2:]
        return regex

    def get_urls(self) -> UrlsType:  # pylint: disable=R0914
        urls: List[Union[URLResolver, URLPattern]] = self.urls_from_registry()

        if self.include_root_view:
            view = self.get_api_root_view(api_urls=urls)
            root_url = re_path(r"^$", view, name=self.root_view_name)
            urls.append(root_url)

        if self.include_format_suffixes:
            urls = format_suffix_patterns(urls)

        for basename, router in self.subroutes.items():
            router.root_view_name = basename
            router.APIRootView = _new_root_view(basename, router.APIRootView, router.APIRootView.__doc__)
            urls.append(re_path(rf"^{basename}/", include(router.urls)))

        return urls

    def urls_from_registry(self) -> List[Union[URLResolver, URLPattern]]:
        urls: List[Union[URLResolver, URLPattern]] = []

        for prefix, view, basename, _ in self.registry:
            if not issubclass(view, ViewSetMixin):
                regex = self.format_regex(url=self.routes[0].url, prefix=prefix)
                urls.append(re_path(regex, view.as_view(), name=basename))
                continue

            lookup = self.get_lookup_regex(view)
            routes = self.get_routes(view)

            for route in routes:
                mapping = self.get_method_map(view, route.mapping)
                if not mapping:
                    continue

                regex = self.format_regex(url=route.url, prefix=prefix, lookup=lookup)
                initkwargs = route.initkwargs.copy()
                initkwargs.update({"basename": basename, "detail": route.detail})

                view_ = view.as_view(mapping, **initkwargs)
                name = route.name.format(basename=basename)
                urls.append(re_path(regex, view_, name=name))

        return urls
