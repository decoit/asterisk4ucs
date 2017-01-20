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
from univention.admin.handlers.asterisk import AsteriskBase

module = "asterisk/mailbox"
short_description = u"Asterisk4UCS-Management: Anrufbeantworter"
operations = ['add', 'edit', 'remove', 'search', 'move']
options = {}

childs = 0
superordinate = "asterisk/server"

# Definiert das Layout der Eingabefelder in der Weboberfläche
layout = [
	Tab('Allgemein', 'Allgemeine Einstellungen', layout = [
		[ "id" ],
		[ "password" ],
		[ "email" ],
	])
]

# Definiert die verschiedenen UDM-Attribute
# http://wiki.univention.de/index.php?title=Entwicklung_und_Integration_eigener_Module_in_Univention_Directory_Manager#property-descriptions
property_descriptions = {
	"commonName": univention.admin.property(
		short_description="Name",
		syntax=univention.admin.syntax.string,
		identifies=True,
		required=True,
		default="temp",
	),
	"id": univention.admin.property(
		short_description="Mailbox-Nummer",
		syntax=univention.admin.syntax.string,
		required=True
	),
	"password": univention.admin.property(
		short_description=u"PIN",
		syntax=univention.admin.syntax.userPasswd,
		required=True,
	),
	"email": univention.admin.property(
		short_description=u"Per eMail benachrichtigen?",
		syntax=univention.admin.syntax.boolean,
	),
}

# Definiert die Zuordnung von UDM-Attributen zu LDAP-Attributen.
# http://wiki.univention.de/index.php?title=Entwicklung_und_Integration_eigener_Module_in_Univention_Directory_Manager#mapping
mapping = univention.admin.mapping.mapping()
mapping.register("commonName", "cn",
	None, univention.admin.mapping.ListToString)
mapping.register("id", "ast4ucsMailboxId",
	None, univention.admin.mapping.ListToString)
mapping.register("password", "ast4ucsMailboxPassword",
	None, univention.admin.mapping.ListToString)
mapping.register("email", "ast4ucsMailboxNotifybymail",
	None, univention.admin.mapping.ListToString)

class object(AsteriskBase):
	module=module

	def _ldap_pre_ready(self):
		"""Wird vor der Syntaxprüfung der Eingabefelder aufgerufen und
		setzt das (auf der Weboberfläche nicht sichtbare) Feld
		"commonName" auf eine menschenlesbare Beschreibung des
		Objekts. Dieser Hack ist notwendig, weil UMC/UDM grundsätzlich
		das Attribut mit identifies=True als "Name" in der Tabelle
		der Suchergebnisse verwendet."""
		super(object, self)._ldap_pre_ready()

		self['commonName'] = "mailbox " + self["id"]

	def _ldap_addlist(self):
		"""Wird kurz vor Schreiben des LDAP-Objects aufgerufen und
		fügt die Attribute objectClass und ast4ucsSrvchild (Verweis
		zum Superordinate) hinzu.
		Bei neuen Modulen müssen die objectClass und der Attributname
		des Superordinate-Verweises angepasst werden"""

		return [('objectClass', ['ast4ucsMailbox' ]),
			('ast4ucsSrvchildServer', self.superordinate.dn)]

# Sucht nach diesem Modul zugehörigen Objekten. Berücksichtigt dabei eventuell
# übergebene Einschränkungen (filter_s) und übergeordnete Objekte
# (superordinate).
# Für neue Module müssen in diesem Code nur die objectClass und das
# LDAP-Attribut für die Superordinate-Zuordnung angepasst werden.
# (in diesem Fall ast4ucsMailbox und ast4ucsSrvchildServer)
def lookup(co, lo, filter_s, base='', superordinate=None, scope='sub', 
		unique=False, required=False, timeout=-1, sizelimit=0):
	filter = univention.admin.filter.conjunction('&', [
		univention.admin.filter.expression(
			'objectClass', "ast4ucsMailbox")
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

# Funktion, die True zurückliefert, wenn dieses Modul für das übergebene
# Objekt zuständig ist. Prüft einfach nur die LDAP objectClass.
def identify(dn, attr, canonical=0):
	return 'ast4ucsMailbox' in attr.get('objectClass', [])

