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

class Instance(univention.management.console.modules.Base):
	def hallo(self, request):
		self.finished(request.id, "Hallo, Programmierer!")

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
