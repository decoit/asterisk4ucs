#!/bin/bash

set -e
set -u

eval "$(ucr shell)"

function create {
	module="$1"
	position="$2"
	shift 2
	udm $module create \
		--ignore_exists \
		--position "$position,$ldap_base" \
		"$@"
}

# Memberserver-Fake
create settings/service "cn=services,cn=univention" \
	--set name="Asterisk Server"
create computers/memberserver "cn=computers" \
	--set name="Fakemember"

# =============== Telefonbuch =================================================
create asterisk/phoneBook "cn=asterisk" \
	--set commonName="Testtelefonbuch"

# Kontakte
create asterisk/contact "cn=Testtelefonbuch,cn=asterisk" \
	--set commonName="Hans Dieter" \
	--set telephoneNumber="0118 999 881 999 119 725 3"
create asterisk/contact "cn=Testtelefonbuch,cn=asterisk" \
	--set commonName="Peter Müller" \
	--set telephoneNumber="1234567890"

# ========== Asterisk-Server ==================================================
create asterisk/server "cn=asterisk" \
	--set commonName="Testserver" \
	--set host="cn=Fakemember,cn=computers,$ldap_base"

# Konferenzraum
create asterisk/conferenceRoom "cn=Testserver,cn=asterisk" \
	--set commonName="Konferenzraum" \
	--set extension="50" \
	--set pin="1234" \
	--set adminPin="4321"

# Telefontyp
create asterisk/phoneType "cn=Testserver,cn=asterisk" \
	--set commonName="Grandstream 12D" \
	--set displaySize="ziemlich groß" \
	--set manufacturer="Grandstream" \
	--set type="Wählscheiben-Telefon"

# Telefongruppen
create asterisk/phoneGroup "cn=Testserver,cn=asterisk" \
	--set commonName="Softwareentwicklung" \
	--set id="1"
create asterisk/phoneGroup "cn=Testserver,cn=asterisk" \
	--set commonName="Systemmanagement" \
	--set id="2"

# Warteschleifen
create asterisk/waitingLoop "cn=Testserver,cn=asterisk" \
	--set commonName="Support-Hotline" \
	--set extension="50"

# Mailboxen
create asterisk/mailbox "cn=Testserver,cn=asterisk" \
	--set id="20" \
	--set password="1234" \
	--set email="1"
create asterisk/mailbox "cn=Testserver,cn=asterisk" \
	--set id="21" \
	--set password="1234" \
	--set email="1"

# Telefone
create asterisk/sipPhone "cn=Testserver,cn=asterisk" \
	--set extension="20" \
	--set password="1234" \
	--set phonetype="cn=Grandstream 12D,cn=Testserver,cn=asterisk,$ldap_base" \
	--set waitingloops="cn=Support-Hotline,cn=Testserver,cn=asterisk" \
	--set callgroups="cn=Systemmanagement,cn=Testserver,cn=asterisk" \
	--set pickupgroups="cn=Systemmanagement,cn=Testserver,cn=asterisk" \
	--set pickupgroups="cn=Softwareentwicklung,cn=Testserver,cn=asterisk"

create asterisk/sipPhone "cn=Testserver,cn=asterisk" \
	--set extension="21" \
	--set password="1234" \
	--set phonetype="cn=Grandstream 12D,cn=Testserver,cn=asterisk,$ldap_base" \
	--set waitingloops="cn=Support-Hotline,cn=Testserver,cn=asterisk" \
	--set callgroups="cn=Softwareentwicklung,cn=Testserver,cn=asterisk" \
	--set pickupgroups="cn=Softwareentwicklung,cn=Testserver,cn=asterisk" \
	--set pickupgroups="cn=Systemmanagement,cn=Testserver,cn=asterisk"

# ====================== Benutzer =============================================

create users/user "cn=users" \
	--set lastname="Moss" \
	--set firstname="Maurice" \
	--set username="mmoss" \
	--set password="mmoss" \
	--set overridePWLength="1"
udm users/user modify --dn "uid=mmoss,cn=users,$ldap_base" \
	--set mailbox="cn=mailbox 20,cn=Testserver,cn=asterisk,$ldap_base" \
	--set phones="cn=phone 20,cn=Testserver,cn=asterisk,$ldap_base"

create users/user "cn=users" \
	--set lastname="Trenneman" \
	--set firstname="Roy" \
	--set username="rtrenneman" \
	--set password="rtrenneman" \
	--set overridePWLength="1"
udm users/user modify --dn "uid=rtrenneman,cn=users,$ldap_base" \
	--set mailbox="cn=mailbox 21,cn=Testserver,cn=asterisk,$ldap_base" \
	--set phones="cn=phone 21,cn=Testserver,cn=asterisk,$ldap_base"

