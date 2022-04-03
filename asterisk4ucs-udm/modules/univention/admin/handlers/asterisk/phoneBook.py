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

module = "asterisk/phoneBook"
short_description = u"Asterisk4UCS-Management: Telefonbuch"
operations = ['add', 'edit', 'remove', 'search', 'move']
options = {
	'default': univention.admin.option(
		short_description=short_description,
		default=True,
		objectClasses=['ast4ucsPhonebook'],
	),
}

childs = False
childmodules = ["asterisk/contact"]

layout = [
	Tab('Allgemein', 'Allgemeine Einstellungen', layout=[
		['commonName'],
	]),
]

property_descriptions = {
	"commonName": univention.admin.property(
		short_description="Name",
		syntax=univention.admin.syntax.string_numbers_letters_dots,
		identifies=True,
		required=True
	),
}

mapping = univention.admin.mapping.mapping()
mapping.register("commonName", "cn", None, univention.admin.mapping.ListToString)


class object(univention.admin.handlers.simpleLdap):
	module = module


lookup = object.lookup
lookup_filter = object.lookup_filter
identify = object.identify
