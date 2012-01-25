import univention.management.console.modules

class Instance( univention.management.console.modules.Base ):
    def getSettings( self, request ):
        self.finished( request.id, {} )

    def setSettings( self, request ):
        self.finished( request.id, "success" )

