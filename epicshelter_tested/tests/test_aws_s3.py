from aws_s3.aws_s3 import S3

import pytest
import boto3

from .aws_utils import boto3_mock

from aws_s3.aws_s3 import S3


def test_source(monkeypatch):

    monkeypatch.setattr(boto3, "client", boto3_mock)

    mock_client = boto3.client('s3')
    data = mock_client.list_objects("test_bucket")

    my_client = S3()

    with pytest.raises(ValueError) as excinfo:
        my_client.list_objects(None)

    assert my_client.list_objects("test_bucket") == ["control.txt"]


    
    