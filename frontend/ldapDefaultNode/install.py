#!/usr/bin/python2.4
# -*- coding: utf-8 -*-

import univention.config_registry
import univention.admin.uldap
import univention.admin.uexceptions
import univention.admin.handlers.container.cn as container

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

config = univention.admin.config.config()
base = univention.admin.uldap.position(ldap.base)
foo = container.object(config, ldap, base)
foo.info['name'] = "asterisk"
foo.open()
try:
	foo.create()
except univention.admin.uexceptions.objectExists:
	print "Asterisk container already existed."

dc = ldap.get(dcDn)
if "univentionDirectoryWithAsterisk" not in dc.get("objectClass", []):
	ldap.modify(dcDn, [("objectClass", None,
		"univentionDirectoryWithAsterisk")])
else:
	print "ObjectClass was already set."

if "univentionAsteriskObject" not in dc.keys():
	ldap.modify(dcDn, [("univentionAsteriskObject", None,
		asteriskDefaultDn)])
else:
	print "UniventionAsteriskObject was already set."

