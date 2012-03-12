pytunia Utilities
=================

This directory contains additional programs intended for use with a pytunia server.

`gen_revisions`
---------------

Generates JSON to be pushed to the CouchDB server. Generally a post-commit hook should be adding documents to the DB as revisions roll in, but this is useful for build testing old revisions or if the commit hook fails.

Uses svn log to get revision author and description, svn ls to get list of functional tests.

Usage:

    $ ./gen_revisions svn_url changeset_url start_rev end_rev > some_revisions.json

       - svn_url: url for public svn checkout
       - changeset_url: base url for changesets, e.g. in Trac. revision number is appended
       - start_rev: start of range of revisions to processing
       - end_rev: end of range to process (not inclusive)

    $ kanso pushdata pytunia some_revisions.json

`wcpush`
--------

Send an SVN working copy off a pytunia server for testing. Requires the [pysvn](http://pysvn.tigris.org) package.

Uses pysvn to generate a diff and get repo metadata. uuencodes the diff so it is json-safe, generates pytunia documents, and pushes them to the database using httplib.

Note: putting these on-demand tests and the production build tests in the same database is possible, but probably not wise. Instead, run a second master with a separate database.

    $ ./wcpush [-m message] [-s server] [-b branch] [-r repository] 

        - message: description of the changes. defaults to 'No description'
        - server: pytunia server. defaults to localhost:5984. NOTE: no 'http://'!
        - branch: git branch to test
        - repository: git repository to test (i.e. git@github.com:username/repository)

`rm_record`
-----------

Delete one or more records and all associated tasks from the database. It does not currently de-allocate the node, and cannot halt a job in progress. Deleting an in-progress task will result in undefined behavior.

Uses the project settings to make the database connection, attempting to `import settings` from `.`, `..`, or the Python path. `settings.py` must be in one of those places. 

    $ ./rm_record <record_id> [record_id_2 ...]

