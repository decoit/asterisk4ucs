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
from univention.admin.handlers import simpleLdap

module = "asterisk/phoneType"
short_description = u"Asterisk4UCS-Management: Telefontyp"
operations = ['add', 'edit', 'remove', 'search', 'move']
options = {}
options = {
	'default': univention.admin.option(
		short_description=short_description,
		default=True,
		objectClasses=['ast4ucsPhonetype'],
	),
}

childs = False
superordinate = "asterisk/server"

layout = [
	Tab('Allgemein', 'Allgemeine Kenndaten', layout=[
		["commonName"],
		["displaySize", "manufacturer"],
		["type"],
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
mapping.register("commonName", "cn", None, univention.admin.mapping.ListToString)
mapping.register("displaySize", "ast4ucsPhonetypeDisplaysize", None, univention.admin.mapping.ListToString)
mapping.register("manufacturer", "ast4ucsPhonetypeManufacturer", None, univention.admin.mapping.ListToString)
mapping.register("type", "ast4ucsPhonetypeType", None, univention.admin.mapping.ListToString)


class object(simpleLdap):
	module = module

	def _ldap_addlist(self):
		return [('ast4ucsSrvchildServer', self.superordinate.dn)]

	@classmethod
	def lookup_filter_superordinate(cls, filter, superordinate):
		filter.expressions.append(univention.admin.filter.expression('ast4ucsSrvchildServer', superordinate.dn, escape=True))
		return filter


lookup = object.lookup
lookup_filter = object.lookup_filter
identify = object.identify
