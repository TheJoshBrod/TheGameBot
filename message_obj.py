class message_obj:
    def __init__(self, message):
        try:
            self.username = message.author.nick
        except:
            self.username = message.author.global_name
        try:
            self.channel = str(message.channel.name) 
        except:
            self.channel = f"private_message_with_{message.author.global_name}"
        try:
            self.guild = message.guild.id
        except:
            self.guild = f"private_message_with_{message.author.global_name}"
        self.content = message.content