from __future__ import annotations

from Interfaces import JSONable
from Errors import APIError, AWSError, ExecutionError
from Utilty import DictUtils, TimeUtils

import json
from typing import Optional, Union, Dict, Any, Type, List
from datetime import datetime

_QueryValue = Union[str, int, float, bool, datetime, dict]
QueryValue = Union[_QueryValue, Type[_QueryValue]]


class Wrapper:

    def __init__(self, event: dict, context: dict, verbose: bool = False):
        self._result: Optional[dict] = None
        self._status_code: Optional[int] = None
        self.args: LambdaArguments = LambdaArguments.parse_event(event)
        self._verbose = verbose
        self.response_headers = {"Content-Type": "application/json"}
        if verbose:
            print("EVENT = " + json.dumps(event))
            print(str(self.args))

    @property
    def result(self) -> dict:
        return self._result

    def set_result(self, result: Union[dict, JSONable], status_code: int = 200):
        self._result = result.to_json() if isinstance(result, JSONable) else result
        self._status_code = status_code
        if self._verbose:
            print(f"Set result ({self._status_code}): {json.dumps(self._result)}")

    def add_cors_header(self):
        self.response_headers["Access-Control-Allow-Origin"] = "*"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type == ExecutionError:
            self._result = {
                "statusCode": exc_value.http_status_code,
                "headers": self.response_headers,
                "body": json.dumps(exc_value.to_json())
            }
            print(f"ERROR: {json.dumps(exc_value.to_json())}")
        elif exc_type is not None:
            e = ExecutionError.wrap(exc_value)
            self._result = {
                "statusCode": e.http_status_code,
                "headers": self.response_headers,
                "body": json.dumps(e.to_json())
            }
            print(f"ERROR: {json.dumps(e.to_json())}")
        elif self._result is not None:
            self._result = {
                "statusCode": self._status_code if self._status_code is not None else 200,
                "headers": self.response_headers,
                "body": json.dumps(self._result)
            }
        else:
            self._result = {
                "statusCode": 204,
                "headers": self.response_headers,
                "body": "{}"
            }
        if self._verbose:
            print(f"Result = {json.dumps(self._result)}")
        return True


class LambdaArguments:

    def __init__(self, path_params: Dict[str, str],
                 query_params: Dict[str, str],
                 headers: Dict[str, str],
                 body: dict):
        self.path_params = path_params if path_params else dict()
        self.query_params = query_params if query_params else dict()
        self.headers = headers if headers else dict()
        self.body = body if body else dict()

    def __str__(self) -> str:
        return f"Path params ({len(self.path_params)}): [{','.join(self.path_params.keys())}] | " \
               f"Query params ({len(self.query_params)}): [{','.join(self.query_params.keys())}] | " \
               f"Headers ({len(self.headers)}): [{','.join(self.headers.keys())}] | " \
               f"Body ({len(self.body)}): [{','.join(self.body.keys())}]"

    @staticmethod
    def parse_event(event: dict) -> LambdaArguments:
        body: Union[str, dict] = DictUtils.get_or_default(event, "body", default=dict())
        if type(body) == str:
            body = json.loads(body)
        return LambdaArguments(
            path_params=DictUtils.get_or_default(event, "pathParameters", default=dict()),
            query_params=DictUtils.get_or_default(event, "queryStringParameters", default=dict()),
            headers=DictUtils.get_or_default(event, "headers", default=dict()),
            body=body,
        )

    def get_only_path_param(self) -> str:
        if len(self.path_params) == 1:
            return list(self.path_params.values())[0]
        raise APIError(f"Must have exactly one path parameter, has {len(self.path_params)}.")

    def get_query(self, key: str, val_type: Type[QueryValue] = str,
                  delimiter: str = None,
                  default: QueryValue = None) -> Union[QueryValue, List[QueryValue], None]:
        val = DictUtils.get_or_default(self.query_params, key, default=default)
        if val is None:
            return None

        if delimiter is None:
            val = self._parse_query_value(val, val_type=val_type)
            if val is None:
                return default
            return val

        split = val.split(delimiter)
        return [self._parse_query_value(s, val_type=val_type) for s in split]

    def get_body_parameter(self, key: str, val_type: Type[QueryValue] = str, is_list: bool = True,
                           default: QueryValue = None) -> Union[QueryValue, List[QueryValue], None]:
        val = DictUtils.get_or_default(self.body, key, default=default)
        if val is None:
            return None

        if is_list:
            return [self._parse_query_value(v, val_type=val_type) for v in val]

        val = self._parse_query_value(val, val_type=val_type)
        if val is None:
            return default
        return val

    def get_query_or_body_parameter(self, key: str, val_type: Type[QueryValue] = str,
                                    delimiter: Optional[str] = None,
                                    default: QueryValue = None) -> Union[QueryValue, List[QueryValue], None]:
        val = self.get_query(key, val_type=val_type, delimiter=delimiter, default=None)
        if val is not None:
            return val

        return self.get_body_parameter(key, val_type=val_type, is_list=(delimiter is not None), default=default)


    @staticmethod
    def _parse_query_value(v: Optional[QueryValue],
                           val_type: Type[QueryValue] = str) -> Optional[QueryValue]:
        if type(v) == val_type:
            return v
        if v is None:
            return None
        if val_type == str:
            return v
        if val_type == type:
            if v == "str":
                return str
            if v == "int":
                return int
            if v == "float":
                return float
            if v == "bool":
                return bool
            if v == "datetime":
                return datetime
            if v == "dict":
                return dict
            return None
        elif val_type == int:
            return int(v)
        elif val_type == float:
            return float(v)
        elif val_type == bool:
            if v.lower() in ["t", "true", "tru", "yes", "y", "1"]:
                return True
            elif v.lower in ["f", "false", "fal", "no", "n", "0"]:
                return False
            return None
        elif val_type == datetime:
            return TimeUtils.parse_date(v)
        elif val_type == dict:
            return json.loads(v)
        else:
            raise APIError(f"Invalid query type: {val_type.__name__}")
