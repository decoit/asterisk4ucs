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

module = "asterisk/fax"
short_description = u"Asterisk4UCS-Management: Fax"
operations = ['add', 'edit', 'remove', 'search', 'move']
options = {
	'default': univention.admin.option(
		short_description=short_description,
		default=True,
		objectClasses=['ast4ucsFax'],
	),
}
childs = False
superordinate = "asterisk/server"

layout = [
	Tab('Allgemein', 'Allgemeine Einstellungen', layout=[
		["extension", "ipaddress"],
		["macaddress", "hostname", ],
		["password"],
	])
]

property_descriptions = {
	"extension": univention.admin.property(
		short_description="Durchwahl",
		syntax=univention.admin.syntax.string,
		required=True,
		identifies=True,
	),
	"ipaddress": univention.admin.property(
		short_description="IP-Adresse",
		syntax=univention.admin.syntax.ipAddress,
	),
	"macaddress": univention.admin.property(
		short_description="MAC-Adresse",
		syntax=univention.admin.syntax.string
	),
	"hostname": univention.admin.property(
		short_description="Hostname",
		syntax=univention.admin.syntax.hostName
	),
	"password": univention.admin.property(
		short_description="Passwort",
		syntax=univention.admin.syntax.userPasswd,
		required=True,
	),
}

mapping = univention.admin.mapping.mapping()
mapping.register("extension", "ast4ucsExtensionExtension", None, univention.admin.mapping.ListToString)
mapping.register("ipaddress", "ast4ucsSipclientIp", None, univention.admin.mapping.ListToString)
mapping.register("macaddress", "ast4ucsSipclientMacaddr", None, univention.admin.mapping.ListToString)
mapping.register("hostname", "ast4ucsSipclientHostname", None, univention.admin.mapping.ListToString)
mapping.register("password", "ast4ucsSipclientSecret", None, univention.admin.mapping.ListToString)


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
