# coding=utf-8

import univention.admin.filter
import univention.admin.handlers
import univention.admin.handlers.asterisk
import univention.admin.syntax

module = "asterisk/phoneGroup"
childs = 0
short_description = u"Telefongruppe"
long_description = u"Telefongruppe"
operations = ['add', 'edit', 'remove', 'search', 'move']
options = {}

layout = [
	univention.admin.tab('Allgemein', 'Allgemeine Einstellungen', [
		[ univention.admin.field("commonName") ],
		[ univention.admin.field("jointRinging"),
			univention.admin.field("takeover") ],
	])
]

property_descriptions = {
	"commonName": univention.admin.property(
		short_description="Name",
		syntax=univention.admin.syntax.string,
		identifies=True,
		required=True
	),
	"jointRinging": univention.admin.property(
		short_description="Gemeinsames Klingeln",
		syntax=univention.admin.syntax.boolean,
	),
	"takeover": univention.admin.property(
		short_description=u"Anrufübernahme aus Gruppe",
		syntax=univention.admin.syntax.boolean,
	),
}

mapping = univention.admin.mapping.mapping()
mapping.register("commonName", "cn",
	None, univention.admin.mapping.ListToString)
mapping.register("jointRinging", "ast4ucsPhonegroupJointringing",
	None, univention.admin.mapping.ListToString)
mapping.register("takeover", "ast4ucsPhonegroupTakeover",
	None, univention.admin.mapping.ListToString)

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
		univention.admin.handlers.simpleLdap.open(self)
		self.save()

	def _ldap_pre_create(self):
		self.dn = '%s=%s,%s' % (
			mapping.mapName('commonName'),
			mapping.mapValue('commonName', self.info['commonName']),
			self.position.getDn()
		)

	def _ldap_addlist(self):
		return [('objectClass', ['top', 'ast4ucsPhonegroup' ])]


def lookup(co, lo, filter_s, base='', superordinate=None, scope='sub', 
		unique=False, required=False, timeout=-1, sizelimit=0):
	filter = univention.admin.filter.conjunction('&', [
		univention.admin.filter.expression(
			'objectClass', "ast4ucsPhonegroup")
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
	return 'ast4ucsPhonegroup' in attr.get('objectClass', [])

