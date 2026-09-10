"""F1 — the (port, variant) registry. Unit-tier ACs."""

from __future__ import annotations

import threading

import pytest

from src.shared.registry import (
    ConcurrentRegistryAccess,
    DuplicateRegistration,
    IncompleteRegistry,
    InvalidKey,
    Registry,
    UnknownVariant,
)


class Counter:
    """A factory that records how many times it was invoked."""

    def __init__(self) -> None:
        self.calls = 0

    def __call__(self):
        self.calls += 1
        return object()


def test_ac_f1_1_duplicate_registration_is_loud():
    """AC-F1.1 — a duplicate (port, variant) raises and leaves the first entry intact."""
    r = Registry()
    r.register("greeter", "polite", lambda: "first", version="1.0.0")
    with pytest.raises(DuplicateRegistration):
        r.register("greeter", "polite", lambda: "second", version="2.0.0")
    assert r.resolve("greeter", "polite") == "first"
    assert r.provenance("greeter", "polite").version == "1.0.0"


def test_ac_f1_2_unknown_variant_names_the_alternatives():
    """AC-F1.2 — UnknownVariant lists the registered variants FOR THAT PORT."""
    r = Registry()
    r.register("greeter", "polite", lambda: 1, version="1.0.0")
    r.register("greeter", "terse", lambda: 2, version="1.0.0")
    r.register("doubler", "mul", lambda: 3, version="1.0.0")
    with pytest.raises(UnknownVariant) as exc:
        r.resolve("greeter", "poilte")
    msg = str(exc.value)
    assert "polite" in msg and "terse" in msg
    assert "mul" not in msg, "must list only the variants of the port asked for"


def test_ac_f1_3_factories_not_instances():
    """AC-F1.3 — registration does not invoke the factory; the first resolve does."""
    f = Counter()
    r = Registry()
    r.register("greeter", "polite", f, version="1.0.0")
    assert f.calls == 0
    r.resolve("greeter", "polite")
    assert f.calls == 1


def test_ac_f1_4_coverage_fails_at_boot_naming_every_missing_port():
    """AC-F1.4 — IncompleteRegistry names EVERY missing port, not just the first."""
    r = Registry()
    r.register("greeter", "polite", lambda: 1, version="1.0.0")
    with pytest.raises(IncompleteRegistry) as exc:
        r.validate_coverage(required_ports=("greeter", "doubler", "pricer"))
    assert set(exc.value.missing) == {"doubler", "pricer"}


def test_ac_f1_5_closed_variant_set_attempts_no_import():
    """AC-F1.5 — resolving an unregistered variant imports nothing (QR-7)."""
    import builtins

    r = Registry()
    r.register("greeter", "polite", lambda: 1, version="1.0.0")

    attempted: list[str] = []
    real_import = builtins.__import__

    def spy(name, *a, **k):
        attempted.append(name)
        return real_import(name, *a, **k)

    builtins.__import__ = spy
    try:
        with pytest.raises(UnknownVariant):
            r.resolve("greeter", "from_the_internet")
    finally:
        builtins.__import__ = real_import
    assert attempted == [], f"resolve attempted imports: {attempted}"


def test_ac_f1_6_caching_is_scoped_to_the_registry_instance():
    """AC-F1.6 — one factory call per (port, variant) per Registry; a NEW Registry rebuilds."""
    f = Counter()
    r = Registry()
    r.register("greeter", "polite", f, version="1.0.0")
    first = r.resolve("greeter", "polite")
    assert r.resolve("greeter", "polite") is first
    assert r.resolve("greeter", "polite") is first
    assert f.calls == 1

    r2 = Registry()
    r2.register("greeter", "polite", f, version="1.0.0")
    second = r2.resolve("greeter", "polite")
    assert f.calls == 2, "a second Registry is a second run scope (D1)"
    assert second is not first


def test_ac_f1_8_provenance_is_entry_derived_not_object_reported():
    """AC-F1.8 — Provenance comes from the ENTRY, never from the resolved object."""

    class Liar:
        port = "something_else"
        variant = "mine"
        version = "9.9.9"
        experimental = False

    r = Registry()
    r.register("greeter", "polite", Liar, version="1.0.0")
    p = r.provenance("greeter", "polite")
    assert (p.port, p.variant, p.version, p.experimental) == ("greeter", "polite", "1.0.0", False)
    with pytest.raises((AttributeError, TypeError)):
        p.version = "0.0.1"  # frozen + slots: immutable by construction


def test_ac_f1_11_experimental_flag_propagates():
    """AC-F1.11 — experimental=True surfaces on Provenance (PG-2)."""
    r = Registry()
    r.register("greeter", "lab", lambda: 1, version="0.1.0", experimental=True)
    assert r.provenance("greeter", "lab").experimental is True
    assert r.resolve_with_provenance("greeter", "lab")[1].experimental is True


def test_ac_f1_12_thin_ports_are_warned_not_failed():
    """AC-F1.12 — a port with <2 real variants is REPORTED; the build does not fail."""
    r = Registry()
    r.register("greeter", "polite", lambda: 1, version="1.0.0")
    r.register("doubler", "mul", lambda: 2, version="1.0.0")
    r.register("doubler", "shift", lambda: 3, version="1.0.0")
    report = r.validate_coverage(required_ports=("greeter", "doubler"))
    assert report.thin_ports == ("greeter",)
    assert report.missing == ()


@pytest.mark.parametrize(
    "port,variant",
    [("", "polite"), ("greeter", ""), ("Greeter", "polite"), ("greeter", "po lite"),
     ("greeter", "polite!"), ("green-ter", "polite")],
)
def test_ac_f1_15_invalid_keys_are_refused(port, variant):
    """AC-F1.15 — CT-1.1's key rules are enforced, not merely stated.

    ⚠ A key "appears in provenance records that outlive the code" (CT-1.1), so a
    mixed-case or whitespace-bearing name is unfixable once written to a trace.
    """
    r = Registry()
    with pytest.raises(InvalidKey):
        r.register(port, variant, lambda: 1, version="1.0.0")


def test_ac_f1_15_names_the_offending_field():
    """AC-F1.15 — the error says WHICH field was wrong."""
    r = Registry()
    with pytest.raises(InvalidKey) as exc:
        r.register("greeter", "Polite", lambda: 1, version="1.0.0")
    assert exc.value.field == "variant"


def test_ac_f1_12_a_fixture_variant_does_not_count_as_earned_abstraction():
    """AC-F1.12 (A1) — a stand-in must not silence the thin-port warning."""
    r = Registry()
    r.register("greeter", "polite", lambda: 1, version="1.0.0")
    r.register("greeter", "stub", lambda: 2, version="0.0.0", fixture=True)
    report = r.validate_coverage(required_ports=("greeter",))
    assert report.thin_ports == ("greeter",), "a fixture is not a second implementation"


def test_ac_f1_12_an_experimental_variant_DOES_count():
    """AC-F1.12 (A1) — experimental is real code on trial; it is not a stand-in."""
    r = Registry()
    r.register("greeter", "polite", lambda: 1, version="1.0.0")
    r.register("greeter", "lab", lambda: 2, version="0.1.0", experimental=True)
    assert r.validate_coverage(required_ports=("greeter",)).thin_ports == ()


def test_ac_f1_14_resolve_from_another_thread_is_refused():
    """AC-F1.14 — cross-thread resolve raises ConcurrentRegistryAccess naming both threads (D3)."""
    r = Registry()
    r.register("greeter", "polite", lambda: 1, version="1.0.0")
    captured: list[BaseException] = []

    def worker():
        try:
            r.resolve("greeter", "polite")
        except BaseException as e:  # noqa: BLE001 — the assertion is the point
            captured.append(e)

    t = threading.Thread(target=worker, name="intruder")
    t.start()
    t.join()
    assert captured and isinstance(captured[0], ConcurrentRegistryAccess)
    assert "intruder" in str(captured[0])
    assert threading.current_thread().name in str(captured[0])
