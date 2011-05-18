#/bin sh

eval "$(ucr shell)"

# Extension
udm settings/extended_attribute create \
	--ignore_exists \
	--position "cn=custom attributes,cn=univention,$ldap_base" \
	--set name="AstExtension" \
	--set CLIName="phoneExtension" \
	--set module="users/user" \
	--set tabName="Phone" \
	--append translationTabName='"de_DE" "Telefon"' \
	--set shortDescription="Extension" \
	--append translationShortDescription='"de_DE" "Extension"' \
	--set objectClass="AsteriskExtension" \
	--set ldapMapping="AstExtension" \
	--set syntax=phone

# Password
udm settings/extended_attribute create \
	--ignore_exists \
	--position "cn=custom attributes,cn=univention,$ldap_base" \
	--set name="AstAccountSecret" \
	--set CLIName="AstAccountSecret" \
	--set module="users/user" \
	--set tabName="Phone" \
	--append translationTabName='"de_DE" "Telefon"' \
	--set shortDescription="Password" \
	--append translationShortDescription='"de_DE" "Passwort"' \
	--set objectClass="AsteriskSIPUser" \
	--set ldapMapping="AstAccountSecret" \
	--set syntax=userPasswd

# Ipaddress
udm settings/extended_attribute create \
	--ignore_exists \
	--position "cn=custom attributes,cn=univention,$ldap_base" \
	--set name="AstAccountIpaddr" \
	--set CLIName="AstAccountIpaddr" \
	--set module="users/user" \
	--set tabName="Phone" \
	--append translationTabName='"de_DE" "Telefon"' \
	--set shortDescription="IP address" \
	--append translationShortDescription='"de_DE" "IP-Addresse"' \
	--set objectClass="AsteriskSIPUser" \
	--set ldapMapping="AstAccountIpaddr" \
	--set syntax=ipAddress

# Host
udm settings/extended_attribute create \
	--ignore_exists \
	--position "cn=custom attributes,cn=univention,$ldap_base" \
	--set name="AstAccountHost" \
	--set CLIName="AstAccountHost" \
	--set module="users/user" \
	--set tabName="Phone" \
	--append translationTabName='"de_DE" "Telefon"' \
	--set shortDescription="Hostname" \
	--append translationShortDescription='"de_DE" "Hostname"' \
	--set objectClass="AsteriskSIPUser" \
	--set ldapMapping="AstAccountHost" \
	--set syntax=hostName

# Mailbox
udm settings/extended_attribute create \
	--ignore_exists \
	--position "cn=custom attributes,cn=univention,$ldap_base" \
	--set name="AstAccountMailbox" \
	--set CLIName="AstAccountMailbox" \
	--set module="users/user" \
	--set tabName="Phone" \
	--append translationTabName='"de_DE" "Telefon"' \
	--set shortDescription="Mailbox" \
	--append translationShortDescription='"de_DE" "Mailbox"' \
	--set objectClass="AsteriskSIPUser" \
	--set ldapMapping="AstAccountMailbox" \
	--set syntax=string

