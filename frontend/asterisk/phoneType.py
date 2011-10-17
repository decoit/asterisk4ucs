# coding=utf-8

import univention.admin.filter
import univention.admin.handlers
import univention.admin.syntax
from univention.admin.layout import Tab

module = "asterisk/phoneType"
childs = 0
short_description = u"Asterisk: Telefontyp"
operations = ['add', 'edit', 'remove', 'search', 'move']
options = {}

layout = [
	Tab('Allgemein', 'Allgemeine Kenndaten', layout = [
		[ "commonName" ],
		[ "displaySize", "manufacturer" ],
		[ "type" ],
	])
]

property_descriptions = {
	"commonName": univention.admin.property(
		short_description="Name",
		syntax=univention.admin.syntax.string,
		identifies=True,
		required=True
	),
	"displaySize": univention.admin.property(
		short_description=u"Displaygröße",
		syntax=univention.admin.syntax.string,
	),
	"manufacturer": univention.admin.property(
		short_description="Hersteller",
		syntax=univention.admin.syntax.string,
	),
	"type": univention.admin.property(
		short_description="Typ",
		syntax=univention.admin.syntax.string,
	),
}

mapping = univention.admin.mapping.mapping()
mapping.register("commonName", "cn",
	None, univention.admin.mapping.ListToString)
mapping.register("displaySize", "ast4ucsPhonetypeDisplaysize",
	None, univention.admin.mapping.ListToString)
mapping.register("manufacturer", "ast4ucsPhonetypeManufacturer",
	None, univention.admin.mapping.ListToString)
mapping.register("type", "ast4ucsPhonetypeType",
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
		return [('objectClass', ['top', 'ast4ucsPhonetype' ])]


def lookup(co, lo, filter_s, base='', superordinate=None, scope='sub', 
		unique=False, required=False, timeout=-1, sizelimit=0):
	filter = univention.admin.filter.conjunction('&', [
		univention.admin.filter.expression(
			'objectClass', "ast4ucsPhonetype")
	])
 
	if filter_s:
		filter_p = univention.admin.filter.parse(filter_s)
		univention.admin.filter.walk(filter_p, 
			univention.admin.mapping.mapRewrite, arg=mapping)
		filter.expressions.append(filter_p)
 
	res = []
	for dn, attrs in lo.search(unicode(filter), base, scope, [], unique,
			required, timeout, sizelimit):
		res.append(object(co, lo, None, dn=dn,
				superordinate=superordinate, attributes=attrs))
	return res

def identify(dn, attr, canonical=0):
	return 'ast4ucsPhonetype' in attr.get('objectClass', [])

