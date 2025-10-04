# Copyright 2025 Toulibre
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import argparse
import pathlib

from pybadges import Config
from pybadges import parse_persons
from pybadges import Printer

parser = argparse.ArgumentParser()
parser.add_argument(
    "-c",
    "--config",
    type=argparse.FileType("rb"),
    metavar="TOML",
    required=True,
    help="config toml file. See README.md for format",
)
parser.add_argument(
    "-C",
    "--directory",
    type=pathlib.Path,
    metavar="DIR",
    default=pathlib.Path.cwd(),
    help="directory to load images from",
)
parser.add_argument(
    "-i",
    "--input",
    type=argparse.FileType("r"),
    metavar="CSV",
    required=True,
    help="input csv file. See README.md for format",
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
printer = Printer(config, directory=args.directory)

printer.make_document(parse_persons(args.input), args.output)
