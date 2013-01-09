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

import univention.management.console.modules
from univention.management.console.protocol.definitions import SUCCESS
from univention.management.console.log import MODULE

import univention.config_registry
import univention.admin.uldap
import univention.admin.config

import univention.admin.modules
univention.admin.modules.update()

import univention.admin.handlers.asterisk
import univention.admin.handlers.asterisk.server
import univention.admin.handlers.asterisk.music
import univention.admin.handlers.asterisk.agiscript as agiscript

import os
import re
from time import strftime, localtime, sleep
import shutil
import tempfile
import subprocess

ucr = univention.config_registry.ConfigRegistry()
ucr.load()

class Instance(univention.management.console.modules.Base):
	def queryServers(self, request):
		servers = getServers()
		result = []
		for server in servers:
			result.append({
				"id": server.dn,
				"label": server["commonName"],
			})
		self.finished(request.id, result)

	def copyid(self, request):
		server = getServer(request.options["server"])
		log = openLog(server["commonName"])
		print >>log, "Die Funktion zum Kopieren des SSH-Schlüssels ist noch " \
				"nicht implementiert."
		closeLog(log)
		self.finished(request.id, True)

	def create(self, request):
		
		server = getServer(request.options["server"])
		MODULE.error('### request: %s' % request)
		MODULE.error('### self: %s' % self)
		MODULE.error('### values: %s' % request.options.get('values', {}))
		log = openLog(server["commonName"])
		createConfigs(log, server)
		closeLog(log)
		self.finished(request.id, True)

	def deploy(self, request):
		server = getServer(request.options["server"])
		log = openLog(server["commonName"])

		configs = createConfigs(log, server)
		print >>log, "\n\n"
		try:
			deployConfigs(log, server, configs)
		except subprocess.CalledProcessError:
			print >>log, "\n\nERROR: Aborted deployment because of an error.\n"
		else:
			print >>log, "\n\nDie neue Konfiguration ist jetzt aktiv."
			print >>log, "Viel Spaß beim Telefonieren!\n"

		closeLog(log)
		self.finished(request.id, True)

	def getLog(self, request):
		server = getServer(request.options["server"])
		log = getLog(server["commonName"])
		self.finished(request.id, log)


def getCoLoPos():
	co = univention.admin.config.config()

	lo, pos = univention.admin.uldap.getAdminConnection()

	return co, lo, pos

def getServers():
	co, lo, pos = getCoLoPos()

	server = univention.admin.modules.get("asterisk/server")
	univention.admin.modules.init(lo, pos, server)
	servers = server.lookup(co, lo, None)

	for item in servers:
		item.open()

	return servers

def getServer(dn):
	co, lo, pos = getCoLoPos()

	server = univention.admin.modules.get("asterisk/server")
	univention.admin.modules.init(lo, pos, server)
	obj = server.object(co, lo, None, dn)
	obj.open()

	return obj

def getLog(servername):
	servername = re.sub(r"[^a-zA-Z0-9]+", "_", servername)
	filename = "/var/log/univention/asteriskDeploy-%s.log" % servername
	try:
		return open(filename).read()
	except IOError, e:
		return "[Error: %s]" % str(e)

def openLog(servername):
	servername = re.sub(r"[^a-zA-Z0-9]+", "_", servername)
	filename = "/var/log/univention/asteriskDeploy-%s.log" % servername
	time = strftime("%a, %d %b %Y %H:%M:%S", localtime())
	
	log = open(filename, "w", False)
	log.write("Log opened %s\n" % time)
	log.write("===========%s\n" % ("=" * len(time)))
	log.write("\n")
	return log

def closeLog(log):
	time = strftime("%a, %d %b %Y %H:%M:%S", localtime())
	log.write("\n")
	log.write("Log closed %s\n" % time)
	log.close()

def createConfigs(log, server):
	print >>log, "Creating config files for server %s" % server["commonName"]
	print >>log, "=================================%s" % (
			"=" * len(server["commonName"]))
	
	configs = univention.admin.handlers.asterisk.genConfigs(server)
	for name, data in configs.items():
		print >>log
		print >>log
		print >>log, "Creating %s:" % name
		print >>log, "---------%s-" % ("-" * len(name))
		print >>log
		errors = re.findall(r"^;; .*", data, re.MULTILINE)
		for error in errors:
			print >>log, error[3:]
		if not errors:
			print >>log, "(no error)"

	return configs

def logCall(log, args, cwd):
	print >>log, "Creating child process: %s" % str(args)
	proc = subprocess.Popen(args, stdout=log, stderr=log,
			stdin=open("/dev/zero"), cwd=cwd)
	print >>log, "Child process has pid %i" % proc.pid

	sleeptime = 0.1
	timeleft = 30
	while timeleft > 0:
		if proc.poll() != None:
			break
		sleep(sleeptime)
		timeleft -= sleeptime
	else:
		print >>log, "Child process did not terminate in time, killing it..."
		proc.kill()
		raise subprocess.CalledProcessError(proc.returncode, args[0])

	print >>log, "Child returned code %i" % proc.returncode

	if proc.returncode != 0:
		raise subprocess.CalledProcessError(proc.returncode, args[0])

def deployConfigs(log, server, configs):
	print >>log, "Deploying config files to server %s" % (
			server["commonName"])
	print >>log, "=================================%s" % (
			"=" * len(server["commonName"]))
	print >>log

	agis = {}
	for agi in agiscript.lookup(server.co, server.lo, False):
		agis["ast4ucs-" + agi["name"]] = agi.getContent()

	sshtarget = "%s@%s" % (server["sshuser"], server["sshhost"])
	scptargetLdapconf = "%s:/etc/asterisk4ucs.ldapconfig" % (sshtarget)
	scptargetConfig = "%s:%s/ucs_autogen" % (sshtarget, server["sshpath"])
	scptargetAgi = "%s:%s/" % (sshtarget, server["sshagipath"])
	sshcmd = "%s -rx 'core reload'" % server["sshcmd"]

	tmpdirConfig = tempfile.mkdtemp()
	tmpdirAgi = tempfile.mkdtemp()
	fd, tmpfileLdapconf = tempfile.mkstemp()
	try:
		f = os.fdopen(fd, "wb")
		f.write("%s.%s\n" % (ucr['hostname'], ucr['domainname']))
		f.write("cn=asterisk,%s\n" % (ucr['ldap/base']))
		f.write("%s\n" % (server.get('agi-user', "")))
		f.write("%s\n" % (server.get('agi-password', "")))
		f.close()

		for name, data in configs.items():
			f = open("%s/%s" % (tmpdirConfig, name), "w")
			f.write(data)
			f.close()

		for name, data in agis.items():
			f = open("%s/%s" % (tmpdirAgi, name), "w")
			f.write(data)
			os.fchmod(f.fileno(), 0755)
			f.close()

		logCall(log, ["scp", "-Bq", tmpfileLdapconf,
				scptargetLdapconf], tmpdirConfig)
		logCall(log, ["scp", "-Bq"] + configs.keys()
				+ [scptargetConfig], tmpdirConfig)
		logCall(log, ["scp", "-Bq"] + agis.keys()
				+ [scptargetAgi], tmpdirAgi)
		logCall(log, ["ssh", "-oBatchMode=yes", sshtarget, sshcmd],
				tmpdirConfig)
	finally:
		shutil.rmtree(tmpdirConfig)
		shutil.rmtree(tmpdirAgi)
		os.remove(tmpfileLdapconf)

