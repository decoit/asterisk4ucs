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

module = "asterisk/agiscript"
short_description = u"Asterisk4UCS-Management: AGI-Script"
operations = ['add', 'edit', 'remove', 'search', 'move']
options = {
	'default': univention.admin.option(
		short_description=short_description,
		default=True,
		objectClasses=['ast4ucsAgiscript'],
	),
}

childs = False
superordinate = "asterisk/server"

layout = [
	Tab('Allgemein', 'Allgemeine Einstellungen', layout=[
		["name"],
		["priority"],
		["content"],
	])
]

property_descriptions = {
	"name": univention.admin.property(
		short_description="Name",
		syntax=univention.admin.syntax.string_numbers_letters_dots,
		identifies=True,
		required=True,
	),
	"priority": univention.admin.property(
		short_description=u"Priorität",
		syntax=univention.admin.syntax.integer,
		required=True,
		default="1000",
	),
	"content": univention.admin.property(
		short_description=u"Script",
		syntax=univention.admin.syntax.Base64Upload,
		required=True,
	),
}

mapping = univention.admin.mapping.mapping()
mapping.register("name", "cn", None, univention.admin.mapping.ListToString)
mapping.register("priority", "ast4ucsAgiscriptPriority", None, univention.admin.mapping.ListToString)
mapping.register("content", "ast4ucsAgiscriptContent", None, univention.admin.mapping.ListToString)


class object(simpleLdap):
	module = module

	def getContent(self):
		return self.get("content", "").decode("base64")

	def setContent(self, content):
		self["content"] = content.encode("base64").replace("\n", "")

	def _ldap_addlist(self):
		return [('ast4ucsSrvchildServer', self.superordinate.dn)]

	@classmethod
	def lookup_filter_superordinate(cls, filter, superordinate):
		filter.expressions.append(univention.admin.filter.expression('ast4ucsSrvchildServer', superordinate.dn, escape=True))
		return filter


lookup = object.lookup
lookup_filter = object.lookup_filter
identify = object.identify
