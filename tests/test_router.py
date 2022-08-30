import pytest
from rest_framework import status


pytestmark = pytest.mark.django_db


def test_root_view(client):
    result = client.get("/", follow=True, content_type="application/json")
    content = result.json()
    expected = {
        "plain": "http://testserver/plain/",
        "redirect1": "http://testserver/redirect1/",
        "redirect2/(?P<username>\\d+)": "http://testserver/redirect2/0/",
        "route": "http://testserver/route/",
        "test1": "http://testserver/test1/",
        "test1/(?P<username>.+)": "http://testserver/test1/.../",
        "test2": "http://testserver/test2/",
        "test2/(?P<username>\\d+)": "http://testserver/test2/0/",
        "test3/(?P<username>[0-9]+)": "http://testserver/test3/1/",
    }

    assert content == expected


def test_test1_view(client):
    data = {"email": "foo@bar.com"}
    result = client.post("/test1/", data=data, content_type="application/json")
    content = result.json()

    assert content == data


def test_test1_item_view(client):
    data = {"email": "foo@bar.com"}
    result = client.post("/test1/.../", data=data, content_type="application/json")
    content = result.json()

    assert content == data


def test_test2_view(client):
    data = {"email": "foo@bar.com"}
    result = client.post("/test2/", data=data, content_type="application/json")
    content = result.json()

    assert content == data


def test_test2_item_view(client):
    data = {"email": "foo@bar.com"}
    result = client.post("/test2/0/", data=data, content_type="application/json")
    content = result.json()

    assert content == data


def test_redirect1_view(client):
    data = {"email": "foo@bar.com"}
    result = client.post("/redirect1/", data=data, content_type="application/json")

    assert result.status_code == status.HTTP_302_FOUND


def test_redirect2_view(client):
    data = {"email": "foo@bar.com"}
    result = client.post("/redirect2/0/", data=data, content_type="application/json")

    assert result.status_code == status.HTTP_301_MOVED_PERMANENTLY
