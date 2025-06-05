from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal, NotRequired, Sequence, TypedDict

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
    errors: Sequence[HealthCheckError] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return not bool(self.errors)

    def serialise(self, with_traceback: bool = False) -> "HealthCheckSerialisedResult":
        result: HealthCheckSerialisedResult = {
            "check": repr(self.check),
            "success": self.success,
            "errors": [],
        }
        for error in self.errors:
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
