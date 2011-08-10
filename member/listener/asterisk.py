# coding=utf-8

name = "asterisk"
description = "Creates configuration files for asterisk"
filter = "(objectClass=ast4ucsServer)"
attributes = ["ast4ucsServerLastupdate"]

import listener
import zlib

success = False

def refreshConfig(configs):
	prefix = "%s/" % listener.baseConfig["asterisk/confpath"]
	listener.setuid(0)
	for config in configs:
		filename,data = config.split(" ", 2)
		open(prefix + filename, "w").write(
			zlib.decompress(data.decode("base64")))
	listener.unsetuid()

def handler(dn, newdata, olddata):
	global success
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
		return

	bin = listener.baseConfig["asterisk/asteriskbin"]
	listener.setuid(0)
	listener.run(bin, [bin, "-r", "-x", "core reload"])
	listener.unsetuid()

