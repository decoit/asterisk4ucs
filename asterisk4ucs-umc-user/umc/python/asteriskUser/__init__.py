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

class Instance( univention.management.console.modules.Base ):
    def getSettings( self, request ):
        self.finished( request.id, {} )

    def setSettings( self, request ):
        self.finished( request.id, "success" )

    def phonesQuery(self, request):
        request.status = SUCCESS
        self.finished(request.id, [{
            "extension": 42,
            "name": "Telefon 42",
        }])

