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

module = "asterisk/music"
short_description = u"Asterisk4UCS-Management: Warteschlangenmusik"
operations = ['add', 'edit', 'remove', 'search', 'move']
options = {}
options = {
	'default': univention.admin.option(
		short_description=short_description,
		default=True,
		objectClasses=['ast4ucsMusic'],
	),
}

childs = False
superordinate = "asterisk/server"

layout = [
	Tab('Allgemein', 'Allgemeine Einstellungen', layout=[
		["name", "music"],
	])
]

property_descriptions = {
	"name": univention.admin.property(
		short_description="Name",
		syntax=univention.admin.syntax.ast4ucsMusicNameSyntax,
		identifies=True,
		may_change=False,
	),
	"music": univention.admin.property(
		short_description="Musiken",
		syntax=univention.admin.syntax.string,
		multivalue=True,
		editable=False,
	),
}

mapping = univention.admin.mapping.mapping()
mapping.register("name", "cn", None, univention.admin.mapping.ListToString)
mapping.register("music", "ast4ucsMusicMusic", None, None)


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
