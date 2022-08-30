# Examples

Create a router for the base level of the API.

```python
from tree_router import TreeRouter
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from django.urls import path, include

router = TreeRouter(
    name="router",
    documentation="This is my router's documentation",
)

router.register(r"view", APIView, "view")
router.register(r"viewset", ViewSet, "viewset")


urlpatterns = [
    path("api/", include(router.urls))
]
```

In [DRF Browsable API][browsable-api], the `name` argument will be displayed as the header
of the root view, and the `documentation` as the body text. This results in the following
API structure:

```
router
├── view
└── viewset
```

---

## Subrouters

You can add other routers as subroutes in the API tree:

```python
from tree_router import TreeRouter

sub_router = TreeRouter(
    name="sub_router",
    documentation="This is my sub-router's documentation",
)
sub_router.register(r"subview", APIView, "subview")

router = TreeRouter(
    name="router",
    documentation="This is my routers documentation",
    subrouters={
        "sub_router": sub_router,
    },
)

# Can also do this outside initialization
router.subrouters["sub_router"] = sub_router
```

Now the API structure looks like this:

```
my_router
├── view
├── viewset
├── sub_router
│   └── subview
```

You can nest any number of TreeRouters like this, and even mix in other
routers that derive form DefaultRouter. You can of course extend a TreeRouter's
registry from another router also.

> Note that when you add a router as a subrouter in another router, the name defined
> for the subrouter during its initialization will be ignored in favor of the key
> in the subrouters definition.

---

## Quick routes

You can also register routes to the router at initialization.
Registered view will use the key of the dictionary as its prefix
and basename (i.e., path and reverse lookup-key). You cannot pass
any arguments to the view like this like you can with `TreeRouter.register`.

```python
from tree_router import TreeRouter

router = TreeRouter(
    name="router",
    routes={
        "view": APIView,
    },
)
```

---

## Path parameters

You can add path parameters with regex, or with path converters. TreeRouter adds a `...`
to each parameter to try to reverse the url, so it can be shown in the router root view.
This only works for string parameters, so you must provide a default for other types with
keyword arguments. To use path converters, add `regex=False` to the `TreeRouter.register`
to use it at a specific path, or at router initialization to use them for all paths
in the router by default.

```python
from tree_router import TreeRouter

router = TreeRouter(
    name="router",
    regex=False,  # default
)

router.register(
    r"subview/(?P<name>.+)",
    APIView,
    "subview-name-1",
)
router.register(
    r"subview/(?P<name>\d+)",
    APIView,
    "subview-name-2",
    name="example",
)
router.register(
    "subview/<str:name>",
    APIView,
    "subview-name-3",
    regex=False,
    name="example",
)
```

---

## Redirects

You can add redirects quickly with the `redirects` argument at router initialization,
or with the `TreeRouter.redirect` method. Redirects given at router initialization are
always non-permanent redirects (similar restrictions to quick routes apply here as well),
but you can create permanent redirects by giving `permanent=True` to `TreeRouter.redirect`.

```python
from tree_router import TreeRouter

router = TreeRouter(
    name="router",
    redirects={
        "old/path": "new-path-key-1",
    },
)

router.redirect(
    "old/path/(?P<name>\d+)",
    "new-path-key-2",
    permanent=True,
    name="example",
)
```

---

[browsable-api]: https://www.django-rest-framework.org/topics/browsable-api/
