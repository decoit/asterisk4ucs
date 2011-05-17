#!/bin/bash

LDAP_SCHEMA_PATH=/etc/ldap/schema
UNI_TEMPLATE_PATH=/etc/univention/templates
UNI_SCHEMA_PATH=/usr/share/univention-ldap/schema
UNI_MODULE_PATH=/usr/lib/python2.4/site-packages/univention/admin/handers

cd "`dirname $0`"

echo "Installing schema..."
install -m664 asterisk.schema "$LDAP_SCHEMA_PATH/"
install -m664 80asterisk "$UNI_TEMPLATE_PATH/files/etc/ldap/slapd.conf.d/"
# info installieren


# icon

# ldap dir object default dings

# asterisk/ nach modulepath

# neustarten


