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
	reverseFieldsLoad, reverseFieldsSave, AsteriskBase
import univention.admin.syntax
from univention.admin.layout import Tab

module = "asterisk/phoneGroup"
short_description = u"Asterisk4UCS-Management: Telefongruppe"
operations = ['add', 'edit', 'remove', 'search', 'move']
options = {}

childs = 0
superordinate = "asterisk/server"

layout = [
	Tab('Allgemein', 'Allgemeine Einstellungen', layout = [
		[ "commonName", "id" ],
		[ "callphones" ],
		[ "pickupphones" ],
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
mapping.register("commonName", "cn",
	None, univention.admin.mapping.ListToString)
mapping.register("id", "ast4ucsPhonegroupId",
	None, univention.admin.mapping.ListToString)

class object(AsteriskBase):
	module=module

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
		return [('objectClass', ['ast4ucsPhonegroup']),
				('ast4ucsSrvchildServer', self.superordinate.dn)]


def lookup(co, lo, filter_s, base='', superordinate=None, scope='sub', 
		unique=False, required=False, timeout=-1, sizelimit=0):
	filter = univention.admin.filter.conjunction('&', [
		univention.admin.filter.expression(
			'objectClass', "ast4ucsPhonegroup")
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
	return 'ast4ucsPhonegroup' in attr.get('objectClass', [])

