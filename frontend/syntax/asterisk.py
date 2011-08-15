
class ast4ucsExtmodeSyntax(select):
	name = "ast4ucsExtmodeSyntax"
	choices = [
		('hide',   "Durchwahl verstecken"),
		('first',  "Durchwahl des ersten Telefons"),
		('normal', "Durchwahl des jeweiligen Telefons"),
	]

class ast4ucsDurationSyntax(integer):
	name = "ast4ucsDurationSyntax"

	def parse(self, text):
		try:
			number = int(text)
			if number > 120 or number < 1:
				raise ValueError
		except ValueError:
			raise univention.admin.uexceptions.valueError, \
				"Value must be a number between 1 and 120!"
		return text

