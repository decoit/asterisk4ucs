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

echo "Installing info-texts for UCR variables..."
install -m664 ucr/category.cfg "$UNI_REGINFO_PATH/categories/asterisk4ucs.cfg"
install -m664 ucr/variables.cfg "$UNI_REGINFO_PATH/variables/asterisk4ucs.cfg"
echo -e "\t\t\t\t\t\t\tdone."

echo "Setting default values for UCR variables..."
ucr set asterisk/mailbox/maxlength="$ast4ucs_ucr_mailbox_maxlength"
ucr set asterisk/mailbox/attach="$ast4ucs_ucr_mailbox_attach"
ucr set asterisk/mailbox/emailsubject="$ast4ucs_ucr_mailbox_emailsubject"
ucr set asterisk/mailbox/emailbody="$ast4ucs_ucr_mailbox_emailbody"
ucr set asterisk/mailbox/emaildateformat="$ast4ucs_ucr_mailbox_emaildateformat"
ucr set asterisk/mailbox/mailcommand="$ast4ucs_ucr_mailbox_mailcommand"
echo -e "\t\t\t\t\t\t\tdone."

echo "Installing UDM module..."
mkdir -p "$UNI_UDM_PATH/syntax.d"
install -m664 frontend/syntax/asterisk.py "$UNI_UDM_PATH/syntax.d/"
mkdir -p "$UNI_UDM_PATH/hooks.d"
install -m664 frontend/hooks/asterisk.py "$UNI_UDM_PATH/hooks.d/"
mkdir -p "$UNI_UDM_PATH/handlers/asterisk"
install -m664 frontend/asterisk/* "$UNI_UDM_PATH/handlers/asterisk/"
echo -e "\t\t\t\t\t\t\tdone."

echo "Creating extended attributes for UDM user module..."
sh frontend/user-phone-extension/install.sh
echo -e "\t\t\t\t\t\t\tdone."

echo "Creating default container for asterisk data..."
python2.4 frontend/ldapDefaultNode/install.py
echo -e "\t\t\t\t\t\t\tdone."

echo "Restarting apache2..."
invoke-rc.d apache2 restart
echo -e "\t\t\t\t\t\t\tdone."

echo "Installation successful."

