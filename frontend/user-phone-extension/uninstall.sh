#/bin sh

set -e
set -u

eval "$(ucr shell)"

for name in ast4ucsPhoneSyntax ast4ucsMailboxSyntax; do
	udm settings/syntax remove \
		--dn "cn=$name,cn=univention,$ldap_base"
done

for name in phones mailbox extmode ringdelay timeout; do
	udm settings/extended_attribute remove \
		--dn "cn=$name,cn=custom attributes,cn=univention,$ldap_base"
done

