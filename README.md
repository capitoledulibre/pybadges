# pybadges

## What is this ?

Just a very quick and dirty Python script to generate badges for
conference attendees and speakers.

It requires a `CSV` file as input, with the following format:

    firstname lastname,company,role
    firstname lastname,company,role
    firstname lastname,company,role
    firstname lastname,company,role

Typically `role` can be `speaker`, `attendee`, `organizer` or something
like that.

It also requires a background image used for the badges.

Typical usage:

    ./pybadges -i input.csv -o output.pdf -b background.png


## License

Licensed under the WTFPL license, http://sam.zoy.org/wtfpl/
