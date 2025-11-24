# 消息模板
class Message:
    def __init__(self, message_id, content, user_id):
        self.message_id = message_id
        self.text = content
        self.user_id = user_id