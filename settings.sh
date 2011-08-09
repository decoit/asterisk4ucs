

UNI_TEMPLATE_PATH=/etc/univention/templates
UNI_SCHEMA_PATH=/usr/share/univention-ldap/schema
UNI_UDM_PATH=/usr/lib/python2.4/site-packages/univention/admin
UNI_ICON_PATH=/usr/share/univention-webui-style/icon
UNI_REGINFO_PATH=/etc/univention/registry.info/


# --------------- UCR Settings -------------------------

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
## Tip: Mailcommand wird von Asterisk auf dem Memberserver ausgeführt.
# ast4ucs_ucr_mailbox_mailcommand="/usr/exim/bin/exim -t"
ast4ucs_ucr_mailbox_mailcommand="/usr/sbin/sendmail -t"

