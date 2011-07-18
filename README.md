pytunia
=======

Real Introduction
-----------------
pytunia is take two of a grid-based build-, functional-, and static-testing platform. Its predecessor, ratbuild, originally ran functional tests in Python on a distributed grid, reported results to the master via Django XML-RPC, and presented results on a web page. I rewrote the RPC to use Apache Thrift, hacked in compilation and functional testing, static testing, and on-demand build testing for users wanting to test their working copy before they commit. pytunia is an effort to do this the right way, and very young.

Introduction
------------
pytunia is a platform for source code quality testing. In addition to testing compilation on various platform (a la buildbot), it can perform functional tests (scripted in Python) and static tests.

pytunia can manage testing for several branches or different projects, and supports both triggered (post-commit) automated testing and on-demand build testing of users working copies.

Testing is performed on a grid of slave nodes, which need not share any resources -- distributed grids are handled naturally. Slave nodes communicate with the build master via Thrift RPC.

Results of all tests are (will be) stored in a Django database and available to users via a web interface.

