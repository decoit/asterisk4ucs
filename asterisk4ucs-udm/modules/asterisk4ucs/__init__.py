#!/usr/bin/env python3
# coding=utf-8

"""
Asterisk4UCS python API

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

import univention.admin.uldap
import univention.admin.modules


class PhoneBookWrapper(object):

	"""Erlaubt einfachen Schreibzugriff auf ein Asterisk4UCS-Telefonbuch"""

	def __init__(self, pbdn):
		"""Die __init__-Methode

		pbdn ist der DN des Telefonbuches im LDAP. (Kann z.B. per
		"udm asterisk/phoneBook list" ermittelt werden)"""

		self.lo, self.pos = univention.admin.uldap.getAdminConnection()

		univention.admin.modules.update()
		self.udmPhonebook = univention.admin.modules.get("asterisk/phoneBook")
		univention.admin.modules.init(self.lo, self.pos, self.udmPhonebook)
		self.udmContact = univention.admin.modules.get("asterisk/contact")
		univention.admin.modules.init(self.lo, self.pos, self.udmContact)

		self.pb = self.udmPhonebook.object(None, self.lo, None, pbdn)
		self.pb.open()
		if not self.pb.exists():
			raise Exception("DN does not exist.")

	def getName(self):
		"""Gibt den Namen des Telefonbuchs zurück"""

		return self.pb["commonName"]

	def empty(self):
		"""Löscht alle Kontakte im Telefonbuch"""

		contacts = self.udmContact.lookup(None, self.lo, None, superordinate=self.pb)

		for contact in contacts:
			contact.remove()

		return len(contacts)

	def addContact(self, title=None, firstname=None, lastname=None, organisation=None, phones=None, mobiles=None, faxes=None):
		"""Fügt einen Kontakt hinzu

		Die Argumente sollten unbedingt als Keyword-Argumente
		übergeben werden, da sich die Reihenfolge der Argumente in
		Zukunft ändern kann.
		Leere Strings werden korrekt als nicht gesetzter Wert
		(ebenso wie None) behandelt. Phones, mobiles und faxes
		akzeptieren sowohl einen String als auch eine Liste von
		Strings.
		Der Rückgabewert ist der DN des neuen Kontakts."""

		contact = self.udmContact.object(None, self.lo, self.pb.position, None, self.pb)
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
