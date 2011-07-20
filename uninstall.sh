#!/bin/bash

set -e
set -u

cd "`dirname $0`"

. settings.sh

echo "Deleting default container for asterisk data..."
python2.4 frontend/ldapDefaultNode/uninstall.py
echo -e "\t\t\t\t\t\t\tdone."

## Currently not needed
# echo "Deleting extended attributes for UMC user module..."
# sh frontend/user-phone-extension/uninstall.sh
# echo -e "\t\t\t\t\t\t\tdone."

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

echo "Deleting folder for asterisk configuration files..."
rm -r "$AST4UCS_ASTCONF_PATH"
echo -e "\t\t\t\t\t\t\tdone."

echo "Removing UCR variables..."
ucr unset asterisk/sipconf
ucr unset asterisk/voicemailconf
ucr unset asterisk/musiconholdconf
ucr unset asterisk/queuesconf
ucr unset asterisk/meetmeconf
ucr unset asterisk/backupsuffix
ucr unset asterisk/hookcommand
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

