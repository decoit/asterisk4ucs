from univention.admin.hook import simpleHook
from univention.admin.handlers.users import user
from univention.admin.filter import escapeForLdapFilter
from univention.admin import uexceptions

class AsteriskUsersUserHook(simpleHook):
	type='AsteriskUsersUserHook'
	class phoneError(uexceptions.base):
		message="A phone can't belong to more than one user: "

	def checkFields(self, module):
		for phonedn in module.info.get("phones"):
			phoneUsers = user.lookup(module.co, module.lo,
				"(&(ast4ucsUserPhone=%s)(!(uid=%s)))" % (
				escapeForLdapFilter(phonedn),
				escapeForLdapFilter(module.info["username"])))
			if phoneUsers:
				raise self.phoneError, (
					"Phone %s belongs to %s!" % (
						phonedn, phoneUsers[0].dn))

	def hook_open(self, module):
		pass

	def hook_ldap_pre_create(self, module):
		self.checkFields(module)

	def hook_ldap_pre_modify(self, module):
		self.checkFields(module)

	def hook_ldap_pre_remove(self, module):
		pass

	def hook_ldap_addlist(self, module, al=[]):
		return al

	def hook_ldap_modlist(self, module, ml=[]):
		return ml

	def hook_ldap_post_create(self, module):
		pass

	def hook_ldap_post_modify(self, module):
		pass

	def hook_ldap_post_remove(self, module):
		pass

