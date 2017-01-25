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
import univention.admin.uexceptions
from univention.admin.layout import Tab
from univention.admin.handlers.asterisk import AsteriskBase

module = "asterisk/contact"
short_description = u"Asterisk4UCS-Management: Kontakt"
operations = ['add', 'edit', 'remove', 'search', 'move']
options = {}

childs = 0
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
		required=True,
		default="fubar",
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

class noNameError(univention.admin.uexceptions.insufficientInformation):
	message = (u"Eines der Felder Vorname, Nachname und Organisation "
			u"muss ausgefüllt sein.")

class object(AsteriskBase):
	module=module

	def __init__(self, co, lo, position, dn='', superordinate=None, attributes=None):
		if not superordinate and (dn or position):
			superordinate = univention.admin.objects.get_superordinate(self.module, co, lo, dn or position.getDn())
		super(object, self).__init__(co, lo, position, dn, superordinate, attributes)

	def openSuperordinate(self):
		if self.superordinate:
			self.superordinate.open()
			return

		pbdn = self.oldattr.get("ast4ucsPbchildPhonebook") or self.lo.getAttr(self.dn, "ast4ucsPbchildPhonebook")
		if not pbdn:
			return
		pbdn = pbdn[0]

		univention.admin.modules.update()
		pbmod = univention.admin.modules.get("asterisk/phoneBook")
		univention.admin.modules.init(self.lo, self.position, pbmod)
		self.superordinate = pbmod.object(self.co, self.lo, self.position, pbdn)
		self.superordinate.open()

	def _ldap_pre_ready(self):
		super(object, self)._ldap_pre_ready()
		orga = self.get("organisation")
		first = self.get("firstname")
		last = self.get("lastname")

		if first and last:
			name = "%s %s" % (first, last)
		elif last:
			name = last
		else:
			name = first  # could be string or None

		if orga and name:
			cn = "%s: %s" % (orga, name)
		elif orga:
			cn = orga
		else:
			cn = name  # could be string or None

		# if cn is None, all three fields were empty => error
		if not cn:
			raise noNameError

		self.info["commonName"] = cn

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

