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
class DrawableBox(Box):
    vertical_offset: int

    @classmethod
    def from_dict(cls, dpi: int, dct: dict[str, t.Any]) -> t.Self:
        dct["height"] = mm2dots(dpi, dct["height"])
        dct["width"] = mm2dots(dpi, dct["width"])
        dct["vertical_offset"] = mm2dots(dpi, dct["vertical_offset"])
        return cls(**dct)


@dataclasses.dataclass
class TextBox(DrawableBox):
    font_name: str
    font_size: int
    color: str
    vertical_offset_if_null: int = 0

    def color_as_int(self) -> int:
        return int(self.color, base=0)

    @classmethod
    def from_dict(cls, dpi: int, dct: dict[str, t.Any]) -> t.Self:
        dct["height"] = mm2dots(dpi, dct["height"])
        dct["width"] = mm2dots(dpi, dct["width"])
        dct["vertical_offset"] = mm2dots(dpi, dct["vertical_offset"])
        dct["vertical_offset_if_null"] = mm2dots(
            dpi, dct.get("vertical_offset_if_null", 0)
        )
        return cls(**dct)


class Config:
    def __init__(
        self,
        dpi: int,
        inner_margin: float,
        resize: bool,
        frontside_only: bool,
        double_sided: bool,
        page: Box,
        badge: Box,
        name: TextBox,
        lastname: TextBox,
        group: TextBox,
        logo: DrawableBox,
    ):
        self.dpi = dpi
        self.inner_margin = mm2dots(dpi, inner_margin)
        self.resize = resize
        self.frontside_only = frontside_only
        self.double_sided = double_sided
        self.page = page
        self.badge = badge

        self.name = name
        self.lastname = lastname
        self.group = group
        self.logo = logo

    @classmethod
    def from_dict(cls, dct: dict[str, t.Any]) -> t.Self:
        dpi = dct["dpi"]
        page = Box.from_dict(dpi, dct["page"])
        badge = Box.from_dict(dpi, dct["badge"])
        name = TextBox.from_dict(dpi, dct["name"])
        lastname = TextBox.from_dict(dpi, dct["lastname"])
        group = TextBox.from_dict(dpi, dct["group"])
        logo = DrawableBox.from_dict(dpi, dct["logo"])

        return cls(
            dpi=dpi,
            inner_margin=dct["inner_margin"],
            resize=dct["resize"],
            frontside_only=dct["frontside_only"],
            double_sided=dct["double_sided"],
            page=page,
            badge=badge,
            name=name,
            lastname=lastname,
            group=group,
            logo=logo,
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
        "frontside_only": {"type": "boolean"},
        "double_sided": {"type": "boolean"},
        "page": {"$ref": "#/$defs/box"},
        "badge": {"$ref": "#/$defs/box"},
        "name": {"$ref": "#/$defs/textbox"},
        "lastname": {"$ref": "#/$defs/textbox"},
        "group": {"$ref": "#/$defs/textbox"},
        "logo": {"$ref": "#/$defs/drawablebox"},
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
        "drawablebox": {
            "type": "object",
            "properties": {
                "height": {"type": "number", "minimum": 0.1},
                "width": {"type": "number", "minimum": 0.1},
                "vertical_offset": {"type": "number", "minimum": 0},
            },
            "required": [
                "height",
                "width",
                "vertical_offset",
            ],
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
                "vertical_offset_if_null": {"type": "number"},
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
        "frontside_only",
        "double_sided",
        "page",
        "badge",
        "name",
        "lastname",
        "group",
    ],
}
