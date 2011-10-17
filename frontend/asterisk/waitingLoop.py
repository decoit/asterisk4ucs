# coding=utf-8

import univention.admin.filter
import univention.admin.handlers
from univention.admin.handlers.asterisk import \
	reverseFieldsLoad, reverseFieldsSave
import univention.admin.syntax
from univention.admin.layout import Tab

module = "asterisk/waitingLoop"
childs = 0
short_description = u"Asterisk: Warteschlange"
operations = ['add', 'edit', 'remove', 'search', 'move']
options = {}

layout = [
	Tab('Allgemein', 'Allgemeine Einstellungen', layout = [
		[ "commonName", "extension" ],
		[ "strategy", "maxCalls" ],
		[ "memberDelay", "members" ],
		[ "delayMusic" ],
	])
]

class SyntaxStrategy(univention.admin.syntax.select):
	name="strategy"
	choices = [
		("ringall", u"Alle gleichzeitig anklingeln (ringall)"),
		("roundrobin", u"Alle der Reihe nach anklingeln (roundrobin)"),
		("leastrecent", u"Den am längsten inaktiven Anschluss " + 
			u"anklingeln (leastrecent)"),
		("fewestcalls", u"Den Anschluss mit den wenigsten "+
			u"beantworteten Anrufen anklingeln (fewestcalls)"),
		("random", u"Einen zufälligen Anschluss anklingeln"),
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
	"strategy": univention.admin.property(
		short_description="Strategie",
		syntax=SyntaxStrategy,
	),
	"maxCalls": univention.admin.property(
		short_description="Maximalzahl gleichzeitiger Anrufe",
		syntax=univention.admin.syntax.integer,
		default="50",
	),
	"memberDelay": univention.admin.property(
		short_description="Wartezeit zwischen Anrufen (in Sekunden)",
		syntax=univention.admin.syntax.integer,
		default="10",
	),
	"delayMusic": univention.admin.property(
		short_description="Warteschlangenmusik",
		syntax=univention.admin.syntax.string,
	),
	"members": univention.admin.property(
		short_description="Teilnehmer",
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
mapping.register("extension", "AstExtension",
	None, univention.admin.mapping.ListToString)
mapping.register("strategy", "ast4ucsWaitingloopStrategy",
	None, univention.admin.mapping.ListToString)
mapping.register("maxCalls", "ast4ucsWaitingloopMaxcalls",
	None, univention.admin.mapping.ListToString)
mapping.register("memberDelay", "ast4ucsWaitingloopMemberdelay",
	None, univention.admin.mapping.ListToString)
mapping.register("delayMusic", "ast4ucsWaitingloopDelaymusic",
	None, univention.admin.mapping.ListToString)

class object(univention.admin.handlers.simpleLdap):
	module=module

	def __init__(self, co, lo, position, dn='', superordinate=None,
			arg=None):
		global mapping
		global property_descriptions
		property_descriptions["delayMusic"].syntax = \
			univention.admin.syntax.ast4ucsMusicSyntax(superordinate)
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
			("members", "asterisk/sipPhone", "waitingloops"),
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
		return [('objectClass', ['top', 'ast4ucsWaitingloop',
			'AsteriskExtension' ])]


def lookup(co, lo, filter_s, base='', superordinate=None, scope='sub', 
		unique=False, required=False, timeout=-1, sizelimit=0):
	filter = univention.admin.filter.conjunction('&', [
		univention.admin.filter.expression(
			'objectClass', "ast4ucsWaitingloop")
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
	return 'ast4ucsWaitingloop' in attr.get('objectClass', [])

