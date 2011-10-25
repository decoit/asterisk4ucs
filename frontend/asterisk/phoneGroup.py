# coding=utf-8

import univention.admin.filter
import univention.admin.handlers
from univention.admin.handlers.asterisk import \
	reverseFieldsLoad, reverseFieldsSave
import univention.admin.syntax
from univention.admin.layout import Tab

module = "asterisk/phoneGroup"
short_description = u"Asterisk: Telefongruppe"
operations = ['add', 'edit', 'remove', 'search', 'move']
options = {}

childs = 0
usewizard = 1
superordinate = "asterisk/server"

layout = [
	Tab('Allgemein', 'Allgemeine Einstellungen', layout = [
		[ "commonName", "id" ],
		[ "callphones", "pickupphones" ],
	])
]

property_descriptions = {
	"commonName": univention.admin.property(
		short_description="Name",
		syntax=univention.admin.syntax.string,
		identifies=True,
		required=True
	),
	"id": univention.admin.property(
		short_description="Telefongruppen-Nummer",
		syntax=univention.admin.syntax.integer,
		required=True
	),
	"callphones": univention.admin.property(
		short_description="'Callgroup'-Teilnehmer",
		syntax=univention.admin.syntax.LDAP_Search(
                        filter="objectClass=ast4ucsPhone",
                        attribute=['asterisk/sipPhone: name'],
                        value='asterisk/sipPhone: dn',
                ),
		multivalue=True,
	),
	"pickupphones": univention.admin.property(
		short_description="'Pickupgroup'-Teilnehmer",
		syntax=univention.admin.syntax.LDAP_Search(
                        filter="objectClass=ast4ucsPhone",
                        attribute=['asterisk/sipPhone: name'],
                        value='asterisk/sipPhone: dn',
                ),
		multivalue=True,
	),
}

mapping = univention.admin.mapping.mapping()
mapping.register("commonName", "cn",
	None, univention.admin.mapping.ListToString)
mapping.register("id", "ast4ucsPhonegroupId",
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
		
		self.reverseFields = [
			("pickupphones", "asterisk/sipPhone", "pickupgroups"),
			("callphones", "asterisk/sipPhone", "callgroups"),
		]

	def exists(self):
		return self._exists

	def open(self):
		univention.admin.handlers.simpleLdap.open(self)
		reverseFieldsLoad(self)
		self.save()

	def _ldap_pre_create(self):
		self.dn = '%s=%s,%s' % (
			mapping.mapName('commonName'),
			mapping.mapValue('commonName', self.info['commonName']),
			self.position.getDn()
		)
		reverseFieldsSave(self)
	
	def _ldap_pre_modify(self):
		reverseFieldsSave(self)
	
	def _ldap_pre_remove(self):
		self.open()
		self.info = {}
		reverseFieldsSave(self)

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
	for dn, attrs in lo.search(unicode(filter), base, scope, [], unique,
			required, timeout, sizelimit):
		res.append(object(co, lo, None, dn=dn,
				superordinate=superordinate, attributes=attrs))
	return res

def identify(dn, attr, canonical=0):
	return 'ast4ucsPhonegroup' in attr.get('objectClass', [])

