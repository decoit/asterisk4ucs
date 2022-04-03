# coding=utf-8

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
from univention.management.console.log import MODULE
import univention.config_registry
import univention.admin.filter
import univention.admin.modules
import univention.admin.handlers
import traceback
import re
from ldap.filter import filter_format

#logfile = "/var/log/univention/asteriskMusicPython.log"
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
	return [thingie]


def genSipconfEntry(co, lo, phone):
	from univention.admin.handlers.users import user
	from univention.admin.handlers.asterisk import sipPhone, mailbox, phoneGroup

	import univention.admin.modules
	univention.admin.modules.init(lo, phone.position, user)

	phoneUser = user.lookup(co, lo, filter_format("(ast4ucsUserPhone=%s)", (phone.dn,)))
	if len(phoneUser) == 0:
		return ";; Phone %s has no user.\n" % phone["extension"]
	if len(phoneUser) > 1:
		msg = ";; Phone %s has multiple users:\n" % phone["extension"]
		for userObj in phoneUser:
			msg += ";;   * %s\n" % userObj["username"]
	phoneUser = phoneUser[0].info

	phone = phone.info

	if phoneUser.get("mailbox"):
		phoneMailbox = mailbox.object(co, lo, None, phoneUser["mailbox"]).info

	callgroups = []
	for group in phone.get("callgroups", []):
		group = phoneGroup.object(co, lo, None, group).info
		callgroups.append(group["id"])

	pickupgroups = []
	for group in phone.get("pickupgroups", []):
		group = phoneGroup.object(co, lo, None, group).info
		pickupgroups.append(group["id"])

	res = "[%s](template-%s)\n" % (phone["extension"], phone.get("profile", "default"))
	res += "secret=%s\n" % (phone["password"])

	if phoneUser.get("extmode") == "normal":
		res += "callerid=\"%s\" <%s>\n" % (
			getNameFromUser(phoneUser),
			phone["extension"])
	elif phoneUser.get("extmode") == "first":
		firstPhone = sipPhone.object(co, lo, None, llist(phoneUser["phones"])[0]).info
		res += "callerid=\"%s\" <%s>\n" % (
			getNameFromUser(phoneUser),
			firstPhone["extension"])

	if phoneUser.get("mailbox"):
		res += "mailbox=%s\n" % (phoneMailbox["id"])

	if callgroups:
		res += "callgroup=%s\n" % (','.join(callgroups))

	if pickupgroups:
		res += "pickupgroup=%s\n" % (','.join(pickupgroups))

	return res


def genSipconfFaxEntry(co, lo, phone):
	res = "[%s]\n" % (phone["extension"])
	res += "type=friend\n"
	res += "host=dynamic\n"
	res += "secret=%s\n" % (phone["password"])
	return res


def genSipconf(co, lo, srv):
	from univention.admin.handlers.asterisk import sipPhone, fax

	conf = "; Automatisch generiert von asterisk4UCS\n"
	conf += "\n"
	conf += "[general]\n"
	conf += "allowsubscribe = yes\n"
	conf += "notifyringing = yes\n"
	conf += "notifyhold = yes\n"
	conf += "limitonpeers = yes\n"
	conf += "\n"
	conf += "[template-default](!)\n"
	conf += "type=friend\n"
	conf += "host=dynamic\n"
	conf += "subscribecontext=default\n"
	conf += "call-limit=10\n"
	conf += "\n"

	conf += "\n\n; ===== Phones =====\n\n"
	for phone in sipPhone.lookup(co, lo, False):
		conf += "; dn: %s\n" % (phone.dn)
		try:
			conf += genSipconfEntry(co, lo, phone)
		except Exception:
			conf += re.sub("(?m)^", ";", traceback.format_exc()[:-1])
		conf += "\n"

	conf += "\n\n; ===== Fax machines =====\n\n"
	for phone in fax.lookup(co, lo, False):
		conf += "; dn: %s\n" % (phone.dn)
		try:
			conf += genSipconfFaxEntry(co, lo, phone)
		except Exception:
			conf += re.sub("(?m)^", ";", traceback.format_exc()[:-1])
		conf += "\n"

	return conf


def genVoicemailconfEntry(co, lo, box):
	from univention.admin.handlers.users import user
	boxUser = user.lookup(co, lo, filter_format("(ast4ucsUserMailbox=%s)", (box.dn,)))
	if len(boxUser) == 0:
		return ";; Mailbox %s has no user.\n" % box["id"]
	if len(boxUser) > 1:
		msg = ";; Mailbox %s has multiple users:\n" % box["id"]
		for userObj in boxUser:
			msg += ";;   * %s\n" % userObj["username"]
	boxUser = boxUser[0].info

	box = box.info

	if box.get("email") == "1" and boxUser.get("mailPrimaryAddress"):
		return "%s => %s,%s,%s\n" % (
			box["id"],
			box["password"],
			getNameFromUser(boxUser),
			llist(boxUser["mailPrimaryAddress"])[0],
		)
	else:
		return "%s => %s,%s\n" % (
			box["id"],
			box["password"],
			getNameFromUser(boxUser),
		)


def genVoicemailconf(co, lo, srv):
	from univention.admin.handlers.asterisk import mailbox

	conf = "; Automatisch generiert von Asterisk4UCS\n\n"

	conf += "[general]\n"
	conf += "maxsecs=%s\n" % (srv.info["mailboxMaxlength"])
	conf += "emailsubject=%s\n" % (srv.info["mailboxEmailsubject"])
	conf += "emailbody=%s\n" % (srv.info["mailboxEmailbody"].replace("\n", "\\n"))
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
		except Exception:
			conf += re.sub("(?m)^", ";", traceback.format_exc()[:-1])
		conf += "\n"

	return conf


def genQueuesconfEntry(co, lo, queue):
	from univention.admin.handlers.asterisk import sipPhone
	members = sipPhone.lookup(co, lo, "(%s=%s)" % (
		sipPhone.mapping.mapName("waitingloops"), queue.dn))
	queue = queue.info

	res = "[%s]\n" % (queue["extension"])
	res += "strategy = %s\n" % (queue["strategy"])
	res += "maxlen = %s\n" % (queue["maxCalls"])
	res += "wrapuptime = %s\n" % (queue["memberDelay"])
	res += "musiconhold = %s\n" % (queue["delayMusic"])

	for member in members:
		res += "member => SIP/%s\n" % (member.info["extension"])

	return res


def genQueuesconf(co, lo, srv):
	from univention.admin.handlers.asterisk import waitingLoop

	conf = "; Automatisch generiert von Asterisk4UCS\n\n"

	for queue in waitingLoop.lookup(co, lo, False):
		conf += "; dn: %s\n" % (queue.dn)
		try:
			conf += genQueuesconfEntry(co, lo, queue)
		except Exception:
			conf += re.sub("(?m)^", ";", traceback.format_exc()[:-1])
		conf += "\n"

	return conf


def genMusiconholdconfEntry(co, lo, srv, moh):
	moh = moh.info

	if moh["name"] == "default":
		return "; ignoring the 'default' class\n"

	res = "[%s]\n" % (moh["name"])
	res += "mode = files\n"
	res += "random = yes\n"
	res += "directory = %s/%s\n" % (srv["sshmohpath"], moh["name"])

	return res


def genMusiconholdconf(co, lo, srv):
	from univention.admin.handlers.asterisk import music

	conf = "; Automatisch generiert von Asterisk4UCS\n\n"

	for moh in music.lookup(co, lo, False):
		conf += "; dn: %s\n" % (moh.dn)
		try:
			conf += genMusiconholdconfEntry(co, lo, srv, moh)
		except Exception:
			conf += re.sub("(?m)^", ";", traceback.format_exc()[:-1])
		conf += "\n"

	return conf


def genExtSIPPhoneEntry(co, lo, agis, extenPhone):
	extension = extenPhone.info["extension"]

	# check if this phone is managed manually (not by ast4ucs)
	if extenPhone.get("skipExtension") == "1":
		return ";; Extension %s is managed manually.\n" % (extenPhone["extension"],)

	from univention.admin.handlers.users import user
	from univention.admin.handlers.asterisk import sipPhone, mailbox

	import univention.admin.modules
	univention.admin.modules.init(lo, extenPhone.position, user)

	phoneUser = user.lookup(co, lo, filter_format("(ast4ucsUserPhone=%s)", (extenPhone.dn,)))
	if len(phoneUser) == 0:
		return ";; Phone %s has no user.\n" % extenPhone["extension"]
	if len(phoneUser) > 1:
		msg = ";; Phone %s has multiple users:\n" % extenPhone["extension"]
		for userObj in phoneUser:
			msg += ";;   * %s\n" % userObj["username"]
	phoneUser = phoneUser[0].info

	try:
		timeout = int(phoneUser["timeout"])
		if timeout < 1 or timeout > 120:
			raise ValueError()
	except ValueError:
		timeout = 10

	try:
		ringdelay = int(phoneUser["ringdelay"])
		if ringdelay < 1 or ringdelay > 120:
			raise ValueError()
	except ValueError:
		ringdelay = 0

	channels = []
	hints = []
	for dn in phoneUser.get("phones", []):
		phone = sipPhone.object(co, lo, extenPhone.position, dn, extenPhone.superordinate)
		hints.append("SIP/%s" % phone["extension"])
		if phone.get("forwarding"):
			channels.append("Local/%s" % phone["forwarding"])
		else:
			channels.append("SIP/%s" % phone["extension"])

	res = []

	# copy agis into res
	for agi in agis:
		res.append(agi)

	if channels:
		if ringdelay:
			for channel in channels[:-1]:
				res.append("Dial(%s,%i,tT)" % (channel, ringdelay))
				res.append("Wait(0.5)")
			res.append("Dial(%s,%i,tT)" % (channels[-1], timeout))
		else:
			res.append("Dial(%s,%i,tT)" % (
				'&'.join(channels), timeout))

	if phoneUser.get("mailbox"):
		phoneMailbox = mailbox.object(
			co, lo, None, phoneUser["mailbox"]).info
		res.append("Voicemail(%s,u)" % phoneMailbox["id"])

	if phoneUser.get("forwarding"):
		res = ["Dial(Local/%s,,tT)" % phoneUser["forwarding"]]

	resStr = ""
	if hints:
		resStr += "exten => %s,hint,%s\n" % (extension, '&'.join(hints))
	for i, data in enumerate(res):
		resStr += "exten => %s,%i,%s\n" % (extension, i + 1, data)

	return resStr


def genExtRoomEntry(co, lo, agis, room):
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

	res = ""
	for i, agi in enumerate(agis):
		res += "exten => %s1,%i,%s\n" % (
			room["extension"],
			i + 1,
			agi
		)
		res += "exten => %s,%i,%s\n" % (
			room["extension"],
			i + 1,
			agi
		)
	res += "exten => %s1,%i,Answer()\n" % (
		room["extension"], len(agis) + 1)
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
	res += "exten => %s,%i,Answer()\n" % (
		room["extension"], len(agis) + 1)
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


def genExtQueueEntry(co, lo, agis, queue):
	queue = queue.info

	res = ""
	for i, agi in enumerate(agis):
		res += "exten => %s,%i,%s\n" % (
			queue["extension"],
			i + 1,
			agi
		)
	res += "exten => %s,%i,Answer()\n" % (
		queue["extension"], len(agis) + 1)
	res += "exten => %s,n,Queue(%s)\n" % (
		queue["extension"], queue["extension"])
	res += "exten => %s,n,Hangup()\n" % (
		queue["extension"])

	return res


def genExtensionsconf(co, lo, srv):
	from univention.admin.handlers.asterisk import sipPhone, conferenceRoom, waitingLoop, agiscript, fax

	# AGI-Script lookup and sorting
	agis = []
	for agi in agiscript.lookup(co, lo, False):
		agis.append((
			int(agi["priority"]),
			"AGI(ast4ucs-%s)" % agi["name"]
		))
	agis.sort(key=lambda x: x[0], reverse=True)
	agis = [x[1] for x in agis]

	conf = "; Automatisch generiert von Asterisk4UCS\n"

	conf += "\n[default]\n"

	conf += "\n\n; ===== Telefone =====\n\n"
	for phone in sipPhone.lookup(co, lo, False):
		conf += "; dn: %s\n" % (phone.dn)
		try:
			conf += genExtSIPPhoneEntry(co, lo, agis, phone)
		except Exception:
			conf += re.sub("(?m)^", ";", traceback.format_exc()[:-1])
		conf += "\n"

	conf += "\n\n; ===== Konferenzräume =====\n\n"
	for room in conferenceRoom.lookup(co, lo, False):
		conf += "; dn: %s\n" % (room.dn)
		try:
			conf += genExtRoomEntry(co, lo, agis, room)
		except Exception:
			conf += re.sub("(?m)^", ";", traceback.format_exc()[:-1])
		conf += "\n"

	conf += "\n\n; ===== Warteschleifen =====\n\n"
	for queue in waitingLoop.lookup(co, lo, False):
		conf += "; dn: %s\n" % (queue.dn)
		try:
			conf += genExtQueueEntry(co, lo, agis, queue)
		except Exception:
			conf += re.sub("(?m)^", ";", traceback.format_exc()[:-1])
		conf += "\n"

	conf += "\n\n; ===== Blockierte Vorwahlen =====\n\n"
	for areaCode in srv.info.get("blockedAreaCodes", []):
		conf += "exten => _%s.,1,Hangup()\n" % (areaCode)

	conf += "\n\n; ===== Faxe =====\n\n"
	for phone in fax.lookup(co, lo, False):
		for i, agi in enumerate(agis):
			conf += "exten => %s,%i,%s" % (
				phone["extension"],
				i + 1,
				agi
			)
		conf += "exten => %s,%i,Dial(SIP/%s)\n" % (
			phone.info["extension"],
			len(agis) + 1,
			phone.info["extension"])

	conf += "\n[extern-incoming]\n"

	conf += "\n\n; ===== Nummernkreise =====\n\n"
	for extnum in llist(srv.info.get("extnums", [])):
		conf += "exten => _%s,1,Goto(default,%s,1)\n" % (
			extnum, srv.info.get("defaultext", "fubar"))
		conf += "exten => _%s.,1,Goto(default,${EXTEN:%i},1)\n" % (
			extnum, len(extnum))

	return conf


def genConfigs(server):
	ucr.load()
	MODULE.error('### server: %s' % server)
	co = server.co
	lo = server.lo

	configs = {
		'sip.conf': genSipconf(co, lo, server),
		'voicemail.conf': genVoicemailconf(co, lo, server),
		'queues.conf': genQueuesconf(co, lo, server),
		'musiconhold.conf': genMusiconholdconf(co, lo, server),
		'extensions.conf': genExtensionsconf(co, lo, server),
	}

	return configs


def reverseFieldsLoad(self):
	if not self.dn:
		return
	for field, foreignModule, foreignField in self.reverseFields:
		foreignModule = univention.admin.modules.get(foreignModule)
		univention.admin.modules.init(self.lo, self.position, foreignModule)
		objects = foreignModule.lookup(self.co, self.lo, filter_format("%s=%s", (foreignModule.mapping.mapName(foreignField), self.dn)), superordinate=self.superordinate)
		self.info[field] = [obj.dn for obj in objects]


def reverseFieldsSave(self):
	if not self.dn:
		return
	for field, foreignModule, foreignField in self.reverseFields:
		foreignModule = univention.admin.modules.get(foreignModule)
		univention.admin.modules.init(self.lo, self.position, foreignModule)
		oldset = set(self.oldinfo.get(field, []))
		newset = set(self.info.get(field, []))

		for dn in (oldset - newset):
			obj = foreignModule.object(self.co, self.lo, None, dn, self.superordinate)
			obj.open()
			try:
				obj.info.get(foreignField, []).remove(self.dn)
			except ValueError:
				pass
			obj.modify()

		for dn in (newset - oldset):
			obj = foreignModule.object(self.co, self.lo, None, dn, self.superordinate)
			obj.open()
			obj.info.setdefault(foreignField, []).append(self.dn)
			obj.modify()


class AsteriskBase(univention.admin.handlers.simpleLdap):

	def __init__(self, co, lo, position, dn='', superordinate=None, attributes=None):
		if not superordinate and (dn or position):
			superordinate = univention.admin.objects.get_superordinate(self.module, co, lo, dn or position.getDn())
		super(AsteriskBase, self).__init__(co, lo, position, dn, superordinate, attributes)
