pytunia
========
pytunia is a platform for source code quality testing/continuous integration based on the [dirt](http://github.com/mastbaum/dirt) package.

In addition to testing compilation on various platform (a la buildbot), it can perform functional tests (scripted in Python), static tests, or any other task describable in a Python module. The provided tasks assume git as the VCS and scons as the build system, but these are easily modified for your application. Branch "svn" provides an SVN-compatible version.

These tasks are run on a grid of slave nodes, which need not share any resources, have zero state, and run no client-side software except a Python interpreter.

Results of all tests are stored in a CouchDB database and available to users via a web interface.

Getting Started
===============
Dependencies
------------

* dirt (http://github.com/mastbaum/dirt)
* kanso (http://kansojs.org)

Installation
------------

1. Get pytunia: `$ git clone http://github.com/mastbaum/pytunia`
2. Modify `settings.py` as necessary
3. Create the web application: `$ cd pytunia/web && ./egret push pytunia & cd ..`
4. Add some slave nodes: `$ dirt updatenodes <node1.yoursite.com> <foo.bar.net> ...`
5. Start the server: `$ dirt serve`

Viewing results
---------------

To see test output, go to the project URL, which defaults to http://localhost:5984/pytunia/_design/pytunia/index.html.

Note: this is the base URL for the entire site. Using `mod_rewrite` to clip this down to `/your-project` is recommended.

Adding revisions
----------------

pytunia deals with revisions (records) and the set of tests to be run for each (tasks). POSTing of record documents and the associated task documents should be done in a post-commit hook on your version control system. A post-commit hook for SVN is provided in `bin` on `pytunia/svn`. For use with github, check out [repoman](http://github.com/mastbaum/repoman). The format for the pytunia document types are as follows.

#### Record (revision) ####

    {
        "_id": "[revision name or number]",
        "type": "record",
        "description": "[commit message]",
        "created": [creation time (seconds since epoch)]
    }

Example:

    {
        "_id": "r123",
        "type": "record",
        "description": "this is revision one two three",
        "created": 1315347385
    }

#### `build` and `cppcheck` Tasks ####

    {
        "_id": [unique uuid],
        "type": "task",
        "name": "cppcheck",
        "created": [creation time (seconds since epoch)],
        "kwargs": {
            "sha": [git revision id to test],
            "git_url": [git repository URL]
        },
        "platform": "[target platform (build only)]"
        "record_id": "[associated record id]"
    }

Example:

    {
        "_id": "8bc2d24cadd9ac26fbe2279fad28b680",
        "type": "task",
        "name": "cppcheck",
        "created": 1315347385,
        "platform": "linux",
        "kwargs": {
            "revnumber": "89e7cfd548133f0cab18bebc74a7c13eec713bc3",
            "git_url": "git@github.com:mastbaum/pytunia"
        },
        "platform": "linux"
        "record_id": "r123"
    }

