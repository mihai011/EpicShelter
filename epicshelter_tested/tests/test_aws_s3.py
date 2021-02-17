import os
import sys

from aws_s3.aws_s3 import S3

import pytest
import boto3

from .aws_utils import boto3_mock

@pytest.fixture
def make_mock(monkeypatch):

    monkeypatch.setattr(boto3, "client", boto3_mock)


def test_list_objects(make_mock):

    # mock_client = boto3.client('s3')
    # data = mock_client.list_objects("test_bucket")
    my_client = S3()

    with pytest.raises(ValueError) as excinfo:
        my_client.list_objects(None)

    assert my_client.list_objects("test_bucket") == ["control.txt", "locale.data", "mercator", "merch.png"]


def test_download_object(make_mock):

    my_client = S3()

    with pytest.raises(ValueError) as excinfo:
        my_client.download_fileobj(None, 'control.txt', "test.txt")

    with pytest.raises(ValueError) as excinfo:
        my_client.download_fileobj("mybucket", None, "test.txt")

    with pytest.raises(ValueError) as excinfo:
        my_client.download_fileobj("mybucket", 'control.txt', None)

    my_client.download_fileobj('mybucket', 'control.txt', "test.txt")

    assert open(os.path.join(os.getcwd(), "tests", "remote_data", "control.txt")).read()  == open("test.txt").read()

    os.remove("test.txt")

    