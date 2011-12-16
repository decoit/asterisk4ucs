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
	return [ thingie ]

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

def genSipconfFaxEntry(co, lo, phone):
	res  = "[%s]\n" % (phone["extension"])
	res += "type=friend\n"
	res += "host=dynamic\n"
	res += "secret=%s\n" % (phone["password"])
	return res

def genSipconf(co, lo, srv):
	import sipPhone, fax, faxGroup

	conf = "; Automatisch generiert von asterisk4UCS\n\n"

	conf += "\n\n; ===== Phones =====\n\n"
	for phone in sipPhone.lookup(co, lo, False):
		conf += "; dn: %s\n" % (phone.dn)
		try:
			conf += genSipconfEntry(co, lo, phone)
		except:
			conf += re.sub("(?m)^", ";",
				traceback.format_exc()[:-1] )
		conf += "\n"

	conf += "\n\n; ===== Faxes =====\n\n"
	for phone in fax.lookup(co, lo, False):
		conf += "; dn: %s\n" % (phone.dn)
		try:
			conf += genSipconfFaxEntry(co, lo, phone)
		except:
			conf += re.sub("(?m)^", ";",
				traceback.format_exc()[:-1] )
		conf += "\n"
	
	conf +="\n\n; ===== FaxGroups =====\n\n"
	for phone in faxGroup.lookup(co, lo, False):
		conf += "; dn: %s\n" % (phone.dn)

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

def genVoicemailconf(co, lo, srv):
	import mailbox

	conf = "; Automatisch generiert von Asterisk4UCS\n\n"

	conf += "[general]\n"
	conf += "maxsecs=%s\n" % (srv.info["mailboxMaxlength"])
	conf += "emailsubject=%s\n" % (srv.info["mailboxEmailsubject"])
	conf += "emailbody=%s\n" % (srv.info["mailboxEmailbody"])
	conf += "emaildateformat=%s\n" % (srv.info["mailboxEmaildateformat"])
	conf += "mailcommand=%s\n" % (srv.info["mailboxMailcommand"])
	if "1" in srv.info["mailboxAttach"]:
		conf += "attach=yes\n"
	else:
		conf += "attach=no\n"
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

def genQueuesconf(co, lo, srv):
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

def genMusiconholdconf(co, lo, srv):
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

  	try:
                globalForward = int(phoneUser["forwarding"])
                if globalForward < 0:
                        raise Exception
        except:
                globalForward = 0


	phones = [sipPhone.object(co, lo, None, dn)
		for dn in phoneUser.get("phones", [])]

	res = []

	if phones:
		if ringdelay:
			counter = 1;
			for phone in phones:
				phoneForward = phone.info.get("forward","")
				if globalForward:
					res.append("Dial(SIP/%s,%i,tT)" % (globalForward, ringdelay))
				elif phoneForward:
					res.append("Dial(SIP/%s,%i,tT)" % (phoneForward, ringdelay))
				else:
					res.append("Dial(SIP/%s,%i,tT)" % (phone.info["extension"], ringdelay))
		
				if (globalForward):
					break

				if (counter < len(phones)):
					res.append("Wait(0.5)")

				counter += 1

		else:
			mergedExtensions = ""
                        for phone in phones:
                                currentExtension = ""
                                phoneForward = phone.info.get("forward","")
                                if globalForward:
                                        currentExtension = str(globalForward)
                                elif phoneForward != "":
                                        currentExtension = phoneForward
                                else:
                                        currentExtension = phone.info["extension"]

                                if mergedExtensions == "":
                                        mergedExtensions += 'SIP/' + currentExtension
                                else:
                                        mergedExtensions += '&SIP/' + currentExtension

                                if globalForward:
                                        break

                        res.append("Dial(%s,%i,tT)" % (mergedExtensions,timeout))


	if phoneUser.get("mailbox"):
		phoneMailbox = mailbox.object(
			co, lo, None, phoneUser["mailbox"]).info
		res.append("Voicemail(%s,u)" % phoneMailbox["id"])

	return ''.join(["exten => %s,%i,%s\n"%(extension, i+1, data)
		for i,data in enumerate(res)])

def genExtRoomEntry(co, lo, room):
	room = room.info

	flags = "s"
	if room.get("announceCount") == "1":
		flags += "c"
	if room.get("initiallyMuted") == "1":
		flags += "m"
	if room.get("quietMode") == "1":
		flags += "q"
	if room.get("musicOnHold") == "1":
		flags += "M"

	try:
		maxusers = int(room.get("maxMembers", "foo"))
	except ValueError:
		maxusers = 100

	res  = "exten => %s1,1,Answer()\n" % (room["extension"])
	res += "exten => %s1,n,Set(GROUP()=conf_%s)\n" % (
		room["extension"], room["extension"])
	res += "exten => %s1,n,GotoIf($[ ${GROUP_COUNT()} > %i ]?limit)\n" % (
		room["extension"], maxusers)
	res += "exten => %s1,n,Authenticate(%s,,%i)\n" % (
		room["extension"], room["adminPin"], len(room["adminPin"]))
	res += "exten => %s1,n,ConfBridge(%s,a%s)\n" % (
		room["extension"], room["extension"], flags)
	res += "exten => %s1,n,Hangup()\n" % (room["extension"])
	res += "exten => %s1,n(limit),Playback(denial-of-service)\n" % (
		room["extension"])
	res += "exten => %s1,n,Congestion()\n" % (
		room["extension"])
	res += "; -------\n"
	res += "exten => %s,1,Answer()\n" % (room["extension"])
	res += "exten => %s,n,Set(GROUP()=conf_%s)\n" % (
		room["extension"], room["extension"])
	res += "exten => %s,n,GotoIf($[ ${GROUP_COUNT()} > %i ]?limit)\n" % (
		room["extension"], maxusers)
	res += "exten => %s,n,Authenticate(%s,,%i)\n" % (
		room["extension"], room["pin"], len(room["pin"]))
	res += "exten => %s,n,ConfBridge(%s,%s)\n" % (
		room["extension"], room["extension"], flags)
	res += "exten => %s,n,Hangup()\n" % (room["extension"])
	res += "exten => %s,n(limit),Playback(denial-of-service)\n" % (
		room["extension"])
	res += "exten => %s,n,Congestion()\n" % (
		room["extension"])

	return res

def genExtQueueEntry(co, lo, queue):
	queue = queue.info
	
	res  = "exten => %s,1,Answer()\n" % (queue["extension"])
	res += "exten => %s,n,Queue(%s)\n" % (
		queue["extension"], queue["extension"])
	res += "exten => %s,n,Hangup()\n" % (queue["extension"])
	
	return res

def genExtensionsconf(co, lo, srv):
	import sipPhone, conferenceRoom, waitingLoop

	conf = "; Automatisch generiert von Asterisk4UCS\n"

	conf += "\n[default]\n"

	if (srv["globalCallId"]):
		conf += "\n;globale Rufnummer fuer alle ausgehenden Anrufe\n"
		conf += ";exten => _0.,1,CALLERID(all," + srv["globalCallId"] + ")\n"
		conf += ";exten => _0.,n,Dial(SIP/${EXTEN:1})\n"

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

	conf += "\n\n; ===== Blockierte Vorwahlen =====\n\n"
	for areaCode in srv.info.get("blockedAreaCodes", []):
		conf += "exten => _%s.,1,Hangup()\n" % (areaCode)

	conf += "\n\n; ===== Faxe =====\n\n"
	for phone in fax.lookup(co, lo, False):
		conf += "exten => %s,1,Dial(SIP/%s)\n" % (
			phone.info["extension"],
			phone.info["extension"])

	conf += "\n[extern-incoming]\n"

	conf += "\n\n; ===== Nummernkreise =====\n\n"
	for extnum in llist(srv.info.get("extnums", [])):
		conf += "exten => _%s,1,Goto(default,%s,1)\n" % (
			extnum, srv.info.get("defaultext", "fubar"))
		conf += "exten => _%s.,1,Goto(default,${EXTEN:%i},1)\n" % (
			extnum, len(extnum))

	return conf

def genConfigs(co, lo, server):
	ucr.load()

	configs = {
		'sip.conf': genSipconf,
		'voicemail.conf': genVoicemailconf,
		'queues.conf': genQueuesconf,
		'musiconhold.conf': genMusiconholdconf,
		'extensions.conf': genExtensionsconf,
	}

	res = []
	for filename,genfunc in configs.items():
		res.append("%s %s" % (filename,
			zlib.compress(genfunc(co, lo, server)).encode("base64")))
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

