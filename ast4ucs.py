#!/usr/bin/env python2
# coding=utf-8

"""
API zum unkomplizierten Erstellen neuer Asterisk4UCS-Kontakte

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

import re
import sys

import univention.admin.config
import univention.admin.uldap
import univention.admin.modules

co = univention.admin.config.config()
lo, pos = univention.admin.uldap.getAdminConnection()

univention.admin.modules.update()

udmPhonebook = univention.admin.modules.get("asterisk/phoneBook")
univention.admin.modules.init(lo, pos, udmPhonebook)

udmContact = univention.admin.modules.get("asterisk/contact")
univention.admin.modules.init(lo, pos, udmContact)

class phoneBookWrapper(object):
	"""Erlaubt einfachen Zugriff auf ein Asterisk4UCS-Telefonbuch"""

	def __init__(self, pbdn):
		"""Die __init__-Methode

		pbdn ist der DN des Telefonbuches im LDAP. (Kann z.B. per
		"udm asterisk/phoneBook list" ermittelt werden)"""

		self.pb = udmPhonebook.object(co, lo, None, pbdn)
		self.pb.open()
		if not self.pb.exists():
			raise Exception, "DN does not exist."

	def empty(self):
		"""Löscht alle Kontakte im Telefonbuch"""

		print ("Deleting all contacts in phonebook %s, "
				"may take a while...") % self.pb["commonName"]

		contacts = udmContact.lookup(co, lo, None,
				superordinate=self.pb)

		for contact in contacts:
			contact.remove()

		print "Deleted %i contacts." % len(contacts)

	def addContact(self, title=None, firstname=None, lastname=None,
			organisation=None,
			phones=None, mobiles=None, faxes=None):
		"""Fügt einen Kontakt hinzu

		Die Argumente sollten unbedingt als Keyword-Argumente
		übergeben werden, da sich die Reihenfolge der Argumente in
		Zukunft ändern kann.
		Leere Strings werden korrekt als nicht gesetzter Wert
		(ebenso wie None) behandelt. Phones, mobiles und faxes
		akzeptieren sowohl einen String als auch eine Liste von
		Strings.
		Der Rückgabewert ist der DN des neuen Kontakts."""

		contact = udmContact.object(co, lo,
				self.pb.position, None, self.pb)
		contact.open()

		if title:
			contact["title"] = title
		if firstname:
			contact["firstname"] = firstname
		if lastname:
			contact["lastname"] = lastname
		if organisation:
			contact["organisation"] = organisation

		if isinstance(phones, str):
			phones = [phones]
		if isinstance(mobiles, str):
			mobiles = [mobiles]
		if isinstance(faxes, str):
			faxes = [faxes]

		if phones:
			contact["telephoneNumber"] = filter(None, phones)
		if mobiles:
			contact["mobileNumber"] = filter(None, mobiles)
		if faxes:
			contact["faxNumber"] = filter(None, faxes)

		contact.create()
		return contact.dn

