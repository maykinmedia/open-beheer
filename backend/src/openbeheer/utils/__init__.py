default_app_config = "openbeheer.utils.apps.UtilsConfig"


def camelize(s: str) -> str:
    if "." in s:
        head, *tail = s.split(".")
        return f"{head}.{'.'.join(map(camelize, tail))}"
    return "".join(part.title() if n else part for n, part in enumerate(s.split("_")))
