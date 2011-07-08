Data Model for Pytunia
======================

Revision?
---------
* id (string?): revision number, uuid, etc.
* description (text): commit message, aide memoire etc.
* user? (string): optionally tied to Django or other auth?

Task
----
* name (string)
* revision? (foreign key Revision?)
* created (datetime)
* slave (foreign key Slave)
* checked_out (datetime)
* completed (datetime)
* success (bool)
* dependencies (list of foreign key Task) <- normalize

Slave
-----
* hostname (string)
* last_login (datetime)
* password (string)
* enabled (bool)
* platform (foreign key Platform)

Platform
--------
* name (string)
* os (string)
* 


