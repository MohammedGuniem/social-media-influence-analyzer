from datetime import datetime


class Timer:
    def getCurrentTime(self):
        return round(datetime.utcnow().timestamp(), 2)

    def calculate_runtime(self, last_time_checkpoint):
        return round(self.getCurrentTime() - last_time_checkpoint, 2)
