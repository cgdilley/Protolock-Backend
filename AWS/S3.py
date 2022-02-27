from Interfaces import LogMethod, LogLevel

from Errors.AWSError import AWSError

import boto3
import os
from typing import Optional


def upload(filename: str,
           bucket: str,
           bucket_key: str,
           acl: str = None,
           client_kwargs: Optional[dict] = None,
           logger: LogMethod = LogMethod.null,
           **kwargs) -> dict:

    try:
        s3 = boto3.client('s3', **_client_kwargs(client_kwargs))
        with open(filename, "rb") as f:
            options = {
                "Bucket": bucket,
                "Key": bucket_key,
                "Body": f
            }
            if acl:
                options["ACL"] = acl
            for k, v in kwargs.items():
                options[k] = v
            return s3.put_object(**options)
    except IOError:
        raise
    except Exception as e:
        raise AWSError("Failed to upload file to S3", e)


def _client_kwargs(client_kwargs: Optional[dict]) -> dict:
    return client_kwargs if client_kwargs is not None else dict()
