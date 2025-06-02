from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal, NotRequired, TypedDict


@dataclass
class HealthCheckError:
    code: str
    message: str
    severity: Literal["error", "warning", "info"]
    exc: str = ""


@dataclass
class HealthCheckResult:
    check: "HealthCheck"
    success: bool
    errors: list[HealthCheckError] | None = None

    def serialise(self, with_traceback: bool = False) -> "HealthCheckSerialisedResult":
        result: HealthCheckSerialisedResult = {
            "check": self.check.get_name(),
            "success": self.success,
            "errors": [],
        }
        for error in self.errors or []:
            serialised_error: HealthCheckSerialisedError = {
                "message": error.message,
            }
            if with_traceback:
                serialised_error["traceback"] = error.exc
            result["errors"].append(serialised_error)

        return result


class HealthCheck(ABC):
    def get_name(self):
        return self.__class__.__name__

    @abstractmethod
    def run(self) -> HealthCheckResult: ...


class HealthCheckSerialisedError(TypedDict):
    message: str
    traceback: NotRequired[str]


class HealthCheckSerialisedResult(TypedDict):
    check: str
    success: bool
    errors: list[HealthCheckSerialisedError]
