# pybadges

A tool to generates badges for conference attendees and speakers.

Features:
* Print front and back sides
* Group badges per sheet (eg. four A6 badges on one A4 sheet)
* Insert a company logo

## Installation

```sh
poetry install
```

## Usage

It requires a TOML file for configuration and a CSV file from the data. The
configuration file should follow the format of the example called `badges.toml`.
The CSV file should be in the format

    frontside,backside,firstname,lastname,group,logo,email

`lastname`, `group`, `logo` and `email` are optional. `logo` is the path to the company
logo. `frontside`  and `backside` are the paths to the background images to use
on each badge. The images are resized if required.

Typical usage:
```sh
poetry run python -m pybadges -c config.toml -i input.csv -o output.pdf
```

## Test

Run tests with:

```shell
python -m unittest tests/pybadges_tests.py
```

### Add dependencies

If needed, install dependencies with:

```shell
pip install -r requirements.txt
```

## License

Licensed under the Apache-2.0 license, https://www.apache.org/licenses/LICENSE-2.0.html
