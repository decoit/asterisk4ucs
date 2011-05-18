#/bin sh

eval "$(ucr shell)"

# Extension
udm settings/extended_attribute remove --dn "cn=AstExtension,\
	cn=custom attributes,cn=univention,$ldap_base"

# Password
udm settings/extended_attribute remove --dn "cn=AstAccountSecret,\
	cn=custom attributes,cn=univention,$ldap_base"

# Ipaddress
udm settings/extended_attribute remove --dn "cn=AstAccountIpaddr,\
	cn=custom attributes,cn=univention,$ldap_base"

# Host
udm settings/extended_attribute remove --dn "cn=AstAccountHost,\
	cn=custom attributes,cn=univention,$ldap_base"

# Mailbox
udm settings/extended_attribute remove --dn "cn=AstAccountMailbox,\
	cn=custom attributes,cn=univention,$ldap_base"

