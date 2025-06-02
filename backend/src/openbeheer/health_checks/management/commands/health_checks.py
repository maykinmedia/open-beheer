from django.core.management.base import BaseCommand

from ...utils import run_health_checks


class Command(BaseCommand):
    help = "Run the health checks for Open Beheer"

    def add_arguments(self, parser):
        parser.add_argument(
            "--with-traceback",
            action="store_true",
            help="When available, print tracebacks for errors.",
        )

    def handle(self, *args, **options):
        results = run_health_checks(with_traceback=options["with_traceback"])

        message = "\n{check}: {status}"

        for result in results:
            style_fn = self.style.SUCCESS if result["success"] else self.style.ERROR

            self.stdout.write(
                style_fn(
                    message.format(
                        check=result["check"],
                        status="success" if result["success"] else "fail",
                    )
                )
            )

            for error in result["errors"]:
                self.stdout.write(error["message"])
                if traceback := error.get("traceback"):
                    self.stdout.write(traceback)
