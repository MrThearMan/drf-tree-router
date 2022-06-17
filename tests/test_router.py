import pytest
from django.http import HttpResponse


pytestmark = pytest.mark.django_db


def test_root_view(client):
    result: HttpResponse = client.get("/", follow=True, content_type="application/json")
    content = result.json()
    expected = {
        "test1": "http://testserver/test1/",
        "test1/(?P<username>.+)": "http://testserver/test1/.../",
        "test2": "http://testserver/test2/",
        "test2/(?P<username>\\d+)": "http://testserver/test2/0/",
        "route": "http://testserver/route/",
        "plain": "http://testserver/plain/",
    }

    assert content == expected


def test_test1_view(client):
    data = {"email": "foo@bar.com"}
    result: HttpResponse = client.post("/test1/", data=data, content_type="application/json")
    content = result.json()

    assert content == data


def test_test1_item_view(client):
    data = {"email": "foo@bar.com"}
    result: HttpResponse = client.post("/test1/.../", data=data, content_type="application/json")
    content = result.json()

    assert content == data


def test_test2_view(client):
    data = {"email": "foo@bar.com"}
    result: HttpResponse = client.post("/test2/", data=data, content_type="application/json")
    content = result.json()

    assert content == data


def test_test2_item_view(client):
    data = {"email": "foo@bar.com"}
    result: HttpResponse = client.post("/test2/0/", data=data, content_type="application/json")
    content = result.json()

    assert content == data
