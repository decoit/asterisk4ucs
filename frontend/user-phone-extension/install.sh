#/bin sh

set -e
set -u

eval "$(ucr shell)"

udm settings/syntax create \
	--ignore_exists \
	--set name="ast4ucsPhoneSyntax" \
	--position "cn=univention,$ldap_base" \
	--set viewonly=FALSE \
	--set filter='(objectClass=ast4ucsPhone)' \
	--set attribute="asterisk/sipPhone: name" \
	--set value="asterisk/sipPhone: dn"

udm settings/syntax create \
	--ignore_exists \
	--set name="ast4ucsMailboxSyntax" \
	--position "cn=univention,$ldap_base" \
	--set viewonly=FALSE \
	--set filter='(objectClass=ast4ucsMailbox)' \
	--set attribute="asterisk/mailbox: commonName" \
	--set value="asterisk/mailbox: dn"

function addUserAttribute {
	name="$1"
	shift
	udm settings/extended_attribute create \
		--ignore_exists \
		--position "cn=custom attributes,cn=univention,$ldap_base" \
		--set module="users/user" \
		--set tabName="Phone" \
		--append translationTabName='"de_DE" "Telefon"' \
		--set objectClass=ast4ucsUser \
		--set name="$name" \
		--set CLIName="$name" \
		--set mayChange=1 \
		"$@"
}

addUserAttribute phones \
	--set shortDescription="Telefone" \
	--set tabPosition=1 \
	--set syntax=ast4ucsPhoneSyntax \
	--set ldapMapping="ast4ucsUserPhone" \
	--set multivalue=1 \
	--set hook="AsteriskUsersUserHook"

addUserAttribute mailbox \
	--set shortDescription="Anrufbeantworter" \
	--set tabPosition=2 \
	--set syntax=ast4ucsMailboxSyntax \
	--set ldapMapping="ast4ucsUserMailbox" \
	--set addEmptyValue=1

addUserAttribute extmode \
	--set shortDescription="Beim Anrufen Durchwahl senden" \
	--set tabPosition=3 \
	--set syntax=ast4ucsExtmodeSyntax \
	--set ldapMapping="ast4ucsUserExtmode"

addUserAttribute ringdelay \
	--set shortDescription="Intervall zwischen Telefonen (Sekunden)" \
	--set tabPosition=4 \
	--set syntax=ast4ucsDurationSyntax \
	--set ldapMapping="ast4ucsUserRingdelay" \
	--set default=10

addUserAttribute timeout \
	--set shortDescription="Mailbox antwortet nach (Sekunden)" \
	--set tabPosition=5 \
	--set syntax=ast4ucsDurationSyntax \
	--set ldapMapping="ast4ucsUserTimeout" \
	--set default=10


