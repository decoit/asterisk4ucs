# coding=utf-8

import univention.config_registry
import univention.admin.filter
import traceback
import re
import shutil
import time
import zlib

ucr = univention.config_registry.ConfigRegistry()

def getNameFromUser(userinfo):
	if userinfo.get("firstname"):
		return "%s %s" % (userinfo["firstname"], userinfo["lastname"])
	else:
		return userinfo["lastname"]

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
	res += "host=dynamic\n"
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

	conf = "; Automatisch generierte sip.conf von asterisk4UCS\n\n"

	for phone in sipPhone.lookup(co, lo, False):
		conf += "; dn: %s\n" % (phone.dn)
		try:
			conf += genSipconfEntry(co, lo, phone)
		except:
			conf += re.sub("(?m)^", ";",
				traceback.format_exc()[:-1] )
		conf += "\n"

	return conf

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

	conf = "; Automatisch generiert von Asterisk4UCS\n\n"

	conf += "[general]\n"
	conf += "maxsecs=%s\n" % (ucr.get(
				"asterisk/mailbox/maxlength", "120"))
	conf += "attach=%s\n" % (ucr.get(
				"asterisk/mailbox/attach", "yes"))
	conf += "emailsubject=%s\n" % (ucr.get(
				"asterisk/mailbox/emailsubject", "-"))
	conf += "emailbody=%s\n" % (ucr.get(
				"asterisk/mailbox/emailbody", "-"))
	conf += "emaildateformat=%s\n" % (ucr.get(
				"asterisk/mailbox/emaildateformat", "-"))
	conf += "mailcommand=%s\n" % (ucr.get(
				"asterisk/mailbox/mailcommand", "/bin/false"))
	conf += "\n"
	conf += "[default]\n"
	
	for box in mailbox.lookup(co, lo, False):
		conf += "; dn: %s\n" % (box.dn)
		try:
			conf += genVoicemailconfEntry(co, lo, box)
		except:
			conf += re.sub("(?m)^", ";",
				traceback.format_exc()[:-1] )
		conf += "\n"

	return conf

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

	conf = "; Automatisch generiert von Asterisk4UCS\n\n"
	
	for queue in waitingLoop.lookup(co, lo, False):
		conf += "; dn: %s\n" % (queue.dn)
		try:
			conf += genQueuesconfEntry(co, lo, queue)
		except:
			conf += re.sub("(?m)^", ";",
				traceback.format_exc()[:-1] )
		conf += "\n"

	return conf

def genMusiconholdconfEntry(co, lo, queue):
	queue = queue.info
	
	res  = "[%s]\n" % ( queue["delayMusic"] )
	res += "mode = files\n"
	res += "random = yes\n"
	res += "directory = %s\n" % ( queue["delayMusic"] )
	
	return res

def genMusiconholdconf(co, lo):
	import waitingLoop

	conf = "; Automatisch generiert von Asterisk4UCS\n\n"
	
	for queue in waitingLoop.lookup(co, lo, False):
		conf += "; dn: %s\n" % (queue.dn)
		try:
			conf += genMusiconholdconfEntry(co, lo, queue)
		except:
			conf += re.sub("(?m)^", ";",
				traceback.format_exc()[:-1] )
		conf += "\n"

	return conf

def genMeetmeconf(co, lo):
	import conferenceRoom

	conf = "; Automatisch generiert von Asterisk4UCS\n\n"

	for room in conferenceRoom.lookup(co, lo, False):
		conf += "; dn: %s\n" % (room.dn)
		try:
			conf += "conf => %s,%s,%s\n"%(
				room.info["extension"],
				room.info.get("pin", ""),
				room.info.get("adminPin", ""),
			)
		except:
			conf += re.sub("(?m)^", ";",
				traceback.format_exc()[:-1] )
		conf += "\n"

	return conf

def genExtSIPPhoneEntry(co, lo, phone):
	import mailbox
	phone = phone.info
	
	res  = "exten => %s,1,Dial(SIP/%s,%s)\n" % (
		phone["extension"],
		phone["extension"],
		phone.get("maxrings", "20"))
	
	if phone.get("mailbox"):
		phoneMailbox = mailbox.object(
			co, lo, None, phone["mailbox"]).info
		
		res += "exten => %s,2,Voicemail(%s,u)\n" % (
			phone["extension"],
			phoneMailbox["id"])
	
	return res

def genExtRoomEntry(co, lo, room):
	room = room.info
	
	res  = "exten => %s,1,Answer()\n" % (room["extension"])
	res += "exten => %s,n,Wait(1)\n" % (room["extension"])
	res += "exten => %s,n,MeetMe(%s)\n" % (
		room["extension"], room["extension"])
	res += "exten => %s,n,Hangup()\n" % (room["extension"])
	
	return res

def genExtQueueEntry(co, lo, queue):
	queue = queue.info
	
	res  = "exten => %s,1,Answer()\n" % (queue["extension"])
	res += "exten => %s,n,Queue(%s)\n" % (
		queue["extension"], queue["extension"])
	res += "exten => %s,n,Hangup()\n" % (queue["extension"])
	
	return res

def genExtensionsconf(co, lo):
	import sipPhone, conferenceRoom, waitingLoop

	conf = "; Automatisch generiert von Asterisk4UCS\n"

	conf += "\n\n; ===== Telefone =====\n\n"
	for phone in sipPhone.lookup(co, lo, False):
		conf += "; dn: %s\n" % (phone.dn)
		try:
			conf += genExtSIPPhoneEntry(co, lo, phone)
		except:
			conf += re.sub("(?m)^", ";",
				traceback.format_exc()[:-1] )
		conf += "\n"
	
	conf += "\n\n; ===== Konferenzräume =====\n\n"
	for room in conferenceRoom.lookup(co, lo, False):
		conf += "; dn: %s\n" % (room.dn)
		try:
			conf += genExtRoomEntry(co, lo, room)
		except:
			conf += re.sub("(?m)^", ";",
				traceback.format_exc()[:-1] )
		conf += "\n"

	conf += "\n\n; ===== Warteschleifen =====\n\n"
	for queue in waitingLoop.lookup(co, lo, False):
		conf += "; dn: %s\n" % (queue.dn)
		try:
			conf += genExtQueueEntry(co, lo, queue)
		except:
			conf += re.sub("(?m)^", ";",
				traceback.format_exc()[:-1] )
		conf += "\n"

	return conf

def genConfigs(co, lo):
	ucr.load()

	configs = {
		'sip.conf': genSipconf,
		'voicemail.conf': genVoicemailconf,
		'queues.conf': genQueuesconf,
		'musiconhold.conf': genMusiconholdconf,
		'meetme.conf': genMeetmeconf,
		'extensions.conf': genExtensionsconf,
	}

	res = []
	for filename,genfunc in configs.items():
		res.append("%s %s" % (filename,
			zlib.compress(genfunc(co, lo)).encode("base64")))
	return res


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

