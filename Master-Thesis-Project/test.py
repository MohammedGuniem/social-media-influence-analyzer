from datetime import date
from classes.statistics.RunningTime import Timer
import time

timer = Timer()

timer.tic()

time.sleep(1)

runtime = timer.toc()
print(runtime)
timer.tic()
time.sleep(4)
runtime = timer.toc()
print(runtime)

print(date.today())
