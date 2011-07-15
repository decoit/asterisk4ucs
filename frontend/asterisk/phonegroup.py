# coding=utf-8

import univention.admin.filter
import univention.admin.handlers
import univention.admin.handlers.asterisk
import univention.admin.syntax

module = "asterisk/phonegroup"
childs = 0
short_description = u"Telefongruppe"
long_description = u"Telefongruppe"
operations = ['add', 'edit', 'remove', 'search', 'move']
options = {}

usewizard = 1
wizardmenustring="Telefongruppen"
wizarddescription="Telefongruppen hinzufügen, editieren und löschen"
wizardoperations={"add":["Add", "Add User"],"find":["Search", "Search for user(s)"]}

layout = [
	univention.admin.tab('Allgemein', 'Allgemeine Einstellungen', [
		[ univention.admin.field("commonName") ],
		[ univention.admin.field("members") ],
	])
]

property_descriptions = {
	"commonName": univention.admin.property(
		short_description="Name",
		syntax=univention.admin.syntax.string,
		identifies=True,
		required=True
	),
	"members": univention.admin.property(
		short_description="Teilnehmer",
		syntax=univention.admin.syntax.LDAP_Search(
			filter="objectClass=ast4ucsPhone",
			attribute=['asterisk/sipPhone: name'],
			value='asterisk/sipPhone: dn'
		),
		multivalue=True
	),
}

mapping = univention.admin.mapping.mapping()
mapping.register("commonName", "cn",
	None, univention.admin.mapping.ListToString)
mapping.register("members", "phoneGroupMember")

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
		return [('objectClass', ['top', 'phoneGroup' ])]


def lookup(co, lo, filter_s, base='', superordinate=None, scope='sub', 
		unique=False, required=False, timeout=-1, sizelimit=0):
	filter = univention.admin.filter.conjunction('&', [
		univention.admin.filter.expression(
			'objectClass', "phoneGroup")
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
	return 'phoneGroup' in attr.get('objectClass', [])

