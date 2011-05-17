
eval "$(ucr shell)"

# EXTENSION
udm settings/extended_attribute remove --dn "cn=AstExtension,\
	cn=custom attributes,cn=univention,$ldap_base"
udm settings/extended_attribute create \
	--ignore_exists \
	--position "cn=custom attributes,cn=univention,$ldap_base" \
	--set name="AstExtension" \
	--set CLIName="phoneExtension" \
	--set module="users/user" \
	--set tabName="Phone" \
	--append translationTabName='"de_DE" "Telefon"' \
	--set tabPosition=1 \
	--set shortDescription="Extension" \
	--append translationShortDescription='"de_DE" "Extension"' \
	--set objectClass="AsteriskExtension" \
	--set ldapMapping="AstExtension" \
	--set syntax=phone \
	--set tabAdvanced=0 \
	--set mayChange=1 \
	--set multivalue=0 \
	--set default=0 

# PASSWORD
udm settings/extended_attribute remove --dn "cn=AstAccountSecret,\
	cn=custom attributes,cn=univention,$ldap_base"
udm settings/extended_attribute create \
	--ignore_exists \
	--position "cn=custom attributes,cn=univention,$ldap_base" \
	--set name="AstAccountSecret" \
	--set CLIName="AstAccountSecret" \
	--set module="users/user" \
	--set tabName="Phone" \
	--append translationTabName='"de_DE" "Telefon"' \
	--set tabPosition=1 \
	--set shortDescription="Password" \
	--append translationShortDescription='"de_DE" "Passwort"' \
	--set objectClass="AsteriskSIPUser" \
	--set ldapMapping="AstAccountSecret" \
	--set syntax=userPasswd \
	--set tabAdvanced=0 \
	--set mayChange=1 \
	--set multivalue=0 \
	--set default=0 

# Ipaddress
udm settings/extended_attribute remove --dn "cn=AstAccountIpaddr,\
	cn=custom attributes,cn=univention,$ldap_base"
udm settings/extended_attribute create \
	--ignore_exists \
	--position "cn=custom attributes,cn=univention,$ldap_base" \
	--set name="AstAccountIpaddr" \
	--set CLIName="AstAccountIpaddr" \
	--set module="users/user" \
	--set tabName="Phone" \
	--append translationTabName='"de_DE" "Telefon"' \
	--set tabPosition=1 \
	--set shortDescription="IP address" \
	--append translationShortDescription='"de_DE" "IP-Addresse"' \
	--set objectClass="AsteriskSIPUser" \
	--set ldapMapping="AstAccountIpaddr" \
	--set syntax=ipAddress \
	--set tabAdvanced=0 \
	--set mayChange=1 \
	--set multivalue=0 \
	--set default=0 

# Host
udm settings/extended_attribute remove --dn "cn=AstAccountHost,\
	cn=custom attributes,cn=univention,$ldap_base"
udm settings/extended_attribute create \
	--ignore_exists \
	--position "cn=custom attributes,cn=univention,$ldap_base" \
	--set name="AstAccountHost" \
	--set CLIName="AstAccountHost" \
	--set module="users/user" \
	--set tabName="Phone" \
	--append translationTabName='"de_DE" "Telefon"' \
	--set tabPosition=1 \
	--set shortDescription="Hostname" \
	--append translationShortDescription='"de_DE" "Hostname"' \
	--set objectClass="AsteriskSIPUser" \
	--set ldapMapping="AstAccountHost" \
	--set syntax=hostName \
	--set tabAdvanced=0 \
	--set mayChange=1 \
	--set multivalue=0 \
	--set default=0 

# Mailbox
udm settings/extended_attribute remove --dn "cn=AstAccountMailbox,\
	cn=custom attributes,cn=univention,$ldap_base"
udm settings/extended_attribute create \
	--ignore_exists \
	--position "cn=custom attributes,cn=univention,$ldap_base" \
	--set name="AstAccountMailbox" \
	--set CLIName="AstAccountMailbox" \
	--set module="users/user" \
	--set tabName="Phone" \
	--append translationTabName='"de_DE" "Telefon"' \
	--set tabPosition=1 \
	--set shortDescription="Mailbox" \
	--append translationShortDescription='"de_DE" "Mailbox"' \
	--set objectClass="AsteriskSIPUser" \
	--set ldapMapping="AstAccountMailbox" \
	--set syntax=string \
	--set tabAdvanced=0 \
	--set mayChange=1 \
	--set multivalue=0 \
	--set default=0 


