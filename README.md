pytunia
========
pytunia is a platform for source code quality testing/continuous integration based on the [dirt](http://github.com/mastbaum/dirt) package.

In addition to testing compilation on various platform (a la buildbot), it can perform functional tests (scripted in Python), static tests, or any other task describable in a Python module.

These tasks are run on a grid of slave nodes, which need not share any resources, have zero state, and run no client-side software.

Results of all tests are stored in a CouchDB database and available to users via a web interface.

