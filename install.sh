#!/bin/bash

set -e
set -u

cd "`dirname $0`"

UNI_TEMPLATE_PATH=/etc/univention/templates
UNI_SCHEMA_PATH=/usr/share/univention-ldap/schema
UNI_MODULE_PATH=/usr/lib/python2.4/site-packages/univention/admin/handers
UNI_ICON_PATH=/usr/share/univention-webui-style/icon

echo -en "Installing schema...\t\t"
cd schema/
install -m664 asterisk.schema "$UNI_SCHEMA_PATH/"
install -m664 80asterisk "$UNI_TEMPLATE_PATH/files/etc/ldap/slapd.conf.d/"
install -m664 asterisk.info "$UNI_TEMPLATE_PATH/info/"
cd ..
echo "done."

echo -en "Installing icons...\t\t"
mkdir -p "$UNI_ICON_PATH/asterisk"
install -m664 icons/asterisk/* "$UNI_ICON_PATH/asterisk/"
echo "done."

echo -en "Installing UMC module...\t\t"
mkdir -p "$UNI_MODULE_PATH/asterisk"
install -m664 frontend/asterisk/* "$UNI_MODULE_PATH/asterisk/"
echo "done."

# umc extended attributes

# ldap dir object default dings

# neustarten

