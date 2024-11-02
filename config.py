import dataclasses
import io
import tomllib
import typing as t


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
        try:
            dct["height"] = mm2dots(dpi, dct["height"])
            dct["width"] = mm2dots(dpi, dct["width"])
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
    def from_dict(cls, dpi: int, dct: dict[str, t.Any]) -> t.Self:
        try:
            dct["height"] = mm2dots(dpi, dct["height"])
            dct["width"] = mm2dots(dpi, dct["width"])
            dct["vertical_offset"] = mm2dots(dpi, dct["vertical_offset"])
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
        try:
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
        except KeyError as e:
            raise ConfigError(f"ConfigError: missing key '{e}'")

    @classmethod
    def from_toml(cls, fp: io.BytesIO) -> t.Self:
        dct = tomllib.load(fp)
        return cls.from_dict(dct)
