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
import univention.admin.syntax
from univention.admin.layout import Tab

module = "asterisk/sipPhone"
short_description = u"Asterisk4UCS-Management: IP-Telefon"
operations = ['add', 'edit', 'remove', 'search', 'move']
options = {}

childs = 0
usewizard = 1
superordinate = "asterisk/server"

layout = [
	Tab('Allgemein', 'Allgemeine Einstellungen', layout = [
		[ "extension", "ipaddress" ],
		[ "macaddress", "hostname" ],
		[ "phonetype", "profile" ],
		[ "password" ],
		[ "forwarding", "skipExtension" ],
		[ "waitingloops" ],
		[ "callgroups" ],
		[ "pickupgroups" ],
	])
]

property_descriptions = {
	"extension": univention.admin.property(
		short_description="Durchwahl",
		syntax=univention.admin.syntax.string,
		required=True,
		identifies=True,
	),
	"ipaddress": univention.admin.property(
		short_description="IP-Adresse",
		syntax=univention.admin.syntax.ipAddress,
	),
	"macaddress": univention.admin.property(
		short_description="MAC-Adresse",
		syntax=univention.admin.syntax.string
	),
	"hostname": univention.admin.property(
		short_description="Hostname",
		syntax=univention.admin.syntax.hostName
	),
	"phonetype": univention.admin.property(
		short_description="Telefontyp",
		syntax=univention.admin.syntax.LDAP_Search(
                        filter="objectClass=ast4ucsPhonetype",
                        attribute=['asterisk/phoneType: commonName'],
                        value='asterisk/phoneType: dn'
                ),
	),
	"profile": univention.admin.property(
		short_description="Profil",
		syntax=univention.admin.syntax.string
	),
	"password": univention.admin.property(
		short_description="Passwort",
		syntax=univention.admin.syntax.userPasswd,
		required=True,
	),
	"callgroups": univention.admin.property(
		short_description="Callgroups",
		syntax=univention.admin.syntax.LDAP_Search(
                        filter="objectClass=ast4ucsPhonegroup",
                        attribute=['asterisk/phoneGroup: commonName'],
                        value='asterisk/phoneGroup: dn'
                ),
		multivalue=True,
	),
	"pickupgroups": univention.admin.property(
		short_description="Pickupgroups",
		syntax=univention.admin.syntax.LDAP_Search(
                        filter="objectClass=ast4ucsPhonegroup",
                        attribute=['asterisk/phoneGroup: commonName'],
                        value='asterisk/phoneGroup: dn'
                ),
		multivalue=True,
	),
	"waitingloops": univention.admin.property(
		short_description="Warteschleifen",
		syntax=univention.admin.syntax.LDAP_Search(
                        filter="objectClass=ast4ucsWaitingloop",
                        attribute=['asterisk/waitingLoop: extension'],
                        value='asterisk/waitingLoop: dn'
                ),
		multivalue=True,
	),
	"forwarding": univention.admin.property(
		short_description="Weiterleitung",
		syntax=univention.admin.syntax.string
	),
	"skipExtension": univention.admin.property(
		short_description="Bei Wählplangenerierung überspringen",
		syntax=univention.admin.syntax.boolean
	),
}

mapping = univention.admin.mapping.mapping()
mapping.register("extension", "ast4ucsExtensionExtension",
	None, univention.admin.mapping.ListToString)

mapping.register("ipaddress", "ast4ucsSipclientIp",
	None, univention.admin.mapping.ListToString)
mapping.register("macaddress", "ast4ucsSipclientMacaddr",
	None, univention.admin.mapping.ListToString)
mapping.register("hostname", "ast4ucsSipclientHostname",
	None, univention.admin.mapping.ListToString)
mapping.register("password", "ast4ucsSipclientSecret",
	None, univention.admin.mapping.ListToString)

mapping.register("phonetype", "ast4ucsPhonePhonetype",
	None, univention.admin.mapping.ListToString)
mapping.register("profile", "ast4ucsPhoneProfile",
	None, univention.admin.mapping.ListToString)
mapping.register("callgroups", "ast4ucsPhoneCallgroup")
mapping.register("pickupgroups", "ast4ucsPhonePickupgroup")
mapping.register("waitingloops", "ast4ucsPhoneWaitingloop")
mapping.register("forwarding", "ast4ucsPhoneForwarding",
	None, univention.admin.mapping.ListToString)
mapping.register("skipExtension", "ast4ucsPhoneSkipextension",
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

		self.openSuperordinate()
		if not self.superordinate:
			raise univention.admin.uexceptions.insufficientInformation, \
					 'superordinate object not present'
		if not dn and not position:
			raise univention.admin.uexceptions.insufficientInformation, \
					 'neither DN nor position present'

	def openSuperordinate(self):
		if self.superordinate:
			return

		self.open()
		serverdn = self.oldattr.get("ast4ucsSrvchildServer")
		if not serverdn:
			return

		if serverdn.__iter__:
			serverdn = serverdn[0]

		univention.admin.modules.update()
		servermod = univention.admin.modules.get("asterisk/server")
		univention.admin.modules.init(self.lo, self.position, servermod)
		self.superordinate = servermod.object(self.co, self.lo,
				self.position, serverdn)
		self.superordinate.open()

	def exists(self):
		return self._exists

	def open(self):
		univention.admin.handlers.simpleLdap.open(self)
		self.save()

	def _ldap_pre_create(self):
		self.dn = '%s=%s,%s' % (
			mapping.mapName('extension'),
			mapping.mapValue('extension', self.info['extension']),
			self.position.getDn()
		)

	def _ldap_addlist(self):
		return [('objectClass', ['ast4ucsPhone']),
				('ast4ucsSrvchildServer', self.superordinate.dn)]

def lookup(co, lo, filter_s, base='', superordinate=None, scope='sub', 
		unique=False, required=False, timeout=-1, sizelimit=0):
	filter = univention.admin.filter.conjunction('&', [
		univention.admin.filter.expression(
			'objectClass', "ast4ucsPhone")
	])

	if superordinate:
		filter.expressions.append(univention.admin.filter.expression(
				'ast4ucsSrvchildServer', superordinate.dn))
 
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
	return res

def identify(dn, attr, canonical=0):
	return 'ast4ucsPhone' in attr.get('objectClass', [])

