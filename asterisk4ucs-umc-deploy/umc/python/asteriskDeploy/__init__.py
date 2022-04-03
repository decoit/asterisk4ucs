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
from __future__ import print_function

from univention.management.console.base import Base
from univention.management.console.log import MODULE
from univention.management.console.config import ucr

import univention.admin.uldap

import univention.admin.modules

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

univention.admin.modules.update()


class Instance(Base):

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
		print("Die Funktion zum Kopieren des SSH-Schlüssels ist noch nicht implementiert.", file=log)
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
		print("\n\n", file=log)
		try:
			deployConfigs(log, server, configs)
		except subprocess.CalledProcessError:
			print("\n\nERROR: Aborted deployment because of an error.\n", file=log)
		else:
			print("\n\nDie neue Konfiguration ist jetzt aktiv.", file=log)
			print("Viel Spaß beim Telefonieren!\n", file=log)

		closeLog(log)
		self.finished(request.id, True)

	def getLog(self, request):
		server = getServer(request.options["server"])
		log = getLog(server["commonName"])
		self.finished(request.id, log)


def getCoLoPos():
	co = None
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
	MODULE.error("server dn: %s" % dn)
	obj.open()

	return obj


def getLog(servername):
	servername = re.sub(r"[^a-zA-Z0-9]+", "_", servername)
	filename = "/var/log/univention/asteriskDeploy-%s.log" % servername
	try:
		return open(filename).read()
	except IOError:
		return "(Für diesen Server gibt es noch kein Deployment-Log)"


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
	print("Creating config files for server %s" % server["commonName"], file=log)
	print("=================================%s" % ("=" * len(server["commonName"])), file=log)

	configs = univention.admin.handlers.asterisk.genConfigs(server)
	for name, data in configs.items():
		print(file=log)
		print(file=log)
		print("Creating %s:" % name, file=log)
		print("---------%s-" % ("-" * len(name)), file=log)
		print(file=log)
		errors = re.findall(r"^;; .*", data, re.MULTILINE)
		for error in errors:
			print(error[3:], file=log)
		if not errors:
			print("(no error)", file=log)

	return configs


def logCall(log, args, cwd):
	print("Creating child process: %s" % str(args), file=log)
	proc = subprocess.Popen(args, stdout=log, stderr=log, stdin=open("/dev/zero"), cwd=cwd)
	print("Child process has pid %i" % proc.pid, file=log)

	sleeptime = 0.1
	timeleft = 30
	while timeleft > 0:
		if proc.poll() is not None:
			break
		sleep(sleeptime)
		timeleft -= sleeptime
	else:
		print("Child process did not terminate in time, killing it...", file=log)
		proc.kill()
		raise subprocess.CalledProcessError(proc.returncode, args[0])

	print("Child returned code %i" % proc.returncode, file=log)

	if proc.returncode != 0:
		raise subprocess.CalledProcessError(proc.returncode, args[0])


def deployConfigs(log, server, configs):
	print("Deploying config files to server %s" % (server["commonName"]), file=log)
	print("=================================%s" % ("=" * len(server["commonName"])), file=log)
	print(file=log)

	agis = {}
	for agi in agiscript.lookup(server.co, server.lo, False):
		agis["ast4ucs-" + agi["name"]] = agi.getContent()

	sshtarget = "%s@%s" % (server["sshuser"], server["sshhost"])
	scptargetLdapconf = "%s:/etc/asterisk4ucs.ldapconfig" % (sshtarget)
	scptargetConfig = "%s:%s/ucs_autogen" % (sshtarget, server["sshpath"])
	scptargetAgi = "%s:%s/" % (sshtarget, server["sshagipath"])
	sshcmd = "%s -rx 'module reload'" % server["sshcmd"]

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
			with open("%s/%s" % (tmpdirConfig, name), "w") as fd:
				fd.write(data)

		for name, data in agis.items():
			with open("%s/%s" % (tmpdirAgi, name), "w") as fd:
				fd.write(data)
				os.fchmod(fd.fileno(), 0o755)

		logCall(log, ["scp", "-Bq", tmpfileLdapconf, scptargetLdapconf], tmpdirConfig)
		logCall(log, ["scp", "-Bq"] + configs.keys() + [scptargetConfig], tmpdirConfig)
		logCall(log, ["scp", "-Bq"] + agis.keys() + [scptargetAgi], tmpdirAgi)
		logCall(log, ["ssh", "-oBatchMode=yes", sshtarget, sshcmd], tmpdirConfig)
	finally:
		shutil.rmtree(tmpdirConfig)
		shutil.rmtree(tmpdirAgi)
		os.remove(tmpfileLdapconf)
