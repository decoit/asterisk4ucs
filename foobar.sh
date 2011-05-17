#!/bin/bash

cd "`dirname %0`"

cp /usr/lib/python2.4/site-packages/univention/admin/handlers/asterisk/{asterisk.py,contact.py,phonegroup.py,waitingloop.py} .

cp /etc/univention/templates/files/etc/ldap/slapd.conf.d/99test .

cp /etc/univention/templates/info/univention-ldap-server.info .

cp /usr/share/univention-ldap/schema/phonebook.schema .


