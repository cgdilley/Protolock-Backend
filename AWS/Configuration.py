import boto3

from typing import Optional
import os


def is_aws_configured(profile_name: Optional[str] = None):
    credentials = get_configuration(profile_name)

    return "access_key" in credentials and "secret_key" in credentials


def get_configuration(profile_name: Optional[str] = None) -> Optional[dict]:
    session = boto3.Session() if not profile_name else boto3.Session(profile_name=profile_name)
    credentials = session.get_credentials()

    if not credentials:
        return None

    frozen = credentials.get_frozen_credentials()

    if not frozen:
        return None

    info = {attr: getattr(frozen, attr) for attr in ["access_key", "secret_key"]
            if hasattr(frozen, attr)}
    if session.region_name:
        info["region"] = session.region_name

    return info


def set_configuration(access_key: str,
                      secret_key: str,
                      region: Optional[str] = None,
                      profile_name: Optional[str] = None) -> bool:
    result = os.system(f"aws configure%s\n{access_key}\n{secret_key}%s\n\n" %
                       (f" --profile {profile_name}" if profile_name else "",
                        region + "\n" if region else ""))
    return result == 0


def get_client_args(access_key: Optional[str] = None,
                    secret_key: Optional[str] = None,
                    region: Optional[str] = None,
                    profile_name: Optional[str] = None,
                    **kwargs) -> Optional[dict]:
    """
    Generates a dictionary of key-value pairs that can be unwound as kwargs to pass to the construction of
    a boto3 client.  This will include, at minimum, "aws_access_key_id" and "aws_secret_access_key".
    Will attempt to use the given values first, but if they are empty or None, then will attempt to load
    an existing AWS configuration.  If no configuration could be found, then returns None.

    :param access_key: Optional.  The access key to use in the client configuration.
    :param secret_key: Optional.  The secret key to use in the client configuration.
    :param region: Optional.  The region to use in the client configuration.
    :param profile_name: Optional.  The AWS profile to load existing configuration from.
    :param kwargs: Additional keyword arguments to add to the returned dictionary.
    :return: A dictionary of keyword arguments to use for configuring a boto3 client, or None
    if no configuration could be built.
    """

    if access_key and secret_key:
        current_config = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key
        }
        if region:
            current_config["region_name"] = region

        if not is_aws_configured(profile_name):
            set_configuration(access_key, secret_key, region, profile_name)

    else:

        loaded_config = get_configuration(profile_name)

        if not loaded_config or not loaded_config["access_key"] or not loaded_config["secret_key"]:
            return None

        current_config = {
            "aws_access_key_id": loaded_config["access_key"],
            "aws_secret_access_key": loaded_config["secret_key"]
        }
        if "region" in loaded_config:
            current_config["region_name"] = loaded_config["region"]

    for k, v in kwargs.items():
        current_config[k] = v

    return current_config
