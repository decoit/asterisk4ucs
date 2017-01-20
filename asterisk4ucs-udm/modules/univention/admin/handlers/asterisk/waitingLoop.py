# coding=utf-8

"""
Copyright (C) 2012 DECOIT GmbH <asterisk4ucs@decoit.de>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License version 3 as
published by the Free Software Foundation

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

import univention.admin.filter
import univention.admin.handlers
from univention.admin.handlers.asterisk import \
	reverseFieldsLoad, reverseFieldsSave
import univention.admin.syntax
from univention.admin.layout import Tab

module = "asterisk/waitingLoop"
short_description = u"Asterisk4UCS-Management: Warteschlange"
operations = ['add', 'edit', 'remove', 'search', 'move']
options = {}

childs = 0
usewizard = 1
superordinate = "asterisk/server"

layout = [
	Tab('Allgemein', 'Allgemeine Einstellungen', layout = [
		[ "extension" ],
		[ "strategy", "maxCalls" ],
		[ "delayMusic", "memberDelay" ],
		[ "members" ],
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
	"extension": univention.admin.property(
		short_description="Durchwahl",
		syntax=univention.admin.syntax.string,
		identifies=True,
		required=True,
	),
	"strategy": univention.admin.property(
		short_description="Strategie",
		syntax=SyntaxStrategy,
		required=True,
		default="ringall",
	),
	"maxCalls": univention.admin.property(
		short_description="Maximalzahl gleichzeitiger Anrufe",
		syntax=univention.admin.syntax.integer,
		required=True,
		default="50",
	),
	"memberDelay": univention.admin.property(
		short_description="Wartezeit zwischen Anrufen (in Sekunden)",
		syntax=univention.admin.syntax.integer,
		required=True,
		default="10",
	),
	"delayMusic": univention.admin.property(
		short_description="Warteschlangenmusik",
		syntax=univention.admin.syntax.LDAP_Search(
			filter="(&(objectClass=ast4ucsMusic)"
				+ "(ast4ucsMusicMusic=*))",
			attribute=["asterisk/music: name"],
			value="asterisk/music: name",
		),
		required=True,
		default="default",
	),
	"members": univention.admin.property(
		short_description="Teilnehmer",
		syntax=univention.admin.syntax.LDAP_Search(
			filter="objectClass=ast4ucsPhone",
			attribute=['asterisk/sipPhone: extension'],
			value='asterisk/sipPhone: dn',
		),
		multivalue=True,
	),
}

mapping = univention.admin.mapping.mapping()
mapping.register("extension", "ast4ucsExtensionExtension",
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
			attributes=[]):
		self.reverseFields = [
			("members", "asterisk/sipPhone", "waitingloops"),
		]

		univention.admin.handlers.simpleLdap.__init__(self, co, lo, 
			position, dn, superordinate)

		self.openSuperordinate()
		if not self.superordinate:
			raise univention.admin.uexceptions.insufficientInformation, \
					 'superordinate object not present'
		if not dn and not position:
			raise univention.admin.uexceptions.insufficientInformation, \
					 'neither DN nor position present'

	def openSuperordinate(self):
		if self.superordinate:
			return

		self.open()
		serverdn = self.oldattr.get("ast4ucsSrvchildServer")
		if not serverdn:
			return

		if serverdn.__iter__:
			serverdn = serverdn[0]

		univention.admin.modules.update()
		servermod = univention.admin.modules.get("asterisk/server")
		univention.admin.modules.init(self.lo, self.position, servermod)
		self.superordinate = servermod.object(self.co, self.lo,
				self.position, serverdn)
		self.superordinate.open()

	def open(self):
		univention.admin.handlers.simpleLdap.open(self)
		reverseFieldsLoad(self)
		self.save()

	def _ldap_pre_create(self):
		super(object, self)._ldap_pre_create()
		reverseFieldsSave(self)
	
	def _ldap_pre_modify(self):
		super(object, self)._ldap_pre_modify()
		reverseFieldsSave(self)
	
	def _ldap_pre_remove(self):
		super(object, self)._ldap_pre_remove()
		self.open()
		self.info = {}
		reverseFieldsSave(self)
	
	def _ldap_addlist(self):
		return [('objectClass', ['ast4ucsWaitingloop']),
				('ast4ucsSrvchildServer', self.superordinate.dn)]


def lookup(co, lo, filter_s, base='', superordinate=None, scope='sub', 
		unique=False, required=False, timeout=-1, sizelimit=0):
	filter = univention.admin.filter.conjunction('&', [
		univention.admin.filter.expression(
			'objectClass', "ast4ucsWaitingloop")
	])

	if superordinate:
		filter.expressions.append(univention.admin.filter.expression(
				'ast4ucsSrvchildServer', superordinate.dn))
 
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
	return 'ast4ucsWaitingloop' in attr.get('objectClass', [])

