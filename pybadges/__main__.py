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
import logging.config
import pathlib

from pybadges import Config
from pybadges import Person
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
parser.add_argument(
    "-v",
    "--verbose",
    action="count",
)

args = parser.parse_args()

level = "WARNING"
if args.verbose == 1:
    level = "INFO"
elif args.verbose > 1:
    level = "DEBUG"

logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                "format": "[%(levelname)8s] %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "simple",
            },
        },
        "loggers": {
            "pybadges": {
                "level": level,
                "handlers": ["console"],
                "propagate": False,
            },
            "root": {
                "level": "WARNING",
                "handlers": ["console"],
            },
        },
    }
)

config = Config.from_toml(args.config)
printer = Printer(config, directory=args.directory)

printer.make_document(Person.many_from_csv(args.input), args.output)
