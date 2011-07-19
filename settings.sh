

UNI_TEMPLATE_PATH=/etc/univention/templates
UNI_SCHEMA_PATH=/usr/share/univention-ldap/schema
UNI_MODULE_PATH=/usr/lib/python2.4/site-packages/univention/admin/handlers
UNI_ICON_PATH=/usr/share/univention-webui-style/icon

AST4UCS_ASTCONF_PATH=/tmp/asterisk/


# --------------- UCR Settings -------------------------

ast4ucs_ucr_sipconf="$AST4UCS_ASTCONF_PATH/sip.conf"
ast4ucs_ucr_voicemailconf="$AST4UCS_ASTCONF_PATH/voicemail.conf"

## Akzeptiert die von strftime() bekannten Direktiven
# ast4ucs_ucr_backupsuffix=.bak
ast4ucs_ucr_backupsuffix=.bak-%y%m%d-%H%M%S


