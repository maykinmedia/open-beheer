from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, NotRequired, TypedDict

if TYPE_CHECKING:
    from .checks import HealthCheck


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
                "code": error.code,
                "severity": error.severity,
            }
            if with_traceback:
                serialised_error["traceback"] = error.exc
            result["errors"].append(serialised_error)

        return result


class HealthCheckSerialisedError(TypedDict):
    message: str
    traceback: NotRequired[str]
    code: str
    severity: Literal["error", "warning", "info"]


class HealthCheckSerialisedResult(TypedDict):
    check: str
    success: bool
    errors: list[HealthCheckSerialisedError]
