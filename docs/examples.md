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

You can add other routers as subroutes in the API tree:

```python
from tree_router import TreeRouter
...

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
...
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

You can also register routes to the router at initialization.

```python
from tree_router import TreeRouter

router = TreeRouter(
    name="router",
    routes={"view": APIView},
)
```

Registered view will now use the key of the dictionary as its prefix and basename
(i.e., path and reverse lookup-key).


[browsable-api]: https://www.django-rest-framework.org/topics/browsable-api/
