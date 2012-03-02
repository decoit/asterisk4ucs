
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

class ast4ucsExtmodeSyntax(select):
	name = "ast4ucsExtmodeSyntax"
	choices = [
		('hide',   "Durchwahl verstecken"),
		('first',  "Durchwahl des ersten Telefons"),
		('normal', "Durchwahl des jeweiligen Telefons"),
	]

class ast4ucsDurationSyntax(integer):
	name = "ast4ucsDurationSyntax"

	@classmethod
	def parse(self, text):
		try:
			number = int(text)
			if number > 300 or number < 1:
				raise ValueError
		except ValueError:
			raise univention.admin.uexceptions.valueError, \
				"Value must be a number between 1 and 120!"
		return text

class ast4ucsMusicSyntax(select):
	name = "ast4ucsMusicSyntax"
	def __init__(self, srv):
		if srv:
			self.choices = [(x,x) for x in srv.info.get("music", [])]
		else:
			self.choices = [("moh", "moh")]

