import dataclasses
import io
import tomllib
import typing as t


DPI = 300


def mm2dots(mm: float) -> int:
    """Convert millimeters to dots."""
    return round(mm / 25.4 * DPI)


class ConfigError(ValueError):
    pass


@dataclasses.dataclass
class Box:
    height: int
    width: int

    def size(self) -> tuple[int, int]:
        return (self.width, self.height)

    @classmethod
    def from_dict(cls, dct: dict[str, t.Any]) -> t.Self:
        try:
            dct["height"] = mm2dots(dct["height"])
            dct["width"] = mm2dots(dct["width"])
            return cls(**dct)
        except KeyError as e:
            raise ConfigError(f"ConfigError: missing key '{e}'")
        except TypeError:
            # TODO
            raise


@dataclasses.dataclass
class TextBox(Box):
    vertical_offset: int
    font_name: str
    font_size: int
    color: str

    def color_as_int(self) -> int:
        return int(self.color, base=0)

    @classmethod
    def from_dict(cls, dct: dict[str, t.Any]) -> t.Self:
        try:
            dct["height"] = mm2dots(dct["height"])
            dct["width"] = mm2dots(dct["width"])
            dct["vertical_offset"] = mm2dots(dct["vertical_offset"])
            return cls(**dct)
        except KeyError as e:
            raise ConfigError(f"ConfigError: missing key '{e}'")
        except TypeError:
            # TODO
            raise


class Config:
    def __init__(
        self,
        dpi: int,
        inner_margin: float,
        page: Box,
        badge: Box,
        name: TextBox,
        lastname: TextBox,
        group: TextBox,
    ):
        self.dpi = dpi
        self.inner_margin = mm2dots(inner_margin)
        self.page = page
        self.badge = badge

        self.name = name
        self.lastname = lastname
        self.group = group

    @classmethod
    def from_dict(cls, dct: dict[str, t.Any]) -> t.Self:
        try:
            page = Box.from_dict(dct["page"])
            badge = Box.from_dict(dct["badge"])
            name = TextBox.from_dict(dct["name"])
            lastname = TextBox.from_dict(dct["lastname"])
            group = TextBox.from_dict(dct["group"])

            return cls(
                dpi=dct["dpi"],
                inner_margin=dct["inner_margin"],
                page=page,
                badge=badge,
                name=name,
                lastname=lastname,
                group=group,
            )
        except KeyError as e:
            raise ConfigError(f"ConfigError: missing key '{e}'")

    @classmethod
    def from_toml(cls, fp: io.BytesIO) -> t.Self:
        dct = tomllib.load(fp)
        return cls.from_dict(dct)
