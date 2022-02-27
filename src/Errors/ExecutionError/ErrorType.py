
from enum import Enum
from abc import ABC, abstractmethod


class ExecutionErrorTemplate(ABC):

    @classmethod
    @abstractmethod
    def description(cls) -> str: ...

    @classmethod
    @abstractmethod
    def http_status_code(cls) -> int: ...

    @classmethod
    @abstractmethod
    def code(cls) -> int: ...


class ExecutionErrorTemplate_BadInput(ExecutionErrorTemplate, ABC):

    @classmethod
    def http_status_code(cls) -> int:
        return 400


class ExecutionErrorTemplate_Internal(ExecutionErrorTemplate, ABC):

    @classmethod
    def http_status_code(cls) -> int:
        return 500


class ExecutionErrorTemplate_Missing(ExecutionErrorTemplate, ABC):

    @classmethod
    def http_status_code(cls) -> int:
        return 404


#


class ExecutionError_Internal(ExecutionErrorTemplate_Internal):
    @classmethod
    def description(cls) -> str:
        return "INTERNAL ERROR"

    @classmethod
    def code(cls) -> int:
        return 198


class ExecutionError_NoPathFound(ExecutionErrorTemplate_Missing):

    @classmethod
    def description(cls) -> str:
        return "NO PATH FOUND"

    @classmethod
    def code(cls) -> int:
        return 101


class ExecutionError_Unknown(ExecutionErrorTemplate_Internal):
    @classmethod
    def description(cls) -> str:
        return "UNKNOWN ERROR"

    @classmethod
    def code(cls) -> int:
        return 199


class ExecutionError_BadRequest(ExecutionErrorTemplate_BadInput):

    @classmethod
    def description(cls) -> str:
        return "BAD REQUEST"

    @classmethod
    def code(cls) -> int:
        return 120


class ErrorType(Enum):
    INTERNAL = ExecutionError_Internal
    UNKNOWN_ERROR = ExecutionError_Unknown
    BAD_REQUEST = ExecutionError_BadRequest
    NO_PATH_FOUND = ExecutionError_NoPathFound
