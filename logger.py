import pytz
import logging
import datetime

class Formatter(logging.Formatter):
    def converter(self, timestamp):
        dt = datetime.datetime.fromtimestamp(timestamp, tz=pytz.UTC)
        return dt.astimezone(pytz.timezone('US/Eastern'))

    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            try:
                s = dt.isoformat(timespec='milliseconds')
            except TypeError:
                s = dt.isoformat()
        return s

class logger:
    def __init__(self, filename):
        self.filename = filename
    
    def critical(self, msg):
        console = logging.FileHandler(self.filename)
        console.setFormatter(Formatter('%(asctime)s;%(name)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S'))
        logging.getLogger('').addHandler(console)
        logging.critical(msg)
        print(msg)

if __name__ == '__main__':
    logger = logger("crypto.log")
    logger.critical("hello world")