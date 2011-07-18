# coding=utf-8

import univention.admin.filter
import univention.admin.handlers
import univention.admin.syntax

module = "asterisk/sipPhone"
childs = 0
short_description = u"SIP-Telefon"
long_description = u"SIP-Telefon"
operations = ['add', 'edit', 'remove', 'search', 'move']
options = {}

layout = [
	univention.admin.tab('Allgemein', 'Allgemeine Einstellungen', [
		[ univention.admin.field("extension"),
			univention.admin.field("ipaddress")],
		[ univention.admin.field("macaddress"),
			univention.admin.field("hostname") ],
		[ univention.admin.field("mailbox"),
			univention.admin.field("maxrings") ],
		[ univention.admin.field("phonetype"),
			univention.admin.field("profile") ],
		[ univention.admin.field("password"),
			univention.admin.field("owner") ],
	])
]

property_descriptions = {
	"name": univention.admin.property(
		short_description="Name",
		syntax=univention.admin.syntax.string,
		identifies=True,
		required=True
	),
	"extension": univention.admin.property(
		short_description="Durchwahl",
		syntax=univention.admin.syntax.phone,
		required=True
	),
	"ipaddress": univention.admin.property(
		short_description="IP-Adresse",
		syntax=univention.admin.syntax.ipAddress
	),
	"macaddress": univention.admin.property(
		short_description="MAC-Adresse",
		syntax=univention.admin.syntax.string
	),
	"hostname": univention.admin.property(
		short_description="Hostname",
		syntax=univention.admin.syntax.hostName
	),
	"mailbox": univention.admin.property(
		short_description="Mailbox",
		syntax=univention.admin.syntax.phone
	),
	"maxrings": univention.admin.property(
		short_description=u"Höchstzahl Klingeln",
		long_description=(u"Nach wievielmaligem Klingeln soll die" + 
			u"Mailbox den Anruf entgegennehmen?"),
		syntax=univention.admin.syntax.integer
	),
	"phonetype": univention.admin.property(
		short_description="Telefontyp",
		syntax=univention.admin.syntax.string
	),
	"profile": univention.admin.property(
		short_description="Profil",
		syntax=univention.admin.syntax.string
	),
	"password": univention.admin.property(
		short_description="Passwort",
		syntax=univention.admin.syntax.userPasswd
	),
	"owner": univention.admin.property(
		short_description="Benutzer",
		syntax=univention.admin.syntax.LDAP_Search(
                        filter="objectClass=inetOrgPerson",
                        attribute=['users/user: username'],
                        value='users/user: dn'
                ),
		required=True,
	),
}

mapping = univention.admin.mapping.mapping()
mapping.register("name", "cn",
	None, univention.admin.mapping.ListToString)
mapping.register("extension", "AstExtension",
	None, univention.admin.mapping.ListToString)
mapping.register("ipaddress", "AstAccountIpaddr",
	None, univention.admin.mapping.ListToString)
mapping.register("macaddress", "macAddress",
	None, univention.admin.mapping.ListToString)
mapping.register("hostname", "AstAccountHost",
	None, univention.admin.mapping.ListToString)
mapping.register("mailbox", "AstAccountMailbox",
	None, univention.admin.mapping.ListToString)
mapping.register("maxrings", "ast4ucsPhoneMaxrings",
	None, univention.admin.mapping.ListToString)
mapping.register("phonetype", "ast4ucsPhoneType",
	None, univention.admin.mapping.ListToString)
mapping.register("profile", "ast4ucsPhoneProfile",
	None, univention.admin.mapping.ListToString)
mapping.register("password", "AstAccountSecret",
	None, univention.admin.mapping.ListToString)
mapping.register("owner", "owner",
	None, univention.admin.mapping.ListToString)

class object(univention.admin.handlers.simpleLdap):
	module=module

	def __init__(self, co, lo, position, dn='', superordinate=None,
			arg=None):
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
	
	def _ldap_pre_ready(self):
		self.info['name'] = self.info["extension"]
	
	def _ldap_pre_create(self):
		self.dn = '%s=%s,%s' % (
			mapping.mapName('name'),
			mapping.mapValue('name', self.info['name']),
			self.position.getDn()
		)
	
	def _ldap_addlist(self):
		return [('objectClass', ['top', 'ast4ucsPhone',
			'AsteriskExtension', 'AsteriskSIPUser' ])]


def lookup(co, lo, filter_s, base='', superordinate=None, scope='sub', 
		unique=False, required=False, timeout=-1, sizelimit=0):
	filter = univention.admin.filter.conjunction('&', [
		univention.admin.filter.expression(
			'objectClass', "ast4ucsPhone")
	])
 
	if filter_s:
		filter_p = univention.admin.filter.parse(filter_s)
		univention.admin.filter.walk(filter_p, 
			univention.admin.mapping.mapRewrite, arg=mapping)
		filter.expressions.append(filter_p)
 
	res = []
	for dn in lo.searchDn(unicode(filter), base, scope, unique, required, 
			timeout, sizelimit):
		res.append(object(co, lo, None, dn))
	return res

def identify(dn, attr, canonical=0):
	return 'ast4ucsPhone' in attr.get('objectClass', [])

