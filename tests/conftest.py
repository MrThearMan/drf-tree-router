import os

import pytest
from django.http import HttpRequest
from pytest_django.fixtures import SettingsWrapper
from rest_framework.request import Request


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.django.settings")


@pytest.fixture(scope="session", autouse=True)
def setup_django_settings() -> SettingsWrapper:
    wrapper = SettingsWrapper()
    wrapper.DEBUG = False
    wrapper.LANGUAGE_CODE = "en-us"
    wrapper.LANGUAGES = [("en", "English"), ("fi", "Finland")]

    yield wrapper
    wrapper.finalize()


@pytest.fixture()
def drf_request() -> Request:
    return Request(HttpRequest())
