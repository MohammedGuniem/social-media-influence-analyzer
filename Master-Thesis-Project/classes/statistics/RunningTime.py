from datetime import datetime


class Timer:
    def __init__(self):
        self.start = 0.00

    def getCurrentTime(self):
        return round(datetime.utcnow().timestamp(), 2)

    def tic(self):
        self.start = self.getCurrentTime()

    def toc(self):
        return self.getCurrentTime() - self.start

    def calculate_time_difference(self, last_time_checkpoint):
        return round(self.getCurrentTime() - last_time_checkpoint, 2)
