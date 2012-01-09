#!/bin/bash

set -e
set -u

eval "$(ucr shell)"

function create {
	module="$1"
	name="$2"
	position="$3"
	shift 3
	udm $module create \
		--ignore_exists \
		--position "$position,$ldap_base" \
		--set name="$name" \
		--set commonName="$name" \
		"$@"
}

# Memberserver-Fake
create settings/service "Asterisk Server" "cn=services,cn=univention"
create computers/memberserver "Fakemember" "cn=computers"

# =============== Telefonbuch =================================================
create asterisk/phoneBook "Testtelefonbuch" "cn=asterisk"

# Kontakte
create asterisk/contact "Hans Dieter" "cn=Testtelefonbuch,cn=asterisk" \
	--set telephoneNumber="0118 999 881 999 119 725 3"
create asterisk/contact "Peter Mueller" "cn=Testtelefonbuch,cn=asterisk" \
	--set telephoneNumber="1234567890"

# ========== Asterisk-Server ==================================================
create asterisk/server "Testserver" "cn=asterisk" \
	--set host="cn=Fakemember,cn=computers,$ldap_base"

# Konferenzraum
create asterisk/conferenceRoom "Konferenzraum" "cn=Testserver,cn=asterisk" \
	--set extension="50" \
	--set pin="1234" \
	--set adminPin="4321"

# Telefontyp
create asterisk/phoneType "Grandstream 12D" "cn=Testserver,cn=asterisk" \
	--set displaySize="ziemlich groß" \
	--set manufacturer="Grandstream" \
	--set type="Wählscheiben-Telefon"

# Telefongruppen
create asterisk/phoneGroup "Softwareentwicklung" "cn=Testserver,cn=asterisk" \
	--set id="1"
create asterisk/phoneGroup "Systemmanagement" "cn=Testserver,cn=asterisk" \
	--set id="2"

# Warteschleifen
create asterisk/waitingLoop "Support-Hotline" "cn=Testserver,cn=asterisk" \
	--set extension="50" \
	--set Name="Support-Hotline"

# Mailboxen
create asterisk/mailbox "" "cn=Testserver,cn=asterisk" \
	--set id="20" \
	--set password="1234" \
	--set email="1"
create asterisk/mailbox "" "cn=Testserver,cn=asterisk" \
	--set id="21" \
	--set password="1234" \
	--set email="1"

# Telefone
create asterisk/sipPhone "" "cn=Testserver,cn=asterisk" \
	--set extension="20" \
	--set password="1234" \
	--set phonetype="cn=Grandstream 12D,cn=Testserver,cn=asterisk,$ldap_base" \
	--set waitingloops="cn=Support-Hotline,cn=Testserver,cn=asterisk" \
	--set callgroups="cn=Systemmanagement,cn=Testserver,cn=asterisk" \
	--set pickupgroups="cn=Systemmanagement,cn=Testserver,cn=asterisk" \
	--set pickupgroups="cn=Softwareentwicklung,cn=Testserver,cn=asterisk"

create asterisk/sipPhone "" "cn=Testserver,cn=asterisk" \
	--set extension="21" \
	--set password="1234" \
	--set phonetype="cn=Grandstream 12D,cn=Testserver,cn=asterisk,$ldap_base" \
	--set waitingloops="cn=Support-Hotline,cn=Testserver,cn=asterisk" \
	--set callgroups="cn=Softwareentwicklung,cn=Testserver,cn=asterisk" \
	--set pickupgroups="cn=Softwareentwicklung,cn=Testserver,cn=asterisk" \
	--set pickupgroups="cn=Systemmanagement,cn=Testserver,cn=asterisk"

# ====================== Benutzer =============================================

create users/user "" "cn=users" \
	--set lastname="Moss" \
	--set firstname="Maurice" \
	--set username="mmoss" \
	--set password="mmoss" \
	--set overridePWLength="1"
udm users/user modify --dn "uid=mmoss,cn=users,$ldap_base" \
	--set mailbox="cn=mailbox 20,cn=Testserver,cn=asterisk,$ldap_base" \
	--set phones="cn=phone 20,cn=Testserver,cn=asterisk,$ldap_base"

create users/user "" "cn=users" \
	--set lastname="Trenneman" \
	--set firstname="Roy" \
	--set username="rtrenneman" \
	--set password="rtrenneman" \
	--set overridePWLength="1"
udm users/user modify --dn "uid=rtrenneman,cn=users,$ldap_base" \
	--set mailbox="cn=mailbox 21,cn=Testserver,cn=asterisk,$ldap_base" \
	--set phones="cn=phone 21,cn=Testserver,cn=asterisk,$ldap_base"

