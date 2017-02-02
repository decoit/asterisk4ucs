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
import univention.admin.syntax
from univention.admin.layout import Tab
from univention.admin import uexceptions
from univention.admin.handlers.asterisk import AsteriskBase

module = "asterisk/conferenceRoom"
short_description = u"Asterisk4UCS-Management: Konferenzraum"
operations = ['add', 'edit', 'remove', 'search', 'move']
options = {}

childs = 0
superordinate = "asterisk/server"

layout = [
	Tab('Allgemein', 'Allgemeine Einstellungen', layout=[
		["extension"],
		["maxMembers"],
		["pin", "adminPin"],
		["announceCount"],
		["initiallyMuted"],
		["musicOnHold"],
		["quietMode"],
	])
]

property_descriptions = {
	"extension": univention.admin.property(
		short_description="Durchwahl",
		syntax=univention.admin.syntax.string,
		identifies=True,
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
mapping.register("extension", "ast4ucsExtensionExtension",
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


class object(AsteriskBase):
	module = module

	def _ldap_pre_ready(self):
		super(object, self)._ldap_pre_ready()
		if self.info.get("pin"):
			if self.info.get("adminPin") == self.info["pin"]:
				class pinError(uexceptions.base):
					message = "Pin und Admin-Pin dürfen " +\
					"nicht übereinstimmen."
				raise pinError

	def _ldap_addlist(self):
		return [('objectClass', ['ast4ucsConfroom']),
				('ast4ucsSrvchildServer', self.superordinate.dn)]


def lookup(co, lo, filter_s, base='', superordinate=None, scope='sub',
		unique=False, required=False, timeout=-1, sizelimit=0):
	filter = univention.admin.filter.conjunction('&', [
		univention.admin.filter.expression(
			'objectClass', "ast4ucsConfroom")
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
	return 'ast4ucsConfroom' in attr.get('objectClass', [])
