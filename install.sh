#!/bin/bash

set -e
set -u

cd "`dirname $0`"

. settings.sh

echo "Installing schemata..."
cd schema/
install -m664 asterisk.schema "$UNI_SCHEMA_PATH/"
install -m664 asterisk4ucs.schema "$UNI_SCHEMA_PATH/"
install -m664 80asterisk "$UNI_TEMPLATE_PATH/files/etc/ldap/slapd.conf.d/"
install -m664 asterisk.info "$UNI_TEMPLATE_PATH/info/"
cd ..
echo -e "\t\t\t\t\t\t\tdone."

echo "Updating slapd.conf..."
univention-config-registry commit /etc/ldap/slapd.conf
echo -e "\t\t\t\t\t\t\tdone."

echo "Restarting slapd..."
invoke-rc.d slapd restart
if [ ! \( -r /var/run/slapd/slapd.pid \
	-a -d /proc/`cat /var/run/slapd/slapd.pid &>/dev/null`/ \) ]; then
	echo -e "\t\t\t\t\t\t\tfailed."
	echo "Slapd failed to start."
	echo "There is probably an error in one of the schema files."
	exit 1
fi
echo -e "\t\t\t\t\t\t\tdone."

echo "Installing icons..."
mkdir -p "$UNI_ICON_PATH/asterisk"
install -m664 icons/asterisk/* "$UNI_ICON_PATH/asterisk/"
echo -e "\t\t\t\t\t\t\tdone."

echo "Creating folder for asterisk configuration files..."
mkdir -p "$AST4UCS_ASTCONF_PATH"
chown www-data:www-data "$AST4UCS_ASTCONF_PATH"
echo -e "\t\t\t\t\t\t\tdone."

echo "Setting default values for UCR variables..."
ucr set asterisk/sipconf="$ast4ucs_ucr_sipconf"
ucr set asterisk/voicemailconf="$ast4ucs_ucr_voicemailconf"
ucr set asterisk/backupsuffix="$ast4ucs_ucr_backupsuffix"
echo -e "\t\t\t\t\t\t\tdone."

echo "Installing UMC module..."
mkdir -p "$UNI_MODULE_PATH/asterisk"
install -m664 frontend/asterisk/* "$UNI_MODULE_PATH/asterisk/"
echo -e "\t\t\t\t\t\t\tdone."

## Currently not needed
# echo "Creating extended attributes for UMC user module..."
# sh frontend/user-phone-extension/install.sh
# echo -e "\t\t\t\t\t\t\tdone."

echo "Creating default container for asterisk data..."
python2.4 frontend/ldapDefaultNode/install.py
echo -e "\t\t\t\t\t\t\tdone."

echo "Restarting apache2..."
invoke-rc.d apache2 restart
echo -e "\t\t\t\t\t\t\tdone."

echo "Installation successful."

