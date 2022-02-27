from __future__ import annotations

from enum import Enum
from typing import Optional
import traceback
import sys

from Interfaces import JSONable
from Errors.ExecutionError.ErrorType import *


class ExecutionError(Exception, JSONable):

    def __init__(self, t: ErrorType, message: str, details: Optional[dict] = None):
        self.type = t
        self.message = message
        self.details = details

    def __str__(self) -> str:
        return f"[{self.code}]({self.description}) - {self.message}"

    def __repr__(self) -> str:
        return str(self)

    @property
    def http_status_code(self) -> int:
        return self.type.value.http_status_code()

    @property
    def description(self) -> str:
        return self.type.value.description()

    @property
    def code(self) -> int:
        return self.type.value.code()

    def to_json(self) -> dict:
        error: ExecutionErrorTemplate = self.type.value
        return {
            "Code": error.code(),
            "Description": error.description(),
            "Message": self.message,
            "Details": self.details if self.details else dict(),
            "HTTPStatusCode": error.http_status_code()
        }

    @staticmethod
    def wrap(e: Exception) -> ExecutionError:
        e_type, e_val, e_tb = sys.exc_info()
        return ExecutionError(t=ErrorType.INTERNAL,
                              message="An exception occurred.",
                              details={"e_type": type(e).__name__,
                                       "message": str(e),
                                       "stacktrace": traceback.format_exception(e_type, e_val, e_tb)})
