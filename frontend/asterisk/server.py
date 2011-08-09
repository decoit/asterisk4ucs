# coding=utf-8

import univention.admin.filter
import univention.admin.handlers
from univention.admin.handlers import asterisk
import univention.admin.syntax
import time

module = "asterisk/server"
childs = 0
short_description = u"Asterisk-Server"
long_description = u"Asterisk-Server"
operations = ['add', 'edit', 'remove', 'search', 'move']
options = {}

layout = [
	univention.admin.tab('Allgemein', 'Allgemeine Einstellungen', [
		[ univention.admin.field("commonName") ],
		[ univention.admin.field("host") ],
		[ univention.admin.field("lastupdate_gui"),
			univention.admin.field("apply") ],
	])
]

property_descriptions = {
	"commonName": univention.admin.property(
		short_description="Name",
		syntax=univention.admin.syntax.string,
		identifies=True,
		required=True
	),
	"host": univention.admin.property(
		short_description="Host",
		syntax=univention.admin.syntax.LDAP_Search(
                        filter="objectClass=univentionHost",
                        attribute=['computers/computer: name'],
                        value='computers/computer: dn',
                ),
		required=True
	),
	"lastupdate": univention.admin.property(
		syntax=univention.admin.syntax.integer,
	),
	"lastupdate_gui": univention.admin.property(
		short_description=u"Konfiguration zuletzt eingespielt am:",
		syntax=univention.admin.syntax.string,
		editable=False,
	),
	"apply": univention.admin.property(
		short_description=u"Konfiguration jetzt einspielen?",
		syntax=univention.admin.syntax.boolean,
		default=False,
	),
	"configs": univention.admin.property(
		syntax=univention.admin.syntax.string,
		multivalue=True,
	),
}

mapping = univention.admin.mapping.mapping()
mapping.register("commonName", "cn",
	None, univention.admin.mapping.ListToString)
mapping.register("host", "ast4ucsServerHost",
	None, univention.admin.mapping.ListToString)
mapping.register("lastupdate", "ast4ucsServerLastupdate",
	None, univention.admin.mapping.ListToString)
mapping.register("configs", "ast4ucsServerConfig")

class object(univention.admin.handlers.simpleLdap):
	module=module

	def __init__(self, co, lo, position, dn='', superordinate=None,
			arg=None):
		global mapping
		global property_descriptions
		self.co = co
		self.lo = lo
		self.dn = dn
		self.position = position
		self._exists = 0
		self.mapping = mapping
		self.descriptions = property_descriptions
		univention.admin.handlers.simpleLdap.__init__(self, co, lo, 
			position, dn, superordinate)

	def exists(self):
		return self._exists

	def open(self):
		try:
			self.info["lastupdate_gui"] = time.strftime(
				"%d.%m.%Y %H:%M:%S", time.localtime(
				int(self.info.get("lastupdate",""))))
		except ValueError:
			self.info["lastupdate_gui"] = "never"

		univention.admin.handlers.simpleLdap.open(self)
		self.save()

        def _ldap_pre_modify(self):
		if (self.info.get('apply') == "1" or
					not self.info.get("lastupdate")):
	                self.info['lastupdate'] = str(int(time.time()))
			self.info['configs'] = asterisk.genConfigs(
							self.co, self.lo)

	def _ldap_pre_create(self):
		self.dn = '%s=%s,%s' % (
			mapping.mapName('commonName'),
			mapping.mapValue('commonName', self.info['commonName']),
			self.position.getDn()
		)

	def _ldap_addlist(self):
		return [('objectClass', ['top', 'ast4ucsServer' ])]


def lookup(co, lo, filter_s, base='', superordinate=None, scope='sub', 
		unique=False, required=False, timeout=-1, sizelimit=0):
	filter = univention.admin.filter.conjunction('&', [
		univention.admin.filter.expression(
			'objectClass', "ast4ucsServer")
	])
 
	if filter_s:
		filter_p = univention.admin.filter.parse(filter_s)
		univention.admin.filter.walk(filter_p, 
			univention.admin.mapping.mapRewrite, arg=mapping)
		filter.expressions.append(filter_p)
 
	res = []
	for dn in lo.searchDn(unicode(filter), base, scope, unique, required, 
			timeout, sizelimit):
		res.append(object(co, lo, None, dn))
	return res

def identify(dn, attr, canonical=0):
	return 'ast4ucsServer' in attr.get('objectClass', [])

