# 创建出来的行程
class Ctsrip:
    def __init__(self, ctrip_id, ctrip_name, destination, start_date, end_date, create_time, is_collect, ai_plan):
        self.ctrip_id = ctrip_id
        self.ctrip_name = ctrip_name
        self.destination = destination
        self.start_date = start_date
        self.end_date = end_date
        self.create_time = create_time
        # 是否被收藏
        self.is_collect = is_collect
        # ai行程
        self.ai_plan = ai_plan