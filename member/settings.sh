

UNI_REGINFO_PATH=/etc/univention/registry.info
UNI_LISTENER_PATH=/usr/lib/univention-directory-listener/system
AST_CONF_PATH=/opt/asterisk-1.8/etc/asterisk


# --------------- UCR Settings -------------------------

## Confpath:
## In diesem Verzeichnis werden die automatisch generierten Asterisk-Configs
## abgelegt.
ast4ucs_ucr_confpath="$AST_CONF_PATH/ucs_autogen"

## Asteriskbin:
## Der Pfad zur ausführbaren Asterisk-Binary.
#ast4ucs_ucr_asteriskbin=/usr/sbin/asterisk
ast4ucs_ucr_asteriskbin=/opt/asterisk-1.8/sbin/asterisk

