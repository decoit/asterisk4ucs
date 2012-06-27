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

module = "asterisk/contact"
short_description = u"Asterisk: Kontakt"
operations = ['add', 'edit', 'remove', 'search', 'move']
options = {}

childs = 0
usewizard = 1
superordinate = "asterisk/phoneBook"

layout = [
	Tab('Allgemein', 'Allgemeine Kontaktdaten', layout = [
		[ 'title', 'firstname', 'lastname' ],
		[ 'organisation' ],
		[ 'telephoneNumber' ],
		[ 'mobileNumber' ],
		[ 'faxNumber' ],
	])
]

property_descriptions = {
	"commonName": univention.admin.property(
		short_description="Name",
		syntax=univention.admin.syntax.string,
		identifies=True,
		required=True
	),
	"firstname": univention.admin.property(
		short_description="Vorname",
		syntax=univention.admin.syntax.OneThirdString,
	),
	"lastname": univention.admin.property(
		short_description="Nachname",
		syntax=univention.admin.syntax.OneThirdString,
	),
	"title": univention.admin.property(
		short_description="Titel",
		syntax=univention.admin.syntax.OneThirdString,
	),
	"organisation": univention.admin.property(
		short_description="Organisation",
		syntax=univention.admin.syntax.string
	),
	"telephoneNumber": univention.admin.property(
		short_description="Telefonnummer",
		syntax=univention.admin.syntax.ast4ucsPhoneNumberSyntax,
		multivalue=True
	),
	"mobileNumber": univention.admin.property(
		short_description="Handynummer",
		syntax=univention.admin.syntax.ast4ucsPhoneNumberSyntax,
		multivalue=True
	),
	"faxNumber": univention.admin.property(
		short_description="Faxnummer",
		syntax=univention.admin.syntax.ast4ucsPhoneNumberSyntax,
		multivalue=True
	),
}

mapping = univention.admin.mapping.mapping()
mapping.register("commonName", "cn",
	None, univention.admin.mapping.ListToString)
mapping.register("firstname", "ast4ucsContactFirstname",
	None, univention.admin.mapping.ListToString)
mapping.register("lastname", "ast4ucsContactLastname",
	None, univention.admin.mapping.ListToString)
mapping.register("title", "title",
	None, univention.admin.mapping.ListToString)
mapping.register("organisation", "o",
	None, univention.admin.mapping.ListToString)
mapping.register("telephoneNumber", "telephoneNumber")
mapping.register("mobileNumber", "ast4ucsContactMobilenumber")
mapping.register("faxNumber", "ast4ucsContactFaxnumber")

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
		pbdn = self.oldattr.get("ast4ucsPbchildPhonebook")
		if not pbdn:
			return

		if pbdn.__iter__:
			pbdn = pbdn[0]

		univention.admin.modules.update()
		pbmod = univention.admin.modules.get("asterisk/phoneBook")
		univention.admin.modules.init(self.lo, self.position, pbmod)
		self.superordinate = pbmod.object(self.co, self.lo,
				self.position, pbdn)
		self.superordinate.open()

	def exists(self):
		return self._exists

	def open(self):
		univention.admin.handlers.simpleLdap.open(self)
		self.save()

	def _ldap_pre_ready(self):
		self["commonName"] = ("%s %s %s" % (
			self.get("firstname",""),
			self.get("lastname",""),
			self.get("organisation",""),
		)).strip()

	def _ldap_pre_create(self):
		self.dn = '%s=%s,%s' % (
			mapping.mapName('commonName'),
			mapping.mapValue('commonName', self.info['commonName']),
			self.position.getDn()
		)

	def _ldap_addlist(self):
		return [('objectClass', ['phonebookContact' ]),
				('ast4ucsPbchildPhonebook', self.superordinate.dn)]


def lookup(co, lo, filter_s, base='', superordinate=None, scope='sub', 
		unique=False, required=False, timeout=-1, sizelimit=0):
	filter = univention.admin.filter.conjunction('&', [
		univention.admin.filter.expression(
			'objectClass', "phonebookContact")
	])

	if superordinate:
		filter.expressions.append(univention.admin.filter.expression(
				'ast4ucsPbchildPhonebook', superordinate.dn))
 
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
	return 'phonebookContact' in attr.get('objectClass', [])

