class NoMessagePermissionException(Exception) :
	"""Raised when the bot does not have permission to send a message"""

	def __init__(self, message="Missing permission to send message: ", missing_permissions: list = ()) :
		self.message = message
		super().__init__(self.message + ", ".join(missing_permissions))


class NoChannelException(Exception) :
	"""Raised when the server does not have a channel set to send a message"""

	def __init__(self, message="No channel set or does not exist, check the config or fill in the required arguments.") :
		self.message = message
