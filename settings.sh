

UNI_TEMPLATE_PATH=/etc/univention/templates
UNI_SCHEMA_PATH=/usr/share/univention-ldap/schema
UNI_MODULE_PATH=/usr/lib/python2.4/site-packages/univention/admin/handlers
UNI_ICON_PATH=/usr/share/univention-webui-style/icon

AST4UCS_ASTCONF_PATH=/tmp/asterisk/


# --------------- UCR Settings -------------------------

ast4ucs_ucr_sipconf="$AST4UCS_ASTCONF_PATH/sip.conf"
ast4ucs_ucr_voicemailconf="$AST4UCS_ASTCONF_PATH/voicemail.conf"
ast4ucs_ucr_musiconholdconf="$AST4UCS_ASTCONF_PATH/musiconhold.conf"
ast4ucs_ucr_queuesconf="$AST4UCS_ASTCONF_PATH/queues.conf"
ast4ucs_ucr_meetmeconf="$AST4UCS_ASTCONF_PATH/meetme.conf"


## Backupsuffix:
## Akzeptiert die von strftime() bekannten Direktiven
# ast4ucs_ucr_backupsuffix=.bak
ast4ucs_ucr_backupsuffix=.bak-%y%m%d-%H%M%S

## Hookcommand:
## Wird ausgeführt, nachdem die Konfigurationsdateien neu generiert wurden.
## Der Befehl wird durch eine Shell ausgeführt, Umleitungen und Befehls-
## verkettungen sollten also funktionieren. Während der Befehl läuft, ist die
## UDM-Weboberfläche blockiert; der Befehl sollte sich also so schnell wie
## möglich beenden.
# ast4ucs_ucr_hookcommand="scp /tmp/asterisk/* asterisk:/etc/asterisk/ ; ssh asterisk invoke-rc.d asterisk restart"
ast4ucs_ucr_hookcommand=""


