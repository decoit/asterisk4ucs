import univention.config_registry
import univention.admin.filter
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
	from univention.admin.handlers.users import user
	import mailbox, phoneGroup
	phone = phone.info
	phoneUser = user.object(co, lo, None, phone["owner"]).info
	
	if phone.get("mailbox"):
		phoneMailbox = mailbox.object(co, lo, None,
			phone["mailbox"]).info
	
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
	
	if phone.get("mailbox"):
		res += "mailbox=%s\n" % (phoneMailbox["id"])

	if callgroups:
		res += "callgroup=%s\n" % (','.join(callgroups))

	if pickupgroups:
		res += "pickupgroup=%s\n" % (','.join(pickupgroups))
	
	return res

def genSipconf(co, lo):
	import sipPhone
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
	from univention.admin.handlers.users import user
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
	import mailbox
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

def genQueuesconfEntry(co, lo, queue):
	import sipPhone
	members = sipPhone.lookup(co, lo, "(%s=%s)" % (
		sipPhone.mapping.mapName("waitingloops"), queue.dn))
	queue = queue.info
	
	res  = "[%s]\n" % ( queue["extension"] )
	res += "strategy = %s\n" % ( queue["strategy"] )
	res += "maxlen = %s\n" % ( queue["maxCalls"] )
	res += "wrapuptime = %s\n" % ( queue["memberDelay"] )
	res += "musiconhold = %s\n" % ( queue["delayMusic"] )
	
	for member in members:
		res += "member => SIP/%s\n" % (member.info["extension"])
	
	return res

def genQueuesconf(co, lo):
	import waitingLoop
	confpath = ucr.get("asterisk/queuesconf", False)
	if not confpath: return
	conf = open(confpath, "w")
	print >> conf, "; Automatisch generierte queues.conf von Asterisk4UCS"
	print >> conf, ""
	print >> conf, "[general]"
	print >> conf, "persistentmembers = yes"
	print >> conf, ""
	
	for queue in waitingLoop.lookup(co, lo, False):
		print >> conf, "; dn: %s" % (queue.dn)
		try:
			print >> conf, genQueuesconfEntry(co, lo, queue)
		except:
			print >> conf, re.sub("(?m)^", ";",
				traceback.format_exc()[:-1] ) + "\n"
	
	conf.close()
	if ucr.get("asterisk/backupsuffix"):
		shutil.copyfile(confpath, confpath + time.strftime(
			ucr.get("asterisk/backupsuffix", "")))

def genMusiconholdconfEntry(co, lo, queue):
	queue = queue.info
	
	res  = "[%s]\n" % ( queue["delayMusic"] )
	res += "mode = files\n"
	res += "random = yes\n"
	res += "directory = %s\n" % ( queue["delayMusic"] )
	
	return res

def genMusiconholdconf(co, lo):
	import waitingLoop
	confpath = ucr.get("asterisk/musiconholdconf", False)
	if not confpath: return
	conf = open(confpath, "w")
	print >> conf, "; Automatisch generierte musiconhold.conf von"
	print >> conf, "; Asterisk4UCS"
	print >> conf, ""
	
	for queue in waitingLoop.lookup(co, lo, False):
		print >> conf, "; dn: %s" % (queue.dn)
		try:
			print >> conf, genMusiconholdconfEntry(co, lo, queue)
		except:
			print >> conf, re.sub("(?m)^", ";",
				traceback.format_exc()[:-1] ) + "\n"
	
	conf.close()
	if ucr.get("asterisk/backupsuffix"):
		shutil.copyfile(confpath, confpath + time.strftime(
			ucr.get("asterisk/backupsuffix", "")))

def genMeetmeconf(co, lo):
	import conferenceRoom
	confpath = ucr.get("asterisk/meetmeconf", False)
	if not confpath: return
	conf = open(confpath, "w")
	print >> conf, "; Automatisch generierte meetme.conf von Asterisk4UCS"
	print >> conf, ""
	print >> conf, "[rooms]"
	
	for room in conferenceRoom.lookup(co, lo, False):
		print >> conf, "; dn: %s" % (room.dn)
		try:
			print >> conf, "conf => %s,%s,%s"%(
				room.info["extension"],
				room.info.get("pin", ""),
				room.info.get("adminPin", ""),
			)
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
	genQueuesconf(co, lo)
	genMusiconholdconf(co, lo)
	genMeetmeconf(co, lo)
	
	callHook()

class ConfRefreshMixin:
	def _ldap_post_create(self):
		genConfigs(self.co, self.lo)
	
	def _ldap_post_modify(self):
		genConfigs(self.co, self.lo)
	
	def _ldap_post_remove(self):
		genConfigs(self.co, self.lo)

def reverseFieldsLoad(self):
	if not self.dn:
		return
	for field, foreignModule, foreignField in self.reverseFields:
		foreignModule = __import__("univention.admin.handlers.%s.%s" % (
			tuple(foreignModule.split("/"))), globals, locals,
			["lookup", "mapping"])
		objects = foreignModule.lookup(self.co, self.lo, "%s=%s" % (
			foreignModule.mapping.mapName(foreignField),
			univention.admin.filter.escapeForLdapFilter(self.dn),
		))
		self.info[field] = [obj.dn for obj in objects]

def reverseFieldsSave(self):
	if not self.dn:
		return
	for field, foreignModule, foreignField in self.reverseFields:
		foreignModule = __import__("univention.admin.handlers.%s.%s" % (
			tuple(foreignModule.split("/"))), globals, locals,
			["object"])
		oldset = set(self.oldinfo.get(field, []))
		newset = set(self.info.get(field, []))
		
		for dn in (oldset - newset):
			obj = foreignModule.object(self.co, self.lo, None, dn)
			obj.open()
			try:
				obj.info.get(foreignField, []).remove(self.dn)
			except ValueError:
				pass
			obj.modify()
		
		for dn in (newset - oldset):
			obj = foreignModule.object(self.co, self.lo, None, dn)
			obj.open()
			obj.info.setdefault(foreignField, []).append(self.dn)
			obj.modify()

