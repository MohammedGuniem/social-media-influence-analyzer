from datetime import datetime


class Timer:
    def __init__(self):
        self.start = 0.00

    def getCurrentTime(self):
        return round(datetime.utcnow().timestamp(), 2)

    def tic(self):
        self.start = self.getCurrentTime()
        return self.start

    def toc(self):
        start = self.start
        return self.getCurrentTime() - start

    def reset(self):
        self.start = 0.00
