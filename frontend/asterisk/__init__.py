from univention.admin.handlers.asterisk import sipPhone, mailbox, phoneGroup
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
	
	debuglog = open("/tmp/debug", "w")
	#debuglog.close()
	Popen(ucr.get("asterisk/hookcommand").split(),
		stdout=debuglog, stderr=debuglog)
	#Popen([ucr.get("asterisk/hookcommand")])

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
	ucr.load()
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
	callHook()

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
	ucr.load()
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
	callHook()

def genConfigs(co, lo):
	pass


