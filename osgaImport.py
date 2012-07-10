#!/usr/bin/env python2

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
import ast4ucs
import psycopg2
import psycopg2.extras
import univention.admin.uexceptions

pb = ast4ucs.phoneBookWrapper(astpbdn)
pb.empty()

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

