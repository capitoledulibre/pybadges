import argparse

from pybadges import Config
from pybadges import make_document
from pybadges import parse_persons

parser = argparse.ArgumentParser()
parser.add_argument(
    "-c",
    "--config",
    type=argparse.FileType("rb"),
    metavar="TOML",
    required=True,
    help="Config toml file. See README.md for format.",
)
parser.add_argument(
    "-i",
    "--input",
    type=argparse.FileType("r"),
    metavar="CSV",
    required=True,
    help="Input csv file. See README.md for format.",
)
parser.add_argument(
    "-o",
    "--output",
    type=argparse.FileType("wb"),
    metavar="PDF",
    required=True,
    help="output pdf file",
)

args = parser.parse_args()
config = Config.from_toml(args.config)
make_document(config, parse_persons(args.input), args.output)
