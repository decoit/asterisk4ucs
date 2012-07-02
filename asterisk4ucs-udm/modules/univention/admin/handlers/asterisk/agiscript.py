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

module = "asterisk/agiscript"
short_description = u"Asterisk: AGI-Script"
operations = ['add', 'edit', 'remove', 'search', 'move']
options = {}

childs = 0
usewizard = 1
superordinate = "asterisk/server"

layout = [
	Tab('Allgemein', 'Allgemeine Einstellungen', layout = [
		[ "name" ],
		[ "priority" ],
		[ "content" ],
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
mapping.register("name", "cn",
	None, univention.admin.mapping.ListToString)
mapping.register("priority", "ast4ucsAgiscriptPriority",
	None, univention.admin.mapping.ListToString)
mapping.register("content", "ast4ucsAgiscriptContent",
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

	def getContent(self):
		return self.get("content", "").decode("base64")

	def setContent(self,content):
		self["content"] = content.encode("base64").replace("\n","")

	def exists(self):
		return self._exists

	def open(self):
		univention.admin.handlers.simpleLdap.open(self)
		self.save()

	def _ldap_pre_create(self):
		self.dn = '%s=%s,%s' % (
			mapping.mapName('name'),
			mapping.mapValue('name', self.info['name']),
			self.position.getDn()
		)

	def _ldap_addlist(self):
		return [('objectClass', ['ast4ucsAgiscript' ]),
				('ast4ucsSrvchildServer', self.superordinate.dn)]


def lookup(co, lo, filter_s, base='', superordinate=None, scope='sub', 
		unique=False, required=False, timeout=-1, sizelimit=0):
	filter = univention.admin.filter.conjunction('&', [
		univention.admin.filter.expression(
			'objectClass', "ast4ucsAgiscript")
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
	return 'ast4ucsAgiscript' in attr.get('objectClass', [])

