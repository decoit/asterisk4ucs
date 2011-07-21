# coding=utf-8

import univention.admin.filter
import univention.admin.handlers
from univention.admin.handlers.asterisk import ConfRefreshMixin
import univention.admin.syntax

module = "asterisk/mailbox"
childs = 0
short_description = u"Anrufbeantworter"
long_description = u"Anrufbeantworter"
operations = ['add', 'edit', 'remove', 'search', 'move']
options = {}

layout = [
	univention.admin.tab('Allgemein', 'Allgemeine Einstellungen', [
		[ univention.admin.field("id") ],
		[ univention.admin.field("password") ],
		[ univention.admin.field("owner"),
			univention.admin.field("email") ],
	])
]

property_descriptions = {
	"commonName": univention.admin.property(
		short_description="Name",
		syntax=univention.admin.syntax.string,
		identifies=True,
		required=True
	),
	"id": univention.admin.property(
		short_description="Mailbox-Nummer",
		syntax=univention.admin.syntax.phone,
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
	"owner": univention.admin.property(
		short_description=u"Benutzer",
		syntax=univention.admin.syntax.LDAP_Search(
			filter="objectClass=inetOrgPerson",
			attribute=['users/user: username'],
			value='users/user: dn'
		),
		required=True,
	),
}

mapping = univention.admin.mapping.mapping()
mapping.register("commonName", "cn",
	None, univention.admin.mapping.ListToString)
mapping.register("id", "ast4ucsMailboxId",
	None, univention.admin.mapping.ListToString)
mapping.register("password", "ast4ucsMailboxPassword",
	None, univention.admin.mapping.ListToString)
mapping.register("email", "ast4ucsMailboxNotifybymail",
	None, univention.admin.mapping.ListToString)
mapping.register("owner", "owner",
	None, univention.admin.mapping.ListToString)

class object(univention.admin.handlers.simpleLdap, ConfRefreshMixin):
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
                self.info['commonName'] = "mailbox " + self.info["id"]

	def _ldap_pre_create(self):
		self.dn = '%s=%s,%s' % (
			mapping.mapName('commonName'),
			mapping.mapValue('commonName', self.info['commonName']),
			self.position.getDn()
		)

	def _ldap_addlist(self):
		return [('objectClass', ['top', 'ast4ucsMailbox' ])]


def lookup(co, lo, filter_s, base='', superordinate=None, scope='sub', 
		unique=False, required=False, timeout=-1, sizelimit=0):
	filter = univention.admin.filter.conjunction('&', [
		univention.admin.filter.expression(
			'objectClass', "ast4ucsMailbox")
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
	return 'ast4ucsMailbox' in attr.get('objectClass', [])

