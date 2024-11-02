import dataclasses
import io
import tomllib
import typing as t

import jsonschema


def mm2dots(dpi: int, mm: float) -> int:
    """Convert millimeters to dots."""
    return round(mm / 25.4 * dpi)


class ConfigError(ValueError):
    pass


@dataclasses.dataclass
class Box:
    height: int
    width: int

    def size(self) -> tuple[int, int]:
        return (self.width, self.height)

    @classmethod
    def from_dict(cls, dpi: int, dct: dict[str, t.Any]) -> t.Self:
        dct["height"] = mm2dots(dpi, dct["height"])
        dct["width"] = mm2dots(dpi, dct["width"])
        return cls(**dct)


@dataclasses.dataclass
class TextBox(Box):
    vertical_offset: int
    font_name: str
    font_size: int
    color: str

    def color_as_int(self) -> int:
        return int(self.color, base=0)

    @classmethod
    def from_dict(cls, dpi: int, dct: dict[str, t.Any]) -> t.Self:
        dct["height"] = mm2dots(dpi, dct["height"])
        dct["width"] = mm2dots(dpi, dct["width"])
        dct["vertical_offset"] = mm2dots(dpi, dct["vertical_offset"])
        return cls(**dct)


class Config:
    def __init__(
        self,
        dpi: int,
        inner_margin: float,
        resize: bool,
        double_sided: bool,
        page: Box,
        badge: Box,
        name: TextBox,
        lastname: TextBox,
        group: TextBox,
    ):
        self.dpi = dpi
        self.inner_margin = mm2dots(dpi, inner_margin)
        self.resize = resize
        self.double_sided = double_sided
        self.page = page
        self.badge = badge

        self.name = name
        self.lastname = lastname
        self.group = group

    @classmethod
    def from_dict(cls, dct: dict[str, t.Any]) -> t.Self:
        dpi = dct["dpi"]
        page = Box.from_dict(dpi, dct["page"])
        badge = Box.from_dict(dpi, dct["badge"])
        name = TextBox.from_dict(dpi, dct["name"])
        lastname = TextBox.from_dict(dpi, dct["lastname"])
        group = TextBox.from_dict(dpi, dct["group"])

        return cls(
            dpi=dpi,
            inner_margin=dct["inner_margin"],
            resize=dct["resize"],
            double_sided=dct["double_sided"],
            page=page,
            badge=badge,
            name=name,
            lastname=lastname,
            group=group,
        )

    @classmethod
    def from_toml(cls, fp: io.BytesIO) -> t.Self:
        dct = tomllib.load(fp)
        try:
            jsonschema.validate(instance=dct, schema=_schema)
        except jsonschema.ValidationError as e:
            raise ConfigError(e)

        return cls.from_dict(dct)


_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "dpi": {"type": "integer", "minimum": 1},
        "inner_margin": {"type": "number", "minimum": 0},
        "resize": {"type": "boolean"},
        "double_sided": {"type": "boolean"},
        "name": {"$ref": "#/$defs/textbox"},
        "lastname": {"$ref": "#/$defs/textbox"},
        "group": {"$ref": "#/$defs/textbox"},
        "page": {"$ref": "#/$defs/box"},
        "badge": {"$ref": "#/$defs/box"},
    },
    "$defs": {
        "box": {
            "type": "object",
            "properties": {
                "height": {"type": "number", "minimum": 0.1},
                "width": {"type": "number", "minimum": 0.1},
            },
            "required": ["height", "width"],
        },
        "textbox": {
            "type": "object",
            "properties": {
                "height": {"type": "number", "minimum": 0.1},
                "width": {"type": "number", "minimum": 0.1},
                "vertical_offset": {"type": "number", "minimum": 0},
                "font_name": {"type": "string"},
                "font_size": {"type": "number", "minimum": 1},
                "color": {"type": "string", "pattern": "^0x[0-9A-Fa-f]{6}$"},
            },
            "required": [
                "height",
                "width",
                "vertical_offset",
                "font_name",
                "font_size",
                "color",
            ],
        },
    },
    "required": [
        "dpi",
        "inner_margin",
        "resize",
        "double_sided",
        "page",
        "badge",
        "name",
        "lastname",
        "group",
    ],
}
