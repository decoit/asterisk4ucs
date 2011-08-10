#!/bin/bash

set -e
set -u
shopt -s extglob

cd "`dirname $0`"

. settings.sh

echo "Deleting directory listener module..."
rm "$UNI_LISTENER_PATH/asterisk.py"
echo -e "\t\t\t\t\t\t\tdone."

echo "Restarting univention directory listener..."
invoke-rc.d univention-directory-listener restart
echo -e "\t\t\t\t\t\t\tdone."

echo "Removing info-texts for UCR variables..."
rm "$UNI_REGINFO_PATH/categories/asterisk_member.cfg"
rm "$UNI_REGINFO_PATH/variables/asterisk_member.cfg"
echo -e "\t\t\t\t\t\t\tdone."

echo "Removing UCR variables..."
ucr unset asterisk/confpath
ucr unset asterisk/asteriskbin
echo -e "\t\t\t\t\t\t\tdone."

echo "Uninstallation successful."
echo
echo "The asterisk configuration files still exist. You will also find a backup"
echo "of the configuration prior to installing Asterisk4UCS in the preUCS.bak"
echo "subdirectory of the asterisk configuration directory."

