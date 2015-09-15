Oxfam lookup
============

Provides postcode or address to representative lookup for UK and Australia.

    /postcode/(UK|AU)/<postcode>
    /address/(UK|AU)/<addressstring>

Installation
------------

Install the dependencies of the application:

    $ pip install -r requirements.txt

A libffi-dev system package might be needed in order for the cryptography
module to install.

Copy `conf/general.yml-example` to `conf/general.yml`, and if you want address
lookup, put a Bing API key in it.

Run `bin/fetch-data` to fetch data from EveryPolitician. You probably want to
run this on cron, there's an example crontab in `conf/crontab.ugly`.

For running the tests:

    $ pip install -r requirements-test.txt
    $ bin/run-tests

For development, install a WSGI server with:

    $ pip install -r requirements-dev.txt
