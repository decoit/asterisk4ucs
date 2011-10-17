
eval "`ucr shell version/version`"

if [ "$version_version" = "2.4" ]; then
	UNI_TEMPLATE_PATH=/etc/univention/templates
	UNI_SCHEMA_PATH=/usr/share/univention-ldap/schema
	UNI_UDM_PATH=/usr/lib/python2.4/site-packages/univention/admin
	UNI_ICON_PATH=/usr/share/univention-webui-style/icon
	UNI_REGINFO_PATH=/etc/univention/registry.info/
	UNI_PYTHON=python2.4
elif [ "$version_version" = "3.0" ]; then
	UNI_TEMPLATE_PATH=/etc/univention/templates
	UNI_SCHEMA_PATH=/usr/share/univention-ldap/schema
	UNI_UDM_PATH=/usr/lib/python2.6/site-packages/univention/admin
	UNI_ICON_PATH=/usr/share/univention-webui-style/icon
	UNI_REGINFO_PATH=/etc/univention/registry.info/
	UNI_PYTHON=python2.6
else
	echo "This version of UCS is not supported."
	exit 1
fi

# --------------- UCR Settings -------------------------


