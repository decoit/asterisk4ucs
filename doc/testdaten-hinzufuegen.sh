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

# Testuser
# todo

# Asterisk-Superordinates
create asterisk/phoneBook "Testtelefonbuch" "cn=asterisk"
create asterisk/server "Testserver" "cn=asterisk" \
	--set host="cn=Fakemember,cn=computers,$ldap_base"

# Kontakte
create asterisk/contact "Hans Dieter" "cn=Testtelefonbuch,cn=asterisk" \
	--set telephoneNumber="0118 999 881 999 119 725 3"
create asterisk/contact "Peter Mueller" "cn=Testtelefonbuch,cn=asterisk" \
	--set telephoneNumber="1234567890"

# Asterisk-Krams
# todo:
# zwei telefone nebst mailboxen
# telefontyp, konferenzraum
# zwei telefongruppen
# eine warteschlange

