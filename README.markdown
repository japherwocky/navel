NAVEL
=====

A fuzzy search engine


Dependencies
------------

First off, you'll need a newish version of python, and an instance of redis listening to localhost (the default settings work great).

If you're on an ubuntu-ish system, you can run something like `sudo apt-get install redis-server`, and things will probably Just Work.  Note though, if you have redis running on your system already, this code will try to wipe out databases 0 through 2!!  

(DONT RUN THIS AGAINST AN EXISTING REDIS INSTANCE, YOU WILL LOSE YOUR DATA)
=========================================================================


This uses a few awesome python libraries:

* [redis](https://github.com/andymccurdy/redis-py)
* [stemming](http://pypi.python.org/pypi/stemming/1.0)
* [fuzzy](http://pypi.python.org/pypi/Fuzzy/)
* [twitter](http://mike.verdone.ca/twitter/)

`pip install` works great for all of these.


There's also a copy of tornado in this repository.

Go time
-------

So once you've got those set up, twitter will add a few command line tools that we'll use to get some data to index.

Run something like `twitter-archiver -o japherwocky`, where japherwocky is your twitter handle.  On the first pass, the -o option will set up and store OAuth credentials, and when you're done you'll have a file named after your particular twitter handle.  In this case, I've got a file named "japherwocky" full of all my tweets.

To build the index, launch navel.py with the `--index` option pointing to the file twitter-archiver just made.  To see some tweets as it goes, use `--logging=debug`, eg:

`python navel.py --index=./japherwocky --logging=debug`

When it's finished, you'll have a webserver running on port 8001, and some indexes built up in redis.  To check it out, go to [localhost:8001](http://localhost:8001/), and try searching for some things!  The "STEMS" button will query against an index of stemmed words, and the "FUZZ" button will query against an index of metaphones.  As you run queries, the terminal running the webserver will also give some insight into what's going on under the hood, if you used --logging=debug.


Questions
---------

This was written pretty quickly and probably isn't all that great.  Feel free to send questions my way: either via github, or give me a ping on [twitter](http://twitter.com/japherwocky)
