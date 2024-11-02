# pybadges

## What is this ?

Just a very quick and dirty Python script to generate badges for
conference attendees and speakers.

It requires a `CSV` file as input, with the following format:

    frontside,backside,firstname,lastname,company,logo
    frontside,backside,firstname,lastname,company,logo
    frontside,backside,firstname,lastname,company,logo
    frontside,backside,firstname,lastname,company,logo

`lastname`, `company` and `logo` are optional. `logo` is the path to the company
logo. `frontside`  and `backside` are the background images to use on each
badge. The images are resized if required.

Typical usage:

    poetry run python pybadges.py -c config.toml -i input.csv -o output.pdf

Use `badges.toml` as an example of config.

## License

Licensed under the WTFPL license, http://sam.zoy.org/wtfpl/
