#!/bin/bash

set -e
set -u

# zieht die verschiedenen dateien in ein einziges verzeichnis und
# erleichtert damit das versionieren und debuggen

cd "`dirname %0`"

cp -r /usr/lib/python2.4/site-packages/univention/admin/handlers/asterisk/ frontend/

cp /etc/univention/templates/files/etc/ldap/slapd.conf.d/80asterisk /etc/univention/templates/info/asterisk.info /usr/share/univention-ldap/schema/asterisk.schema schema/



