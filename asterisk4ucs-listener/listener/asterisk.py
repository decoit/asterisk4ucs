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

name = "asterisk"
description = "Creates configuration files for asterisk"
filter = "(objectClass=ast4ucsServer)"
attributes = ["ast4ucsServerLastupdate"]

import listener
import zlib
from subprocess import Popen, PIPE
from string import Template

success = False

def refreshConfig(configs):
	prefix = "%s/" % listener.baseConfig["asterisk/confpath"]
	listener.setuid(0)
	for config in configs:
		filename,data = config.split(" ", 2)
		open(prefix + filename, "w").write(
			zlib.decompress(data.decode("base64")))
	listener.unsetuid()

def sendMail(templ):
	if not admins:
		return

	hostname = "fubar"
	body = templ.substitute(hostname=hostname)
	for admin in admins:
		body = ( "To: %s\r\n" % admin ) + body

	sendmail = Popen(["/usr/sbin/sendmail", "-t"],
			stdin=PIPE, stdout=PIPE, stderr=PIPE)
	stdout, stderr = sendmail.communicate(body)

def handler(dn, newdata, olddata):
	global success, admins
	admins = newdata.get("admins")
	success = False
	
	if not newdata:
		return

	if (newdata["ast4ucsServerHost"][0]
				!= listener.baseConfig["ldap/hostdn"]):
		return

	refreshConfig(newdata.get("ast4ucsServerConfig", []))
	success = True

def postrun():
	if not success:
		sendMail(failMail)
		return

	bin = listener.baseConfig["asterisk/asteriskbin"]
	listener.setuid(0)
	listener.run(bin, [bin, "-r", "-x", "core reload"])
	listener.unsetuid()

	sendMail(successMail)


successMail = Template("""\
From: Asterisk auf {hostname} <asterisk@{hostname}>
Subject: Neue Konfiguration erfolgreich Eingespielt!

(Kein Text)
""".replace("\n", "\r\n"))


failMail = Template("""\
From: Asterisk auf {hostname} <asterisk@{hostname}>
Subject: Fehler beim Einspielen der Konfiguration!

(Hier wird später eine sehr hilfreiche Fehlermeldung stehen.)
""".replace("\n", "\r\n"))


