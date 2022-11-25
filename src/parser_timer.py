import schedule
import time
import datetime
# import spiderrr

timer_ = datetime.time
days_ = list

def set_time(t: datetime.time):
    global timer_
    timer_ = t
    print(t)

def set_days(days: list):
    global days_
    days_ = days
    print(days)
        
#TODO: Реализовать таймер

# schedule.every().day.do(spiderrr.SpiderRadugaFile().start_parse())

# while True:
#     schedule.run_pending()
#     time.sleep(3)