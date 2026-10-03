from wattson_core.ai.identity import WattsonIdentity


def test_wattson_identity_has_name():
    identity = WattsonIdentity()

    assert identity.name == "Wattson"


def test_wattson_identity_has_purpose():
    identity = WattsonIdentity()

    assert identity.purpose == "assistir o usuário"


def test_wattson_identity_has_limits():
    identity = WattsonIdentity()

    assert isinstance(identity.limits, list)


def test_wattson_identity_has_defined_limits():
    identity = WattsonIdentity()

    assert "não inventar informações" in identity.limits


def test_wattson_identity_has_characteristics():
    identity = WattsonIdentity()

    assert isinstance(identity.characteristics, list)


def test_wattson_identity_is_modular():
    identity = WattsonIdentity()

    assert "modular" in identity.characteristics
