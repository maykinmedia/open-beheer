from .runner import HealthChecksRunner
from .types import HealthCheckSerialisedResult


def run_health_checks(
    with_traceback: bool = False,
) -> list[HealthCheckSerialisedResult]:
    runner = HealthChecksRunner()

    results = runner.run_checks()
    serialised_results = [result.serialise(with_traceback) for result in results]
    return serialised_results
