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

def llist(thingie):
	"""Forces thingie to be a list.

	This should be used to work around univention's broken LDAP-module
	sometimes returning attribute values as a list of strings or a string
	depending on how many values an attribute has.

	llist("foo") -> ["foo"]
	llist(["foo", "bar"]) -> ["foo", "bar"]
	"""

	if isinstance(thingie, list):
		return thingie
	return list(thingie)

def genSipconfEntry(co, lo, phone):
	from univention.admin.handlers.users import user
	import mailbox, phoneGroup

	import univention.admin.modules
	univention.admin.modules.init(lo, phone.position, user)

	phoneUser = user.lookup(co, lo, "(ast4ucsUserPhone=%s)" % (
		univention.admin.filter.escapeForLdapFilter(phone.dn)))
	if len(phoneUser) != 1:
		return "; ERROR: Multiple or no users own this phone.\n"
	phoneUser = phoneUser[0].info

	phone = phone.info
	
	if phoneUser.get("mailbox"):
		phoneMailbox = mailbox.object(co, lo, None,
			phoneUser["mailbox"]).info
	
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

	if phoneUser.get("extmode") == "normal":
		res += "callerid=\"%s\" <%s>\n" % (
			getNameFromUser(phoneUser),
			phone["extension"] )
	elif phoneUser.get("extmode") == "first":
		firstPhone = sipPhone.object(co, lo, None,
			llist(phoneUser["phones"])[0]).info
		res += "callerid=\"%s\" <%s>\n" % (
			getNameFromUser(phoneUser),
			firstPhone["extension"] )

	if phoneUser.get("mailbox"):
		res += "mailbox=%s\n" % (phoneMailbox["id"])

	if callgroups:
		res += "callgroup=%s\n" % (','.join(callgroups))

	if pickupgroups:
		res += "pickupgroup=%s\n" % (','.join(pickupgroups))
	
	return res

def genSipconf(co, lo):
	import sipPhone

	conf = "; Automatisch generiert von asterisk4UCS\n\n"

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
	boxUser = user.lookup(co, lo, "(ast4ucsUserMailbox=%s)"%(
		univention.admin.filter.escapeForLdapFilter(box.dn)))
	if len(boxUser) != 1:
		return "; ERROR: Multiple or no users own this mailbox.\n"
	boxUser = boxUser[0].info
	
	box = box.info
	
	if box.get("email") == "1" and boxUser.get("e-mail"):
		return "%s => %s,%s,%s\n" % (
			box["id"],
			box["password"],
			getNameFromUser(boxUser),
			llist(boxUser["e-mail"])[0],
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

def genConfbridgeconf(co, lo):
	conf = "; Automatisch generiert von Asterisk4UCS\n\n"

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

def genExtSIPPhoneEntry(co, lo, extenPhone):
	from univention.admin.handlers.users import user
	import mailbox
	extension = extenPhone.info["extension"]

	import univention.admin.modules
	univention.admin.modules.init(lo, extenPhone.position, user)

	phoneUser = user.lookup(co, lo, "(ast4ucsUserPhone=%s)"%(
		univention.admin.filter.escapeForLdapFilter(extenPhone.dn)))
	if len(phoneUser) != 1:
		return "; ERROR: Multiple or no users own this phone.\n"
	phoneUser = phoneUser[0].info

	try:
		timeout = int(phoneUser["timeout"])
		if timeout < 1 or timeout > 120:
			raise Exception
	except:
		timeout = 10

	try:
		ringdelay = int(phoneUser["ringdelay"])
		if ringdelay < 1 or ringdelay > 120:
			raise Exception
	except:
		ringdelay = 0

	phones = [sipPhone.object(co, lo, None, dn).info["extension"]
		for dn in phoneUser.get("phones", [])]

	res = []

	if ringdelay:
		for phone in phones:
			res.append("Dial(SIP/%s,%i,tT)" % (phone, ringdelay))
			res.append("Wait(0.5)")
	else:
		res.append("Dial(%s,%i,tT)" % (
			'&'.join(["SIP/%s"%phone for phone in phones]),
			timeout))

	if phoneUser.get("mailbox"):
		phoneMailbox = mailbox.object(
			co, lo, None, phoneUser["mailbox"]).info
		res.append("Voicemail(%s,u)" % phoneMailbox["id"])

	return ''.join(["exten => %s,%i,%s\n"%(extension, i+1, data)
		for i,data in enumerate(res)])

def genExtRoomEntry(co, lo, room):
	room = room.info
	
	res  = "exten => %s,1,Answer()\n" % (room["extension"])
	res += "exten => %s,n,ConfBridge(%s)\n" % (
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
		'confbridge.conf': genConfbridgeconf,
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

