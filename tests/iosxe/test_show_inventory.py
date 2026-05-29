import inspect

import pytest

from yenie_parser.iosxe import _genie_show_inventory as parsers


def _value_at(data: dict, path: tuple[object, ...]) -> object:
    current = data
    for key in path:
        current = current[key]
    return current


INVENTORY_OUTPUT = (
    'NAME: "Chassis", DESCR: "Cisco Catalyst Series C9500X-28C8D Chassis"\n'
    "PID: C9500X-28C8D      , VID: V00  , SN: FDO25030SLN\n"
    "OID: 1.3.6.1.4.1.9.12.3.1.3.2421"
)


INVENTORY_CASES = {
    "ShowInventoryRaw": (
        {},
        INVENTORY_OUTPUT,
        (
            (("name", "Chassis", "description"), "Cisco Catalyst Series C9500X-28C8D Chassis"),
            (("name", "Chassis", "pid"), "C9500X-28C8D"),
            (("name", "Chassis", "vid"), "V00"),
            (("name", "Chassis", "sn"), "FDO25030SLN"),
        ),
    ),
    "ShowInventoryOID": (
        {},
        INVENTORY_OUTPUT,
        ((("name", "Chassis", "oid"), "1.3.6.1.4.1.9.12.3.1.3.2421"),),
    ),
    "ShowInventoryName": (
        {"name": "Chassis"},
        INVENTORY_OUTPUT,
        ((("name", "Chassis", "pid"), "C9500X-28C8D"),),
    ),
}


@pytest.mark.parametrize("class_name", sorted(INVENTORY_CASES))
def test_inventory_parser_class(class_name: str) -> None:
    kwargs, output, expectations = INVENTORY_CASES[class_name]
    parser = getattr(parsers, class_name)()

    parsed = parser.cli(output=output, **kwargs)

    assert parsed
    for path, expected in expectations:
        assert _value_at(parsed, path) == expected


def test_all_effective_inventory_parser_classes_are_covered() -> None:
    parser_classes = {
        name
        for name, parser_class in inspect.getmembers(parsers, inspect.isclass)
        if parser_class.__module__ == parsers.__name__ and hasattr(parser_class, "cli_command")
    }

    assert parser_classes == set(INVENTORY_CASES)


def test_inventory_empty_output_is_permissive() -> None:
    assert parsers.ShowInventoryRaw().cli(output="") == {}
