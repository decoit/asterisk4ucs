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

from univention.management.console.base import Base, UMC_Error
from univention.management.console.log import MODULE

import univention.config_registry
import univention.admin.uldap
import univention.admin.modules

import univention.admin.handlers.users.user
import univention.admin.handlers.asterisk.sipPhone
import univention.admin.handlers.asterisk.mailbox
import univention.admin.handlers.asterisk.server

univention.admin.modules.update()


class Instance(Base):

	def load(self, request):
		user, mailbox = getUserAndMailbox(self._user_dn)
		raise UMC_Error("Es wurde kein Asterisk-Server angelegt!")
		result = {
			"phones/interval": user["ringdelay"],
			"forwarding/number": user.get("forwarding", ""),

			"mailbox/timeout": user["timeout"],
			"mailbox": False,
		}

		if mailbox:
			result.update({
				"mailbox": True,
				"mailbox/password": mailbox["password"],
				"mailbox/email": mailbox["email"],
			})

		self.finished(request.id, result)

	def save(self, request):
		user, mailbox = getUserAndMailbox(self._user_dn)

		user["ringdelay"] = request.options["phones/interval"]
		user["timeout"] = request.options["mailbox/timeout"]
		if request.options["forwarding/number"]:
			user["forwarding"] = request.options["forwarding/number"]
		else:
			try:
				del user.info["forwarding"]
			except KeyError:
				pass
		user.modify()

		if mailbox:
			mailbox["password"] = request.options["mailbox/password"]
			mailbox["email"] = request.options["mailbox/email"]
			mailbox.modify()

		self.finished(request.id, None, "Speichern war erfolgreich!")

	def phonesQuery(self, request):
		if (request.options.get("dn") and request.options.get("position") in ["-1", "1"]):
			changePhoneOrder(self._user_dn, request.options["dn"], int(request.options["position"]))

		phones = getPhones(self._user_dn)

		result = []
		for i, phone in enumerate(phones):
			result.append({
				"position": i,
				"dn": phone.dn,
				"name": phone["extension"],
			})

		self.finished(request.id, result)


def getCoLo():
	lo = univention.admin.uldap.getAdminConnection()[0]
	co = None
	return co, lo


def getUser(co, lo, dn):
	position = univention.admin.uldap.position(lo.base)

	univention.admin.modules.init(lo, position, univention.admin.handlers.users.user)

	obj = univention.admin.handlers.users.user.object(co, lo, None, dn)
	obj.open()
	return obj


def getPhone(co, lo, dn):
	obj = univention.admin.handlers.asterisk.sipPhone.object(co, lo, None, dn)
	obj.open()
	return obj


def getMailbox(co, lo, dn):
	obj = univention.admin.handlers.asterisk.mailbox.object(co, lo, None, dn)
	obj.open()
	return obj


def getPhones(userdn):
	co, lo = getCoLo()

	user = getUser(co, lo, userdn)

	phones = []
	for dn in user.get("phones", []):
		phones.append(getPhone(co, lo, dn))

	return phones


def getUserAndMailbox(userdn):
	co, lo, pos = getCoLoPos()

	server = univention.admin.modules.get("asterisk/server")
	univention.admin.modules.init(lo, pos, server)
	objs = server.lookup(co, lo, None)

	checkServers = []
	for obj in objs:
		checkServers.append({
			"label": obj["commonName"],
		})

	MODULE.error('User: server: %s' % len(checkServers))
	if checkServers:
		co, lo = getCoLo()

		user = getUser(co, lo, userdn)

		mailbox = user.get("mailbox")
		if mailbox:
			mailbox = getMailbox(co, lo, mailbox)

		return user, mailbox
	else:
		MODULE.error('Fehler gefunden!')
		mailbox = "KeinServer"
		user = "KeinServer"
		return user, mailbox


def getCoLoPos():
	co = None
	lo, pos = univention.admin.uldap.getAdminConnection()
	return co, lo, pos


def changePhoneOrder(userdn, phonedn, change):
	co, lo = getCoLo()

	user = getUser(co, lo, userdn)

	phones = user.get("phones", [])
	i = phones.index(phonedn)
	phones.pop(i)
	if change == -1 and i > 0:
		phones.insert(i - 1, phonedn)
	elif change == 1:
		phones.insert(i + 1, phonedn)

	user["phones"] = phones
	user.modify()
