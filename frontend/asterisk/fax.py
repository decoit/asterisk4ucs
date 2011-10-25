# coding=utf-8

import univention.admin.filter
import univention.admin.handlers
import univention.admin.syntax
from univention.admin.layout import Tab

module = "asterisk/fax"
short_description = u"Asterisk: Fax"
operations = ['add', 'edit', 'remove', 'search', 'move']
options = {}

childs = 0
usewizard = 1
superordinate = "asterisk/server"

layout = [
	Tab('Allgemein', 'Allgemeine Einstellungen', layout = [
		[ "extension", "ipaddress" ],
		[ "macaddress", "hostname", ],
		[ "password" ],
	])
]

property_descriptions = {
	"name": univention.admin.property(
		short_description="Name",
		syntax=univention.admin.syntax.string,
		identifies=True,
		required=True,
		default="foo",
	),
	"extension": univention.admin.property(
		short_description="Durchwahl",
		syntax=univention.admin.syntax.string,
		required=True
	),
	"ipaddress": univention.admin.property(
		short_description="IP-Adresse",
		syntax=univention.admin.syntax.ipAddress,
	),
	"macaddress": univention.admin.property(
		short_description="MAC-Adresse",
		syntax=univention.admin.syntax.string
	),
	"hostname": univention.admin.property(
		short_description="Hostname",
		syntax=univention.admin.syntax.hostName
	),
	"password": univention.admin.property(
		short_description="Passwort",
		syntax=univention.admin.syntax.userPasswd,
		required=True,
	),
}

mapping = univention.admin.mapping.mapping()
mapping.register("name", "cn",
	None, univention.admin.mapping.ListToString)
mapping.register("extension", "AstExtension",
	None, univention.admin.mapping.ListToString)
mapping.register("ipaddress", "AstAccountIpaddr",
	None, univention.admin.mapping.ListToString)
mapping.register("macaddress", "macAddress",
	None, univention.admin.mapping.ListToString)
mapping.register("hostname", "AstAccountHost",
	None, univention.admin.mapping.ListToString)
mapping.register("password", "AstAccountSecret",
	None, univention.admin.mapping.ListToString)

class object(univention.admin.handlers.simpleLdap):
	module=module

	def __init__(self, co, lo, position, dn='', superordinate=None,
			attributes=[]):
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
	
	def _ldap_pre_ready(self):
		self.info['name'] = "fax " + self.info["extension"]
	
	def _ldap_pre_create(self):
		self.dn = '%s=%s,%s' % (
			mapping.mapName('name'),
			mapping.mapValue('name', self.info['name']),
			self.position.getDn()
		)
	
	def _ldap_addlist(self):
		return [('objectClass', ['top', 'ast4ucsFax',
			'AsteriskExtension', 'AsteriskSIPUser' ])]


def lookup(co, lo, filter_s, base='', superordinate=None, scope='sub', 
		unique=False, required=False, timeout=-1, sizelimit=0):
	filter = univention.admin.filter.conjunction('&', [
		univention.admin.filter.expression(
			'objectClass', "ast4ucsFax")
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
	return 'ast4ucsFax' in attr.get('objectClass', [])

