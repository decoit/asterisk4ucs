#!/usr/bin/env python2
# coding=utf-8

"""
Asterisk4UCS-Importscript für OSGA-Kontakte

Dieses Script importiert Kontakte aus der OSGA-Groupware in ein Asterisk4UCS-
Adressbuch.

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

import sys

try:
	astpbdn = sys.argv[1]
	pghost = sys.argv[2]
	pgdb = sys.argv[3]
	pguser = sys.argv[4]
	pgpass = sys.argv[5]
except IndexError:
	print "Usage:"
	print "%s <phonebook DN> <host> <database> <user> <pass>" % sys.argv[0]
	sys.exit(1)

import re
from asterisk4ucs import PhoneBookWrapper
import psycopg2
import psycopg2.extras
import univention.admin.uexceptions

pb = PhoneBookWrapper(astpbdn)
print "Deleting all contacts in phonebook %s, may take a while..." % (
		pb.getName())
pb.empty()
print "Done."
print "Importing..."

conn = psycopg2.connect(host=pghost, database=pgdb,
		user=pguser, password=pgpass)

cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

cur.execute("SELECT * FROM contacts "
		"WHERE status != 'D' AND acc_read = 'group';")
contacts = cur.fetchall()

def formatNumber(number):
	if not number:
		return None
	return re.sub(r"[-/ ]", "", number)

for contact in contacts:
	sys.stdout.write("%s (%s)          \r" % (
			contact["nachname"], contact["id"]))
	sys.stdout.flush()
	try:
		dn = pb.addContact(
			firstname = contact["vorname"],
			lastname = contact["nachname"],
			organisation = contact["firma"],
			phones = [formatNumber(contact["tel1"]),
					formatNumber(contact["tel2"])],
			mobiles = formatNumber(contact["mobil"]),
			faxes = formatNumber(contact["fax"]),
		)
		#print "Created %s" % dn
	except univention.admin.uexceptions.valueInvalidSyntax:
		print "Syntax error in contact %s (%s), skipping." % (
				contact["nachname"], contact["id"])
	except univention.admin.uexceptions.objectExists:
		print "Found duplicate contact %s (%s), skipping." % (
				contact["nachname"], contact["id"])

print "Done.          "

