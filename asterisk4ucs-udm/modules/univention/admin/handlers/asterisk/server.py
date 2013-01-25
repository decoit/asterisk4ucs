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

import univention.admin.filter
import univention.admin.handlers
from univention.admin.handlers import asterisk
import univention.admin.syntax
from univention.admin.layout import Tab
import time
import logging

#logfile = "/var/log/univention/asteriskMusicPython.log"

module = "asterisk/server"
short_description = u"Asterisk4UCS-Management: Asterisk-Server"
operations = ['add', 'edit', 'remove', 'search', 'move']
options = {}

childs = 1
usewizard = 1

#logging.basicConfig(filename=logfile,
	#level=logging.INFO,
#     level=logging.DEBUG,
#	format = "%(asctime)s\t%(levelname)s\t%(message)s",
#	datefmt = "%d.%m.%Y %H:%M:%S"
#	)

layout = [
	Tab('Allgemein', 'Allgemeine Einstellungen', layout = [
		[ "commonName" ],
		[ "globalCallId" ],
	]),
	Tab('Vorwahlen', 'Gesperrte Vorwahlen', layout = [
		[ "blockedAreaCodes", "blockInternational" ],
	]),
	Tab('Anrufbeantworter', 'Anrufbeantworter', layout = [
		[ "mailboxMaxlength" ],
		[ "mailboxEmailsubject", "mailboxEmailbody" ],
		[ "mailboxEmaildateformat", "mailboxAttach" ],
		[ "mailboxMailcommand" ],
	]),
	Tab('Nummernkreise', 'Nummernkreise', layout = [
		[ "extnums", "defaultext" ],
	], advanced=True),
	Tab('Asterisk-Host', 'Asterisk-Host', layout = [
		[ "sshuser", "sshhost" ],
		[ "sshpath", "sshmohpath" ],
		[ "sshagipath", "sshcmd" ],
	], advanced=True),
	Tab('Namensauflösung', 'Namensauflösung für Anrufer', layout = [
		[ "agi-user", "agi-password" ],
	], advanced=True),
]

property_descriptions = {
	"commonName": univention.admin.property(
		short_description="Name",
		syntax=univention.admin.syntax.string,
		identifies=True,
		required=True
	),
	"sshuser": univention.admin.property(
		short_description="SSH-User",
		syntax=univention.admin.syntax.string,
		default="root",
		required=True,
	),
	"sshhost": univention.admin.property(
		short_description="SSH-Host",
		syntax=univention.admin.syntax.string,
		required=True,
	),
	"sshpath": univention.admin.property(
		short_description="Asterisk-Konfigurationspfad auf Zielhost",
		syntax=univention.admin.syntax.string,
		default="/etc/asterisk",
		required=True,
	),
	"sshmohpath": univention.admin.property(
		short_description="Asterisk-Warteschlangenmusikpfad auf Zielhost",
		syntax=univention.admin.syntax.string,
		default="/opt/asterisk4ucs/moh",
		required=True,
	),
	"sshagipath": univention.admin.property(
		short_description="Asterisk-Agibinpfad auf Zielhost",
		syntax=univention.admin.syntax.string,
		default="/var/lib/asterisk/agi-bin",
		required=True,
	),
	"sshcmd": univention.admin.property(
		short_description="Asterisk-Kommando auf Zielhost",
		syntax=univention.admin.syntax.string,
		default="asterisk",
		required=True,
	),
	"globalCallId" : univention.admin.property(
		syntax=univention.admin.syntax.string,
		short_description=u"Alle ausgehenden Anrufer übermitteln die folgende Nummer:",
	),
	"blockedAreaCodes": univention.admin.property(
		short_description=u"Blockierte Vorwahlen",
		syntax=univention.admin.syntax.string,
		multivalue=True,
	),
	"blockInternational": univention.admin.property(
		short_description=u"Auslandsgespräche blockieren",
		long_description=u"Blockiert die Vorwahlen 00 und +",
		syntax=univention.admin.syntax.boolean,
		default=False,
	),
	"extnums": univention.admin.property(
		short_description="Eigene externe Rufnummer(n)",
		syntax=univention.admin.syntax.string,
		multivalue=True,
	),
	"defaultext": univention.admin.property(
		short_description="Standard-Extension",
		syntax=univention.admin.syntax.string,
	),
	"mailboxMaxlength": univention.admin.property(
		short_description=u"Maximale Länge einer Sprachnachricht (Sekunden)",
		syntax=univention.admin.syntax.integer,
		required=True,
		default="300",
	),
	"mailboxEmailsubject": univention.admin.property(
		short_description="Betreff der eMails",
		long_description=u"""Die folgenden Platzhalter können verwendet werden:
     ${VM_NAME}      Name des Mailbox-Inhabers
     ${VM_DUR}       Länge der Nachricht
     ${VM_MSGNUM}    Nummer der Nachricht
     ${VM_MAILBOX}   Name der Mailbox
     ${VM_CALLERID}  Telefonnummer und Name des Anrufers
     ${VM_CIDNUM}    Telefonnummer des Anrufers
     ${VM_CIDNAME}   Name des Anrufers
     ${VM_DATE}      Datum und Uhrzeit des Anrufs
     ${VM_MESSAGEFILE}
		     Name der Sounddatei, in der die
		     Nachricht abgespeichert ist""".replace("\n","<br>"),
		syntax=univention.admin.syntax.string,
		required=True,
		default="New message from ${VM_CALLERID}",
	),
	"mailboxEmailbody": univention.admin.property(
		short_description="Textkörper der eMails",
		long_description=u"""Die folgenden Platzhalter können verwendet werden:
     ${VM_NAME}      Name des Mailbox-Inhabers
     ${VM_DUR}       Länge der Nachricht
     ${VM_MSGNUM}    Nummer der Nachricht
     ${VM_MAILBOX}   Name der Mailbox
     ${VM_CALLERID}  Telefonnummer und Name des Anrufers
     ${VM_CIDNUM}    Telefonnummer des Anrufers
     ${VM_CIDNAME}   Name des Anrufers
     ${VM_DATE}      Datum und Uhrzeit des Anrufs
     ${VM_MESSAGEFILE}
		     Name der Sounddatei, in der die
		     Nachricht abgespeichert ist

Weiterhin können die folgenden Escapesequenzen verwendet werden:
     \\n	     Neue Zeile
     \\t	     Tabulator-Zeichen""".replace("\n","<br>"),
		syntax=univention.admin.syntax.string,
		required=True,
		default="Hello ${VM_NAME},\n\nThere is a new message " + \
			"in mailbox ${VM_MAILBOX}.",
	),
	"mailboxEmaildateformat": univention.admin.property(
		short_description="Datumsformat in eMails",
		long_description=u"""Folgt der strftime-Notation:
%a    Abgekürzter Wochentag
%A    Ausgeschriebener Wochentag
%b    Abgekürzter Monatsname
%B    Voller Monatsname
%c    Datum und Uhrzeit
%d    Tag im Monat (1-31)
%H    Stunde (0-23)
%I    Stunde (0-12)
%j    Tag im Jahr (1-366)
%m    Monat (1-12)
%M    Minute (00-59)
%p    AM/PM
%S    Sekunde (00-59)
%w    Wochentag (0-6)
%W    Woche im Jahr (0-52)
%x    Lokale Datumsdarstellung
%X    Lokale Zeit-Darstellung
%y    Jahr ohne Jahrhundert (0-99)
%Y    Jahr mit Jahrhundertangabe
%Z    Name der Zeitzone (z.B. MEZ)
%%    Das '%'-Zeichen""".replace("\n","<br>"),
		syntax=univention.admin.syntax.string,
		required=True,
		default="%d.%m.%Y %H:%M",
	),
	"mailboxAttach": univention.admin.property(
		short_description="Sprachnachricht an eMails anhängen?",
		syntax=univention.admin.syntax.boolean,
		required=True,
		default="1",
	),
	"mailboxMailcommand": univention.admin.property(
		short_description="Befehl zum Versenden der eMails",
		long_description=u"Programm zum Versenden von E-Mails " + \
			"(unbedingt den absoluten Pfad angeben!)",
		syntax=univention.admin.syntax.string,
		required=True,
		default="/usr/sbin/sendmail -t",
	),
	"agi-user": univention.admin.property(
		short_description="Ldap bind DN für AGI-Skripte",
		long_description=u"Der Ldap bind DN für die Authentifikation der AGI Skripte",
		syntax=univention.admin.syntax.string,
	),
	"agi-password": univention.admin.property(
		short_description="Ldap Passwort für AGI-Skripte",
		long_description=u"Das Passwort für den Ldap bind DN",
		syntax=univention.admin.syntax.string,
	),
}

mapping = univention.admin.mapping.mapping()
mapping.register("commonName", "cn",
	None, univention.admin.mapping.ListToString)
mapping.register("blockedAreaCodes", "ast4ucsServerBlockedareacode")
mapping.register("extnums", "ast4ucsServerExtnum")
mapping.register("defaultext", "ast4ucsServerDefaultext",
	None, univention.admin.mapping.ListToString)

mapping.register("sshuser", "ast4ucsServerSshuser",
	None, univention.admin.mapping.ListToString)
mapping.register("sshhost", "ast4ucsServerSshhost",
	None, univention.admin.mapping.ListToString)
mapping.register("sshpath", "ast4ucsServerSshpath",
	None, univention.admin.mapping.ListToString)
mapping.register("sshmohpath", "ast4ucsServerSshmohpath",
	None, univention.admin.mapping.ListToString)
mapping.register("sshagipath", "ast4ucsServerSshagipath",
	None, univention.admin.mapping.ListToString)
mapping.register("sshcmd", "ast4ucsServerSshcmd",
	None, univention.admin.mapping.ListToString)

mapping.register("mailboxMaxlength", "ast4ucsServerMailboxmaxlen",
	None, univention.admin.mapping.ListToString)
mapping.register("mailboxEmailsubject", "ast4ucsServerMailboxemailsubject",
	None, univention.admin.mapping.ListToString)
mapping.register("mailboxEmailbody", "ast4ucsServerMailboxemailbody",
	None, univention.admin.mapping.ListToString)
mapping.register("mailboxEmaildateformat", "ast4ucsServerMailboxemaildateformat",
	None, univention.admin.mapping.ListToString)
mapping.register("mailboxAttach", "ast4ucsServerMailboxattach",
	None, univention.admin.mapping.ListToString)
mapping.register("mailboxMailcommand", "ast4ucsServerMailboxemailcommand",
	None, univention.admin.mapping.ListToString)
mapping.register("globalCallId", "ast4ucsServerGlobalCallId",
	None, univention.admin.mapping.ListToString)

mapping.register("agi-user", "ast4ucsServerAgiuser",
	None, univention.admin.mapping.ListToString)
mapping.register("agi-password", "ast4ucsServerAgipassword",
	None, univention.admin.mapping.ListToString)

class object(univention.admin.handlers.simpleLdap):
	module=module

	def __init__(self, co, lo, position, dn='', superordinate=None,
			attributes=[]):
		global mapping
		global property_descriptions
		self.co = co
		self.lo = lo
		self.dn = dn
		self.position = position
		self._exists = 0
		self.mapping = mapping
		self.descriptions = property_descriptions
		univention.admin.handlers.simpleLdap.__init__(self, co, lo, 
			position, dn, superordinate)

	def exists(self):
		return self._exists

	def open(self):
		univention.admin.handlers.simpleLdap.open(self)
		self.save()

		for areaCode in ["+", "00"]:
			if not areaCode in self.info.get("blockedAreaCodes", []):
				break
		else:
			self.info["blockInternational"] = "1"
			for areaCode in ["+", "00"]:
				self.info["blockedAreaCodes"].remove(areaCode)

	def saveCheckboxes(self):
		if "1" in self.info.get("blockInternational",[]):
			self.info.setdefault("blockedAreaCodes", []).extend(["+", "00"])
			if "" in self.info["blockedAreaCodes"]:
				self.info["blockedAreaCodes"].remove("")
			self.info["blockedAreaCodes"] = list(set(
				self.info["blockedAreaCodes"]))

	def _ldap_pre_modify(self):
		self.saveCheckboxes()

	def _ldap_pre_create(self):
		self.dn = '%s=%s,%s' % (
			mapping.mapName('commonName'),
			mapping.mapValue('commonName', self.info['commonName']),
			self.position.getDn()
		)
		self.saveCheckboxes()

	def _ldap_post_create(self):
		# this mess just creates the "default" asterisk/music
		# (dn: "cn=default," + self.dn)
		music = univention.admin.modules.get("asterisk/music")
		univention.admin.modules.init(self.lo, self.position, music)
		pos = univention.admin.uldap.position(self.position.getBase())
		pos.setDn(self.dn)
		defaultMoh = music.object(self.co, self.lo, pos, None, self)
		defaultMoh.open()
		defaultMoh.info["name"] = "default"
		defaultMoh.info["music"] = ["default"]
		defaultMoh.create()

		# this mess just creates the "number2name" asterisk/agiscript
		agiscript = univention.admin.modules.get("asterisk/agiscript")
		univention.admin.modules.init(self.lo, self.position, agiscript)
		pos = univention.admin.uldap.position(self.position.getBase())
		pos.setDn(self.dn)
		number2name = agiscript.object(self.co, self.lo, pos, None, self)
		number2name.open()
		number2name.info["name"] = "number2name"
		number2name.info["priority"] = "2000"
		number2name.setContent(open("/usr/lib/asterisk4ucs/number2name.agi").read())
		number2name.create()

	def _ldap_addlist(self):
		return [('objectClass', ['ast4ucsServer'])]


def lookup(co, lo, filter_s, base='', superordinate=None, scope='sub', 
		unique=False, required=False, timeout=-1, sizelimit=0):
	filter = univention.admin.filter.conjunction('&', [
		univention.admin.filter.expression(
			'objectClass', "ast4ucsServer")
	])
 	#logging.debug('server.py UDM 366: filter: %s', filter)
	if filter_s:
		filter_p = univention.admin.filter.parse(filter_s)
		univention.admin.filter.walk(filter_p, 
			univention.admin.mapping.mapRewrite, arg=mapping)
		filter.expressions.append(filter_p)
 
	res = []
	for dn, attrs in lo.search(unicode(filter), base, scope, [], unique,
			required, timeout, sizelimit):
		res.append(object(co, lo, None, dn=dn,
				superordinate=superordinate, attributes=attrs))
	#logging.debug('server.py UDM 378: res: %s',res)
	return res

def identify(dn, attr, canonical=0):
	return 'ast4ucsServer' in attr.get('objectClass', [])

