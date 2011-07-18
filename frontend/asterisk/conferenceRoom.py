# coding=utf-8

import univention.admin.filter
import univention.admin.handlers
import univention.admin.syntax

module = "asterisk/conferenceRoom"
childs = 0
short_description = u"Konferenzraum"
long_description = u"Konferenzraum"
operations = ['add', 'edit', 'remove', 'search', 'move']
options = {}

usewizard = 1
wizardmenustring="Konferenzraum"
wizarddescription="Konferenzräume hinzufügen, editieren und löschen"
wizardoperations={"add":["Add", "Add user."],"find":["Search", "Search for user(s)"]}

layout = [
	univention.admin.tab('Allgemein', 'Allgemeine Einstellungen', [
		[ univention.admin.field("commonName") ],
		[ univention.admin.field("extension"),
			univention.admin.field("maxMembers") ],
		[ univention.admin.field("pin"),
			univention.admin.field("adminPin") ],
		[ univention.admin.field("options") ],
	])
]

property_descriptions = {
	"commonName": univention.admin.property(
		short_description="Name",
		syntax=univention.admin.syntax.string,
		identifies=True,
		required=True
	),
	"extension": univention.admin.property(
		short_description="Durchwahl",
		syntax=univention.admin.syntax.phone,
	),
	"maxMembers": univention.admin.property(
		short_description="Maximalzahl der Benutzer",
		syntax=univention.admin.syntax.integer,
	),
	"pin": univention.admin.property(
		short_description="Pin",
		syntax=univention.admin.syntax.integer,
	),
	"adminPin": univention.admin.property(
		short_description="Admin-Pin",
		syntax=univention.admin.syntax.integer,
	),
	"options": univention.admin.property(
		short_description="Optionen",
		syntax=univention.admin.syntax.string,
	),
}

mapping = univention.admin.mapping.mapping()
mapping.register("commonName", "cn",
	None, univention.admin.mapping.ListToString)
mapping.register("extension", "AstExtension",
	None, univention.admin.mapping.ListToString)
mapping.register("maxMembers", "AstMeetmeMembers",
	None, univention.admin.mapping.ListToString)
mapping.register("pin", "AstMeetmePin",
	None, univention.admin.mapping.ListToString)
mapping.register("adminPin", "AstMeetmeAdminpin",
	None, univention.admin.mapping.ListToString)
mapping.register("options", "ast4ucsConfRoomOptions",
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
		return [('objectClass', ['top', 'ast4ucsConferenceRoom',
			'AsteriskExtension', 'AsteriskMeetme' ])]


def lookup(co, lo, filter_s, base='', superordinate=None, scope='sub', 
		unique=False, required=False, timeout=-1, sizelimit=0):
	filter = univention.admin.filter.conjunction('&', [
		univention.admin.filter.expression(
			'objectClass', "ast4ucsConferenceRoom")
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
	return 'ast4ucsConferenceRoom' in attr.get('objectClass', [])

