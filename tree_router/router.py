import logging
import re

from django.urls import include, re_path
from django.urls.resolvers import URLPattern, URLResolver, _route_to_regex
from rest_framework.routers import DefaultRouter, Route
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSetMixin

from .typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    RegistryEntry,
    RootDictEntry,
    Tuple,
    Type,
    Union,
    UrlsType,
    ViewType,
)
from .views import APIRootView as RootView
from .views import RedirectView

__all__ = [
    "TreeRouter",
]


logger = logging.getLogger(__name__)


def _new_root_view(name: str, type_: Type[APIView], docstring: Optional[str]) -> Type[APIView]:
    root_view: Type[APIView] = type(name, (type_,), {})  # noqa
    root_view.__doc__ = docstring
    return root_view


class TreeRouter(DefaultRouter):
    """A Router that can nest itself. Also accepts APIViews in addition to ViewSets."""

    registry: List[RegistryEntry]
    APIRootView: Type[APIView] = RootView

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        documentation: Optional[str] = None,
        routes: Optional[Dict[str, ViewType]] = None,
        subrouters: Optional[Dict[str, DefaultRouter]] = None,
        redirects: Optional[Dict[str, str]] = None,
        regex: bool = True,
        **kwargs: Any,
    ):
        """New TreeRouter with given subroutes.

        :param name: Name of the router.
        :param documentation: Router documentation.
        :param routes: Register these routes.
        :param subrouters: Nested routers containing more routes.
        :param regex: If False, use paths and converters for paths by default (e.g. <slug:title>).
        :param kwargs: Additional arguments passed to DefaultRouter.
        """

        name = name if name is not None else self.APIRootView.__name__
        self.root_view_name = name
        self.APIRootView = _new_root_view(name, self.APIRootView, documentation)  # pylint: disable=C0103
        self.subrouters: Dict[str, DefaultRouter] = subrouters or {}
        self.regex = regex

        super().__init__(**kwargs)

        if routes:
            for path, view in routes.items():
                self.register(path, view, path, regex=self.regex)

        if redirects:
            for old_path, reverse_key in redirects.items():
                self.redirect(old_path, reverse_key, regex=self.regex)

    def register(  # pylint: disable=arguments-renamed
        self,
        path: str,
        view: ViewType,
        reverse_key: str = None,
        regex: bool = True,
        **kwargs: Any,
    ) -> None:
        """Register a view in the given path with the given reverse-key.

        :param path: Path to register the view at.
        :param view: View to register.
        :param reverse_key: Key to use for `django.urls.reverse()`
        :param regex: If False, use path converters for the path (e.g. <slug:title>).
        :param kwargs: Additional arguments to pass to the view in order for the
                       APIRootView to find the view with `django.urls.reverse()`
                       for displaying in the root view.
        """
        if reverse_key is None:
            reverse_key = self.get_default_basename(view)  # pragma: no cover

        if not regex or not self.regex:
            path, _ = _route_to_regex(path)
            path = path[1:]  # remove leading ^

        # Construct default values for regex parts
        params = {key: "..." for key in re.compile(path).groupindex}
        params.update(kwargs)
        self.registry.append(
            RegistryEntry(
                path=path,
                view=view,
                reverse_key=reverse_key,
                kwargs=params,
            ),
        )

        # Invalidate the urls cache
        if hasattr(self, "_urls"):  # pragma: no cover
            del self._urls

    def redirect(  # pylint: disable=too-many-arguments
        self,
        path: str,
        reverse_key: str,
        regex: bool = True,
        permanent: bool = False,
        query_string: bool = True,
        **kwargs: Any,
    ) -> None:
        """Add a redirect from a given path to the path resolved with the given reverse key.

        :param path: Old path to redirect.
        :param reverse_key: Reverse key for `django.urls.reverse()` to the new path.
        :param regex: If False, use path converters for the path (e.g. <slug:title>).
        :param permanent: Is the redirect permanent (301) or not (302)?
        :param query_string: Should query string be copied to the redirected url?
        :param kwargs: Additional arguments to pass to the view in order for the
                       APIRootView to find the view with `django.urls.reverse()`
                       for displaying in the root view.
        """
        self.register(
            path=path,
            view=RedirectView.with_args(reverse_key, permanent, query_string),
            reverse_key=f"{reverse_key}-{path}",
            regex=regex,
            **kwargs,
        )

    def get_routes(self, viewset: ViewType) -> List[Route]:
        if issubclass(viewset, ViewSetMixin):
            return super().get_routes(viewset)
        return []  # pragma: no cover

    def get_api_root_view(self, api_urls: UrlsType = None) -> Callable[..., Any]:
        api_root_dict: Dict[str, Tuple[str, Dict[str, Any]]] = {}
        list_name = self.routes[0].name

        for entry in self.registry:
            if issubclass(entry.view, ViewSetMixin):
                api_root_dict[entry.path] = RootDictEntry(
                    reverse_key=list_name.format(basename=entry.reverse_key),
                    kwargs=entry.kwargs,
                )
            else:
                api_root_dict[entry.path] = RootDictEntry(
                    reverse_key=entry.reverse_key,
                    kwargs=entry.kwargs,
                )

        for basename in self.subrouters:
            api_root_dict[rf"{basename}"] = RootDictEntry(
                reverse_key=basename,
                kwargs={},
            )

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

        for basename, router in self.subrouters.items():
            router.root_view_name = basename
            router.APIRootView = _new_root_view(basename, router.APIRootView, router.APIRootView.__doc__)
            urls.append(re_path(rf"^{basename}/", include(router.urls)))

        return urls

    def urls_from_registry(self) -> List[Union[URLResolver, URLPattern]]:
        urls: List[Union[URLResolver, URLPattern]] = []

        for entry in self.registry:
            if not issubclass(entry.view, ViewSetMixin):
                regex = self.format_regex(url=self.routes[0].url, prefix=entry.path)
                urls.append(re_path(regex, entry.view.as_view(), name=entry.reverse_key))
                continue

            lookup = self.get_lookup_regex(entry.view)
            routes = self.get_routes(entry.view)

            for route in routes:
                mapping = self.get_method_map(entry.view, route.mapping)
                if not mapping:
                    continue

                regex = self.format_regex(url=route.url, prefix=entry.path, lookup=lookup)
                initkwargs = route.initkwargs.copy()
                initkwargs.update({"basename": entry.reverse_key, "detail": route.detail})

                view_ = entry.view.as_view(mapping, **initkwargs)
                name = route.name.format(basename=entry.reverse_key)
                urls.append(re_path(regex, view_, name=name))

        return urls
