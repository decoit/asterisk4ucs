#!/bin/bash

set -e
set -u

cd "`dirname $0`"

UNI_TEMPLATE_PATH=/etc/univention/templates
UNI_SCHEMA_PATH=/usr/share/univention-ldap/schema
UNI_MODULE_PATH=/usr/lib/python2.4/site-packages/univention/admin/handlers
UNI_ICON_PATH=/usr/share/univention-webui-style/icon

echo "Deleting default container for asterisk data..."
python2.4 frontend/ldapDefaultNode/uninstall.py
echo -e "\t\t\t\t\t\t\tdone."

echo "Deleting extended attributes for UMC user module..."
sh frontend/user-phone-extension/uninstall.sh
echo -e "\t\t\t\t\t\t\tdone."

echo "Uninstalling schemata..."
rm "$UNI_SCHEMA_PATH/asterisk.schema"
rm "$UNI_SCHEMA_PATH/asterisk4ucs.schema"
rm "$UNI_TEMPLATE_PATH/files/etc/ldap/slapd.conf.d/80asterisk"
rm "$UNI_TEMPLATE_PATH/info/asterisk.info"
echo -e "\t\t\t\t\t\t\tdone."

echo "Updating slapd.conf..."
univention-config-registry commit /etc/ldap/slapd.conf
echo -e "\t\t\t\t\t\t\tdone."

echo "Restarting slapd..."
invoke-rc.d slapd restart
echo -e "\t\t\t\t\t\t\tdone."

echo "Uninstalling UMC module..."
rm -r "$UNI_MODULE_PATH/asterisk"
echo -e "\t\t\t\t\t\t\tdone."

echo "Uninstalling icons..."
rm -r "$UNI_ICON_PATH/asterisk"
echo -e "\t\t\t\t\t\t\tdone."

echo "Restarting apache2..."
invoke-rc.d apache2 restart
echo -e "\t\t\t\t\t\t\tdone."

echo "Uninstallation successful."

