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

class Instance(univention.management.console.modules.Base):
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
		moh = getMoh(request.options["mohdn"])

		result = []
		for song in moh.get("music", []):
			result.append({
				"name": song,
			})

		request.status = SUCCESS
		self.finished(request.id, result)

	def create(self, request):
		server = request.options["server"]
		name = request.options["name"]

		result = {
			"newDn": create(server, name),
		}

		request.status = SUCCESS
		self.finished(request.id, result)

	def upload(self, request):
		moh = getMoh(request.options["moh"])
		server = getServer(re.sub(r"^[^,]+,", "", request.options["moh"]))
		data = base64.b64decode(request.options["data"])

		filename = request.options["filename"]
		stem = re.sub(r"\.\w+$", "", filename)
		stem = re.sub(r"[^a-zA-Z0-9-]+", "_", stem)
		stem = re.sub(r"^_+", "", stem)
		stem = re.sub(r"_+$", "", stem)

		if stem in moh.info.get("music", []):
			self.finished(request.id, {
				"success": False,
				"details": "Ein Musikstück mit diesem Namen wurde bereits hochgeladen!",
			})
			return

		uploadMusic(server, moh, data, stem, filename)

		moh.info.setdefault("music", []).append(stem)
		moh.modify()

		request.status = SUCCESS
		self.finished(request.id, {"foo":"bar"})


def getCoLoPos():
	co = univention.admin.config.config()

	lo, pos = univention.admin.uldap.getAdminConnection()

	return co, lo, pos

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
	moh = music.object(co, lo, pos, None)
	moh.open()
	moh.info["name"] = name
	moh.create()

	return moh.dn

def uploadMusic(server, moh, data, stem, filename):
	log = open("/tmp/upload.log", "w", 0)

	mohname = moh.info["name"]
	scriptpath = "/usr/lib/asterisk4ucs/moh-copy"
	sshtarget = "%s@%s" % (server.info["sshuser"], server.info["sshhost"])
	sshcmd = server.info["sshcmd"]
	sshmohpath = server.info.get("sshmohpath", "/opt/asterisk4ucs/moh")

	tmpdir = tempfile.mkdtemp()
	try:
		inputfilename = stem
		if re.match("\.mp3$", filename):
			inputfilename += ".mp3"

		inputfile = open("%s/%s" % (tmpdir, inputfilename), "wb")
		inputfile.write(data)
		inputfile.close()

		subprocess.check_call([scriptpath, stem, inputfilename,
				mohname, sshtarget, sshmohpath, sshcmd],
				stdout=log, stderr=log, cwd=tmpdir)
	finally:
		shutil.rmtree(tmpdir)


