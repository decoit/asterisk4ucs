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
	reverseFieldsLoad, reverseFieldsSave, simpleLdap
import univention.admin.syntax
from univention.admin.layout import Tab

module = "asterisk/phoneGroup"
short_description = u"Asterisk4UCS-Management: Telefongruppe"
operations = ['add', 'edit', 'remove', 'search', 'move']
options = {
	'default': univention.admin.option(
		short_description=short_description,
		default=True,
		objectClasses=['ast4ucsPhonegroup'],
	),
}

childs = False
superordinate = "asterisk/server"

layout = [
	Tab('Allgemein', 'Allgemeine Einstellungen', layout=[
		["commonName", "id"],
		["callphones"],
		["pickupphones"],
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
		short_description="Callgroup-Teilnehmer",
		syntax=univention.admin.syntax.LDAP_Search(
			filter="objectClass=ast4ucsPhone",
			attribute=['asterisk/sipPhone: extension'],
			value='asterisk/sipPhone: dn',
		),
		multivalue=True,
	),
	"pickupphones": univention.admin.property(
		short_description="Pickupgroup-Teilnehmer",
		syntax=univention.admin.syntax.LDAP_Search(
			filter="objectClass=ast4ucsPhone",
			attribute=['asterisk/sipPhone: extension'],
			value='asterisk/sipPhone: dn',
		),
		multivalue=True,
	),
}

mapping = univention.admin.mapping.mapping()
mapping.register("commonName", "cn", None, univention.admin.mapping.ListToString)
mapping.register("id", "ast4ucsPhonegroupId", None, univention.admin.mapping.ListToString)


class object(simpleLdap):
	module = module

	def __init__(self, co, lo, position, dn='', superordinate=None, attributes=None):
		self.reverseFields = [
			("pickupphones", "asterisk/sipPhone", "pickupgroups"),
			("callphones", "asterisk/sipPhone", "callgroups"),
		]
		super(object, self).__init__(co, lo, position, dn, superordinate=superordinate, attributes=attributes)

	def open(self):
		super(object, self).open()
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
		return [('ast4ucsSrvchildServer', self.superordinate.dn)]

	@classmethod
	def lookup_filter_superordinate(cls, filter, superordinate):
		filter.expressions.append(univention.admin.filter.expression('ast4ucsSrvchildServer', superordinate.dn, escape=True))
		return filter


lookup = object.lookup
lookup_filter = object.lookup_filter
identify = object.identify
