from univention.admin.hook import simpleHook
from univention.admin.handlers.users import user
from univention.admin.filter import escapeForLdapFilter
from univention.admin import uexceptions

class AsteriskUsersUserHook(simpleHook):
	type='AsteriskUsersUserHook'
	class phoneError(uexceptions.base):
		message="A phone can't belong to more than one user: "

	class mailboxError(uexceptions.base):
		message="A mailbox can't belong to more than one user: "
	
	class faxError(uexceptions.base):
                message="A fax can't belong to more than one user: "

	
	def checkFields(self, module):
		def nameFromDn(dn):
			return dn.split(",")[0].split("=", 1)[1]

		for phonedn in module.info.get("phones", []):
			if not phonedn:
				continue
			phoneUsers = user.lookup(module.co, module.lo,
				"(&(ast4ucsUserPhone=%s)(!(uid=%s)))" % (
				escapeForLdapFilter(phonedn),
				escapeForLdapFilter(module.info["username"])))
			if phoneUsers:
				raise self.phoneError, (
					"%s belongs to %s!" % (
						nameFromDn(phonedn),
						nameFromDn(phoneUsers[0].dn)))

		mailboxdn = module.info.get("mailbox")
		if mailboxdn:
			mailboxUsers = user.lookup(module.co, module.lo,
				"(&(ast4ucsUserMailbox=%s)(!(uid=%s)))" % (
				escapeForLdapFilter(mailboxdn),
				escapeForLdapFilter(module.info["username"])))
			if mailboxUsers:
				raise self.mailboxError, (
					"%s belongs to %s!" % (
						nameFromDn(mailboxdn),
						nameFromDn(mailboxUsers[0].dn)))

                for faxdn in module.info.get("faxes", []):
                        if not faxdn:
                                continue
                        faxUsers = user.lookup(module.co, module.lo,
                                "(&(ast4ucsUserFax=%s)(!(uid=%s)))" % (
                                escapeForLdapFilter(faxdn),
                                escapeForLdapFilter(module.info["username"])))
                        if faxUsers:
                                raise self.faxError, (
                                        "%s belongs to %s!" % (
                                                nameFromDn(faxdn),
                                                nameFromDn(faxUsers[0].dn)))

		for faxgroupdn in module.info.get("faxgroups", []):
                        if not faxgroupdn:
                                continue
                        faxGroups = user.lookup(module.co, module.lo,
                                "(&(ast4ucsUserFaxgroup=%s)(!(uid=%s)))" % (
                                escapeForLdapFilter(faxgroupdn),
                                escapeForLdapFilter(module.info["username"])))
                        if faxGroups:
                                raise self.faxError, (
                                        "%s belongs to %s!" % (
                                                nameFromDn(faxgroupdn),
                                                nameFromDn(faxgroupUsers[0].dn)))


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

