# 行程
class Trip:
    def __init__(self):
        self.trip_id = None
        self.trip_name = None
        self.destination = None
        self.start_date = None
        self.end_date = None
        self.create_time = None
        # 是否被收藏
        self.is_collect = None
        # ai行程
        self.ai_plan = None