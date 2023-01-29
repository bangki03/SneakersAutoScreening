import time
import random
from datetime import datetime

def sleep_random(t_min, t_max):
    time.sleep(random.uniform(t_min,t_max))


def get_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M')