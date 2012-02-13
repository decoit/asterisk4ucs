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
            extension: 42,
            name: "Telefon 42",
        }])

