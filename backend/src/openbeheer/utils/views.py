from django.conf import settings
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.views.generic.base import TemplateView


class RootView(TemplateView):
    """View for the root of the backend.

    If the script backend/bin/setup_e2e.sh has been run, the frontend
    has been built and the staticfiles have been symlinked into the backend
    folder. We then use the template produced by the frontend (index.html).

    Otherwise we use the default master.html.
    """

    def get_template_names(self) -> list[str]:
        if not getattr(settings, "E2E_TESTS", False):
            return ["master.html"]

        try:
            get_template("index.html")
        except TemplateDoesNotExist:
            return ["master.html"]

        return ["index.html"]
