# imports for modules in univention.admin.handlers.asterisk are at the end of
# this file to avoid problems with circular imports
from univention.admin.handlers.users import user
import univention.config_registry
import traceback
import re
import shutil
import time
from subprocess import Popen

ucr = univention.config_registry.ConfigRegistry()

def getNameFromUser(userinfo):
	if userinfo.get("firstname"):
		return "%s %s" % (userinfo["firstname"], userinfo["lastname"])
	else:
		return userinfo["lastname"]

def callHook():
	if not ucr.get("asterisk/hookcommand"):
		return
	
	# The following call _does_ block until the child process exits.
	# ( Unexpected behavior, probably a bug )
	Popen(ucr.get("asterisk/hookcommand"), shell=True)

def genSipconfEntry(co, lo, phone):
	phone = phone.info
	phoneUser = user.object(co, lo, None, phone["owner"]).info
	phoneMailbox = mailbox.object(co, lo, None, phone["mailbox"]).info
	
	callgroups = []
	for group in phone.get("callgroups", []):
		group = phoneGroup.object(co, lo, None, group).info
		callgroups.append(group["id"])
	
	pickupgroups = []
	for group in phone.get("pickupgroups", []):
		group = phoneGroup.object(co, lo, None, group).info
		pickupgroups.append(group["id"])
	
	res  = "[%s]\n" % (phone["extension"])
	res += "type=friend\n"
	res += "secret=%s\n" % (phone["password"])
	res += "callerid=\"%s\" <%s>\n" % (
		getNameFromUser(phoneUser),
		phone["extension"] )
	res += "mailbox=%s\n" % (phoneMailbox["id"])

	if callgroups:
		res += "callgroup=%s\n" % (','.join(callgroups))

	if pickupgroups:
		res += "pickupgroup=%s\n" % (','.join(pickupgroups))
	
	return res

def genSipconf(co, lo):
	confpath = ucr.get("asterisk/sipconf", False)
	if not confpath:
		return
	conf = open(confpath, "w")
	print >> conf, "; Automatisch generierte sip.conf von asterisk4UCS"
	print >> conf, ""
	
	for phone in sipPhone.lookup(co, lo, False):
		print >> conf, "; dn: %s" % (phone.dn)
		try:
			print >> conf, genSipconfEntry(co, lo, phone)
		except:
			print >> conf, re.sub("(?m)^", ";",
				traceback.format_exc()[:-1] ) + "\n"
	
	conf.close()
	if ucr.get("asterisk/backupsuffix"):
		shutil.copyfile(confpath, confpath + time.strftime(
			ucr.get("asterisk/backupsuffix", "")))

def genVoicemailconfEntry(co, lo, box):
	box = box.info
	boxUser = user.object(co, lo, None, box["owner"]).info
	
	if box.get("email") and boxUser.get("e-mail", []):
		return "%s => %s,%s,%s\n" % (
			box["id"],
			box["password"],
			getNameFromUser(boxUser),
			boxUser["e-mail"][0],
		)
	else:
		return "%s => %s,%s\n" % (
			box["id"],
			box["password"],
			getNameFromUser(boxUser),
		)

def genVoicemailconf(co, lo):
	confpath = ucr.get("asterisk/voicemailconf", False)
	if not confpath: return
	conf = open(confpath, "w")
	print >> conf, "; Automatisch generierte voicemail.conf von"
	print >> conf, "; Asterisk4UCS"
	print >> conf, ""
	
	for box in mailbox.lookup(co, lo, False):
		print >> conf, "; dn: %s" % (box.dn)
		try:
			print >> conf, genVoicemailconfEntry(co, lo, box)
		except:
			print >> conf, re.sub("(?m)^", ";",
				traceback.format_exc()[:-1] ) + "\n"
	
	conf.close()
	if ucr.get("asterisk/backupsuffix"):
		shutil.copyfile(confpath, confpath + time.strftime(
			ucr.get("asterisk/backupsuffix", "")))

def genQueuesconfEntry(co, lo, box):
	box = box.info
	boxUser = user.object(co, lo, None, box["owner"]).info
	
	if box.get("email") and boxUser.get("e-mail", []):
		return "%s => %s,%s,%s\n" % (
			box["id"],
			box["password"],
			getNameFromUser(boxUser),
			boxUser["e-mail"][0],
		)
	else:
		return "%s => %s,%s\n" % (
			box["id"],
			box["password"],
			getNameFromUser(boxUser),
		)

def genQueuesconf(co, lo):
	confpath = ucr.get("asterisk/queuesconf", False)
	if not confpath: return
	conf = open(confpath, "w")
	print >> conf, "; Automatisch generierte queues.conf von Asterisk4UCS"
	print >> conf, ""
	
	for box in mailbox.lookup(co, lo, False):
		print >> conf, "; dn: %s" % (box.dn)
		try:
			print >> conf, genQueuesconfEntry(co, lo, box)
		except:
			print >> conf, re.sub("(?m)^", ";",
				traceback.format_exc()[:-1] ) + "\n"
	
	conf.close()
	if ucr.get("asterisk/backupsuffix"):
		shutil.copyfile(confpath, confpath + time.strftime(
			ucr.get("asterisk/backupsuffix", "")))

def genConfigs(co, lo):
	ucr.load()
	
	genSipconf(co, lo)
	genVoicemailconf(co, lo)
	
	callHook()

# def fubar(self):
# 	genConfigs(self.co, self.lo)
# 
# for foo in [sipPhone, mailbox, waitingLoop]:
# 	foo.object._ldap_post_create = fubar
# 	foo.object._ldap_post_modify = fubar
# 	foo.object._ldap_post_delete = fubar

class ConfRefreshMixin:
	def _ldap_post_create(self):
		genConfigs(self.co, self.lo)
	
	def _ldap_post_modify(self):
		genConfigs(self.co, self.lo)
	
	def _ldap_post_delete(self):
		genConfigs(self.co, self.lo)

import sipPhone, mailbox, phoneGroup, waitingLoop

 
