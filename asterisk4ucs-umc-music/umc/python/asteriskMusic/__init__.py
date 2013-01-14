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
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA."""

import univention.management.console.modules
from univention.management.console.protocol.definitions import SUCCESS
from univention.management.console.log import MODULE

import univention.config_registry
import univention.admin.uldap
import univention.admin.config

import univention.admin.modules
univention.admin.modules.update()

import univention.admin.handlers.asterisk.server
import univention.admin.handlers.asterisk.music

import re
import base64
import shutil
import tempfile
import subprocess
import logging

logfile = "/var/log/univention/asteriskMusicPython.log"
logFilename = "/var/log/univention/asteriskMusicUpload.log"

class Instance(univention.management.console.modules.Base):
	#logging.basicConfig(filename=logfile,
		#level=logging.INFO,
          #level=logging.DEBUG,
		#format = "%(asctime)s\t%(levelname)s\t%(message)s",
		#datefmt = "%d.%m.%Y %H:%M:%S"
		#)
	def queryServers(self, request):
		servers = getServers()
		result = []
		for server in servers:
			result.append({
				"id": server.dn,
				"label": server["commonName"],
			})

		request.status = SUCCESS
		self.finished(request.id, result)

	def queryMohs(self, request):
		mohs = getMohs()

		result = []
		for moh in mohs:
			if moh["name"] != "default":
				result.append({
					"id": moh.dn,
					"label": moh["name"],
				})

		request.status = SUCCESS
		self.finished(request.id, result)

	def querySongs(self, request):
		if request.options["mohdn"] == "":
			self.finished(request.id, [])
			return

		moh = getMoh(request.options["mohdn"])

		if request.options.get("delete"):
			name = request.options["delete"]
			moh["music"].remove(name)
			deleteSong(moh, name)
			moh.modify()

		result = []
		for song in moh.get("music", []):
			result.append({
				"name": song,
			})

		request.status = SUCCESS
		self.finished(request.id, result)

	def create(self, request):
		server = request.options['server']
		name = request.options["name"]
		#logging.debug('__init__.py: server: %s , %s',request.options['server'],name)
		result = {
			"newDn": create(server, name),
		}

		request.status = SUCCESS
		self.finished(request.id, result)

	def delete(self, request):
		#logging.debug('__init__.py: moh: %s' , request)
		moh = getMoh(request.options["mohdn"])
		delete(moh)
		moh.remove()

		request.status = SUCCESS
		self.finished(request.id, True)

	def upload(self, request):
		#logging.debug('__init__.py: Upload requestMoh: %s',request.options["moh"])
		moh = getMoh(request.options["moh"])
		#logging.debug('__init__.py: getMoh: %s', moh)
		server = getServer(re.sub(r"^[^,]+,", "", request.options["moh"]))
		#logging.debug('__init__.py: getServer: %s', server)
		data = base64.b64decode(request.options["data"])

		filename = request.options["filename"]
		#logging.debug('__init__.py: Filename: %s', filename)
		stem = re.sub(r"\.\w+$", "", filename)
		stem = re.sub(r"[^a-zA-Z0-9-]+", "_", stem)
		stem = re.sub(r"^_+", "", stem)
		stem = re.sub(r"_+$", "", stem)
		#logging.debug('__init__.py: stem: %s', stem)
		#logging.debug('__init__.py: moh.info.get: %s',moh.info.get("music"));

		if stem in moh.info.get("music", []):
			#logging.debug('__init__.py: moh.info.get: %s',moh.info.get("music"));
			self.finished(request.id, {
				"success": False,
				"details": "Ein Musikstueck mit diesem Namen wurde bereits hochgeladen!",
			})
			#logging.debug('__init__.py: vor return');
			return

		#logging.debug('__init__.py: Upload Server: %s, MOH: %s, stem: %s, filename: %s',server,moh,stem,filenane)
		if uploadMusic(server, moh, data, stem, filename):
			moh.info.setdefault("music", []).append(stem)
			moh.modify()
			request.status = SUCCESS
			self.finished(request.id, {"foo":"bar"})
		else:
			log = open(logFilename).read()
			request.status = SUCCESS
			self.finished(request.id, {"error": log})

def getCoLoPos():
	co = univention.admin.config.config()
	#logging.debug('__init__.py: co: %s',co)"""
	lo, pos = univention.admin.uldap.getAdminConnection()
	#logging.debug('__init__.py: lo: %s pos: %s',lo, pos)

	return co, lo, pos

def getServers():
	co, lo, pos = getCoLoPos()

	server = univention.admin.modules.get("asterisk/server")
	univention.admin.modules.init(lo, pos, server)
	servers = server.lookup(co, lo, None)

	for item in servers:
		item.open()

	return servers

def getMohs():
	co, lo, pos = getCoLoPos()

	music = univention.admin.modules.get("asterisk/music")
	univention.admin.modules.init(lo, pos, music)
	mohs = music.lookup(co, lo, None)

	for moh in mohs:
		moh.open()

	return mohs

def getMoh(dn):
	co, lo, pos = getCoLoPos()

	music = univention.admin.modules.get("asterisk/music")
	univention.admin.modules.init(lo, pos, music)
	
	moh = music.object(co, lo, None, dn)
	moh.open()

	return moh

def getServer(dn):
	co, lo, pos = getCoLoPos()

	server = univention.admin.modules.get("asterisk/server")
	univention.admin.modules.init(lo, pos, server)
	obj = server.object(co, lo, None, dn)
	obj.open()

	return obj

def create(serverdn, name):
	co, lo, pos = getCoLoPos()

	server = univention.admin.modules.get("asterisk/server")
	univention.admin.modules.init(lo, pos, server)
	srv = server.object(co, lo, pos, serverdn)
	srv.open()
	if not srv.exists():
		raise Exception, "Invalid serverDN"

	pos.setDn(serverdn)

	music = univention.admin.modules.get("asterisk/music")
	univention.admin.modules.init(lo, pos, music)
	moh = music.object(co, lo, pos, None, srv)
	moh.open()
	moh.info["name"] = name
	moh.create()

	return moh.dn

def uploadMusic(server, moh, data, stem, filename):
	log = open(logFilename, "w", 0)

	mohname = moh.info["name"]
	scriptpath = "/usr/lib/asterisk4ucs/moh-copy"
	sshtarget = "%s@%s" % (server.info["sshuser"], server.info["sshhost"])
	sshcmd = server.info["sshcmd"]
	sshmohpath = server.info.get("sshmohpath", "/opt/asterisk4ucs/moh")

	tmpdir = tempfile.mkdtemp()
	try:
		inputfilename = "input_file"
		#logging.debug('__init__.py: filename: %s',filename);
		#logging.debug('__init__.py: inputfilename: %s',inputfilename);
		if re.search("\.mp3$", filename):
			inputfilename += ".mp3"

		inputfile = open("%s/%s" % (tmpdir, inputfilename), "wb")
		inputfile.write(data)
		inputfile.close()

		subprocess.check_call([scriptpath, stem, inputfilename,
				mohname, sshtarget, sshmohpath, sshcmd],
				stdout=log, stderr=log, cwd=tmpdir)
	except subprocess.CalledProcessError:
		return False
	finally:
		shutil.rmtree(tmpdir)

	return True

def delete(moh):
	server = moh.superordinate
	log = open(logFilename, "w", 0)

	mohname = moh.info["name"]
	sshtarget = "%s@%s" % (server.info["sshuser"], server.info["sshhost"])
	sshcmd = server.info["sshcmd"]
	sshmohpath = server.info.get("sshmohpath", "/opt/asterisk4ucs/moh")
	mohpath = "%s/%s" % (sshmohpath, mohname)
	remotecmd = "rm -r '%s' ; %s -rx 'moh reload'" % (
			mohpath.replace("'", r"'\''"), # escaping is fun!
			sshcmd )

	subprocess.check_call(["ssh", "-oBatchMode=yes", sshtarget, remotecmd],
			stdout=log, stderr=log)
def deleteSong(moh, song):
	server = moh.superordinate
	log = open(logFilename, "w", 0)

	mohname = moh.info["name"]
	sshtarget = "%s@%s" % (server.info["sshuser"], server.info["sshhost"])
	sshcmd = server.info["sshcmd"]
	sshmohpath = server.info.get("sshmohpath", "/opt/asterisk4ucs/moh")
	mohpath = "%s/%s/%s" % (sshmohpath, mohname, song)
	bashcmd = "rm '%s'.*" % mohpath.replace("'", r"'\''") # escaping is fun!
	remotecmd = "bash -c '%s' ; %s -rx 'moh reload'" % (
			bashcmd.replace("'", r"'\''"), # nested escaping is even more fun!
			sshcmd )

	subprocess.check_call(["ssh", "-oBatchMode=yes", sshtarget, remotecmd],
			stdout=log, stderr=log)

