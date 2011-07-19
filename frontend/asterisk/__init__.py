from univention.admin.handlers.asterisk import sipPhone, mailbox, phoneGroup
from univention.admin.handlers.users import user
import traceback
import re

def genSipconfEntry(co, lo, phone):
	phone = phone.info
	phoneUser = user.object(co, lo, None, phone["owner"]).info
	phoneMailbox = mailbox.object(co, lo, None, phone["mailbox"]).info
	
	callgroups = []
	for group in phone.get("phonegroups", []):
		group = phoneGroup.object(co, lo, None, group).info
		callgroups.append(group["commonName"])
	
	res  = "[%s]\n" % (phone["extension"])
	res += "type=friend\n"
	res += "secret=%s\n" % (phone["password"])
	res += "callerid=\"%s %s\" <%s>\n" % (
		phoneUser["firstname"],
		phoneUser["lastname"],
		phone["extension"] )
	res += "mailbox=%s\n" % (phoneMailbox["commonName"])
	res += "callgroup=%s\n" % (','.join(callgroups))
	res += "pickupgroup=%s\n" % (','.join(callgroups))
	return res

def genSipconf(co, lo):
	sipconf = open("/tmp/sip.conf", "w")
	print >> sipconf, "# Automatisch generierte sip.conf von asterisk4UCS"
	print >> sipconf, ""
	
	for phone in sipPhone.lookup(co, lo, False):
		print >> sipconf, "; dn=%s" % (phone.dn)
		try:
			print >> sipconf, genSipconfEntry(co, lo, phone)
		except:
			print >> sipconf, re.sub("(?m)^", ";",
				traceback.format_exc()[:-1] ) + "\n"
			#traceback.print_exc(file=sipconf)
	
	sipconf.close()


