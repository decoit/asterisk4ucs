# coding=utf-8

import univention.admin.filter
import univention.admin.handlers
import univention.admin.syntax
from univention.admin.layout import Tab
from univention.admin import uexceptions

module = "asterisk/conferenceRoom"
short_description = u"Asterisk: Konferenzraum"
operations = ['add', 'edit', 'remove', 'search', 'move']
options = {}

childs = 0
usewizard = 1
superordinate = "asterisk/server"

layout = [
	Tab('Allgemein', 'Allgemeine Einstellungen', layout = [
		[ "commonName", "extension" ],
		[ "maxMembers" ],
		[ "pin", "adminPin" ],
		[ "announceCount", "initiallyMuted" ],
		[ "musicOnHold", "quietMode" ],
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
		required=True,
	),
	"maxMembers": univention.admin.property(
		short_description="Maximalzahl der Benutzer",
		syntax=univention.admin.syntax.integer,
		default="100",
	),
	"pin": univention.admin.property(
		short_description="Pin",
		syntax=univention.admin.syntax.string,
		required=True,
		default="1234",
	),
	"adminPin": univention.admin.property(
		short_description="Admin-Pin",
		syntax=univention.admin.syntax.string,
		required=True,
		default="1234",
	),
	"announceCount": univention.admin.property(
		short_description="Beim Betreten Teilnehmerzahl ansagen",
		syntax=univention.admin.syntax.boolean,
	),
	"initiallyMuted": univention.admin.property(
		short_description=u"Teilnehmer zunächst muten",
		syntax=univention.admin.syntax.boolean,
	),
	"musicOnHold": univention.admin.property(
		short_description=u"Wartemusik für ersten Teilnehmer",
		syntax=univention.admin.syntax.boolean,
	),
	"quietMode": univention.admin.property(
		short_description="Kein Signal beim Betreten/Verlassen eines Teilnehmers",
		syntax=univention.admin.syntax.boolean,
	),
}

mapping = univention.admin.mapping.mapping()
mapping.register("commonName", "cn",
	None, univention.admin.mapping.ListToString)
mapping.register("extension", "ast4ucsConfroomExtension",
	None, univention.admin.mapping.ListToString)
mapping.register("maxMembers", "ast4ucsConfroomMaxmembers",
	None, univention.admin.mapping.ListToString)
mapping.register("pin", "ast4ucsConfroomPin",
	None, univention.admin.mapping.ListToString)
mapping.register("adminPin", "ast4ucsConfroomAdminpin",
	None, univention.admin.mapping.ListToString)

mapping.register("announceCount", "ast4ucsConfroomAnnouncecount",
	None, univention.admin.mapping.ListToString)
mapping.register("initiallyMuted", "ast4ucsConfroomInitiallymuted",
	None, univention.admin.mapping.ListToString)
mapping.register("musicOnHold", "ast4ucsConfroomMusiconhold",
	None, univention.admin.mapping.ListToString)
mapping.register("quietMode", "ast4ucsConfroomQuietmode",
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
		if self.info.get("pin"):
			if self.info.get("adminPin") == self.info["pin"]:
				class pinError(uexceptions.base):
					message="Pin und Admin-Pin dürfen "+\
					"nicht übereinstimmen."
				raise pinError

	def _ldap_pre_create(self):
		self.dn = '%s=%s,%s' % (
			mapping.mapName('commonName'),
			mapping.mapValue('commonName', self.info['commonName']),
			self.position.getDn()
		)

	def _ldap_addlist(self):
		return [('objectClass', ['top', 'ast4ucsConfroom'])]


def lookup(co, lo, filter_s, base='', superordinate=None, scope='sub', 
		unique=False, required=False, timeout=-1, sizelimit=0):
	filter = univention.admin.filter.conjunction('&', [
		univention.admin.filter.expression(
			'objectClass', "ast4ucsConfroom")
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
	return 'ast4ucsConfroom' in attr.get('objectClass', [])

