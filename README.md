# pybadges

A tool to generates badges for conference attendees and speakers.

## Installation

```sh
poetry install
```

## Usage

It requires a TOML file for configuration and a CSV file from the data. The
configuration file should follow the format of the example called `badges.toml`.
The CSV file should be in the format

    frontside,backside,firstname,lastname,group,logo

`lastname`, `group` and `logo` are optional. `logo` is the path to the company
logo. `frontside`  and `backside` are the paths to the background images to use
on each badge. The images are resized if required.

Typical usage:
```sh
poetry run python pybadges.py -c config.toml -i input.csv -o output.pdf
```

## License

Licensed under the WTFPL license, http://sam.zoy.org/wtfpl/
