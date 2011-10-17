#!/usr/bin/python2.4
# -*- coding: utf-8 -*-

import univention.config_registry
import univention.admin.uldap
import univention.admin.uexceptions
import univention.admin.config
import univention.admin.handlers.container.cn
from univention.admin.handlers.asterisk \
	import contact, phoneGroup, waitingLoop, sipPhone, conferenceRoom, \
		phoneType, mailbox, faxGroup, server, fax, phoneBook

ucr = univention.config_registry.ConfigRegistry()
ucr.load()
ldap_master = ucr.get('ldap/master', '')
ldap_base = ucr.get('ldap/base', '')

binddn = ','.join(('cn=admin', ldap_base))
bindpw = open('/etc/ldap.secret','r').read().strip()

ldap = univention.admin.uldap.access(host=ldap_master, base=ldap_base,
	binddn=binddn, bindpw=bindpw, start_tls=2)

dcDn = "cn=default containers,cn=univention,%s"%ldap.base
asteriskDefaultDn = "cn=asterisk,%s"%ldap.base


dc = ldap.get(dcDn)
if asteriskDefaultDn in dc.get("univentionAsteriskObject", []):
	ldap.modify(dcDn, [("univentionAsteriskObject",
		asteriskDefaultDn, None)])
else:
	print "UniventionAsteriskObject was not set."

if "univentionDirectoryWithAsterisk" in dc.get("objectClass", []):
	ldap.modify(dcDn, [("objectClass",
		"univentionDirectoryWithAsterisk", None)])
else:
	print "ObjectClass was not set."


config = univention.admin.config.config()
base = univention.admin.uldap.position(ldap.base)

for entrytype in [contact, waitingLoop, phoneGroup, sipPhone, conferenceRoom,
		phoneType, mailbox, faxGroup, fax, server, phoneBook]:
	for entry in entrytype.lookup(config, ldap, None):
		entry.remove()

try:
	astContainer = univention.admin.handlers.container.cn.object(
		config, ldap, base, asteriskDefaultDn)
	astContainer.remove()
except univention.admin.uexceptions.noObject:
	print "Asterisk default container was already removed."

