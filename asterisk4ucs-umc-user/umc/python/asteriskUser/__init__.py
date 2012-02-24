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

import univention.management.console.modules
from univention.management.console.protocol.definitions import SUCCESS

import univention.config_registry
import univention.admin.uldap
import univention.admin.config
import univention.admin.modules
import univention.admin.handlers.users.user
import univention.admin.handlers.asterisk.sipPhone
import univention.admin.handlers.asterisk.mailbox

class Instance( univention.management.console.modules.Base ):
	def load( self, request ):
		user, mailbox = getUserAndMailbox(self._user_dn)

		result = {
			"phones/interval": user["ringdelay"],
			"forwarding/number": 42,

			"mailbox/timeout": user["timeout"],
			"mailbox": False,
		}

		if mailbox:
			result.update({
				"mailbox": True,
				"mailbox/password": mailbox["password"],
				"mailbox/email": mailbox["email"],
			})

		request.status = SUCCESS
		self.finished( request.id, result )

	def save( self, request ):
		user, mailbox = getUserAndMailbox(self._user_dn)

		user["ringdelay"] = request.options["phones/interval"]
		user["timeout"] = request.options["mailbox/timeout"]
		user.modify()

		if mailbox:
			mailbox["password"] = request.options[
							"mailbox/password"]
			mailbox["email"] = request.options["mailbox/email"]
			mailbox.modify()

		request.status = SUCCESS
		self.finished( request.id, "success",
			"Speichern war erfolgreich!" )

	def phonesQuery(self, request):
		phones = getPhones(self._user_dn)

		result = []
		for phone in phones:
			result.append({
				"extension": phone["extension"],
				"name": phone["name"],
			})

		request.status = SUCCESS
		self.finished(request.id, result)

def getCoLo():
	# create ldap connection
	ucr = univention.config_registry.ConfigRegistry()
	ucr.load()
	ldap_master = ucr.get('ldap/master', '')
	ldap_base = ucr.get('ldap/base', '')
	binddn = ','.join(('cn=admin', ldap_base))
	bindpw = open('/etc/ldap.secret','r').read().strip()
	lo = univention.admin.uldap.access(host=ldap_master, base=ldap_base,
		binddn=binddn, bindpw=bindpw, start_tls=2)

	co = univention.admin.config.config()
	return co, lo

def getUser(co, lo, dn):
	position = univention.admin.uldap.position(lo.base)

	univention.admin.modules.init(lo, position,
		univention.admin.handlers.users.user)

	return univention.admin.handlers.users.user.object(co, lo,
		None, dn)

def getPhone(co, lo, dn):
	return univention.admin.handlers.asterisk.sipPhone.object(co, lo,
		None, dn)

def getMailbox(co, lo, dn):
	return univention.admin.handlers.asterisk.mailbox.object(co, lo,
		None, dn)

def getPhones(userdn):
	co, lo = getCoLo()

	user = getUser(co, lo, userdn)

	phones = []
	for dn in user.get("phones", []):
		phones.append(getPhone(co, lo, dn))

	return phones

def getUserAndMailbox(userdn):
	co, lo = getCoLo()

	user = getUser(co, lo, userdn)

	mailbox = user.get("mailbox")
	if mailbox:
		mailbox = getMailbox(co, lo, mailbox)

	return user, mailbox

