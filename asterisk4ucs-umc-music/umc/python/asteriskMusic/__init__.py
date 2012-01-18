import univention.management.console.modules

class Instance( univention.management.console.modules.Base ):
    def hallo( self, request ):
        self.finished( request.id, "Hallo, Programmierer!" )

