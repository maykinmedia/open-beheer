from msgspec import UNSET, Struct, UnsetType


class OIDCInfo(Struct):
    enabled: bool
    login_url: str | UnsetType = UNSET

    def __post_init__(self):
        if not self.enabled:
            self.login_url = UNSET
