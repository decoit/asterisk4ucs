

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
## Akzeptiert die von strftime() bekannten Direktiven (siehe
## http://pubs.opengroup.org/onlinepubs/009695399/functions/strftime.html )
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


#### ----- Voicemail-Einstellungen -----------

## Mailbox/Maxlength:
## Definiert die maximale Länge einer Sprachnachricht in Sekunden.
ast4ucs_ucr_mailbox_maxlength=300

## Mailbox/Attach:
## Legt fest, ob an die Benachrichtigungs-E-Mails an die Nutzer auch die
## Sprachnachricht als Sounddatei angehängt wird.
# ast4ucs_ucr_mailbox_attach=no
ast4ucs_ucr_mailbox_attach=yes

## Mailbox/Emailsubject:
## Mailbox/Emailbody:
## Definieren Subject bzw. Body der Benachrichtigungs-E-Mails.
## 
## Die folgenden Platzhalter können verwendet werden:
## 	${VM_NAME}	Name des Mailbox-Inhabers
## 	${VM_DUR}	Länge der Nachricht
## 	${VM_MSGNUM}	Nummer der Nachricht
## 	${VM_MAILBOX}	Name der Mailbox
## 	${VM_CALLERID}	Telefonnummer und Name des Anrufers
## 	${VM_CIDNUM}	Telefonnummer des Anrufers
## 	${VM_CIDNAME}	Name des Anrufers
## 	${VM_DATE}	Datum und Uhrzeit des Anrufs
## 	${VM_MESSAGEFILE}
## 		Name der Sounddatei, in der die Nachricht abgespeichert ist
## 
## Weiterhin können im Body die folgenden Escapesequenzen verwendet werden:
## 	\n	Neue Zeile
## 	\t	Tabulator-Zeichen
## 
ast4ucs_ucr_mailbox_emailsubject='Neue Sprachnachricht von ${VM_CALLERID}'
ast4ucs_ucr_mailbox_emailbody='Hallo ${VM_NAME},\n\nKannst du ${VM_DUR} Minuten erübrigen?\nDann rufe doch mal deine Voicemailbox ${VM_MAILBOX} ab...'

## Mailbox/Emaildateformat:
## Definiert das Datumsformat des Platzhalters ${VM_DATE} in strftime-Notation
## ( http://pubs.opengroup.org/onlinepubs/009695399/functions/strftime.html )
ast4ucs_ucr_mailbox_emaildateformat="%d.%m.%Y %H:%M"

## Mailbox/Mailcommand:
## Programm zum Versenden von E-Mails (unbedingt den absoluten Pfad angeben!)
# ast4ucs_ucr_mailbox_mailcommand="/usr/exim/bin/exim -t"
ast4ucs_ucr_mailbox_mailcommand="/usr/sbin/sendmail -t"

