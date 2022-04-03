
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

from univention.admin.hook import simpleHook
from univention.admin.handlers.users import user
from univention.admin.filter import escapeForLdapFilter
from univention.admin import uexceptions


class AsteriskUsersUserHook(simpleHook):
	type = 'AsteriskUsersUserHook'

	class phoneError(uexceptions.valueError):
		_message = "The phone '%s' belongs to user '%s'."

		def __init__(self, *args):
			self.message = self._message % args

	class mailboxError(uexceptions.valueError):
		_message = "The mailbox '%s' belongs to user '%s'."

		def __init__(self, *args):
			self.message = self._message % args

	def checkFields(self, module):
		def nameFromDn(dn):
			return dn.split(",")[0].split("=", 1)[1]

		for phonedn in module.info.get("phones", []):
			if not phonedn:
				continue
			phoneUsers = user.lookup(module.co, module.lo, "(&(ast4ucsUserPhone=%s)(!(uid=%s)))" % (escapeForLdapFilter(phonedn), escapeForLdapFilter(module.info["username"])))
			if phoneUsers:
				raise self.phoneError(nameFromDn(phonedn), nameFromDn(phoneUsers[0].dn))

		mailboxdn = module.info.get("mailbox")
		if mailboxdn:
			mailboxUsers = user.lookup(module.co, module.lo, "(&(ast4ucsUserMailbox=%s)(!(uid=%s)))" % (escapeForLdapFilter(mailboxdn), escapeForLdapFilter(module.info["username"])))
			if mailboxUsers:
				raise self.mailboxError(nameFromDn(mailboxdn), nameFromDn(mailboxUsers[0].dn))

	def hook_ldap_pre_create(self, module):
		self.checkFields(module)

	def hook_ldap_pre_modify(self, module):
		self.checkFields(module)
