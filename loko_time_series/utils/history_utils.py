import datetime
import os


class History:
    def __init__(self, date=None, time=None):
        if isinstance(date, datetime.datetime):
            self.date = date.date()
            self.time = date.time()
        else:
            dt = datetime.datetime.now()
            self.date = date or dt.date()
            self.time = time or dt.time()

    def historify(self, name, joiner: str = "_"):
        name, ext = os.path.splitext(name)
        return joiner.join([name, self.date.strftime("%d-%m-%Y"), self.time.strftime("%H-%M-%S")]) + ext

    def get_time_parsed(self, name, joiner: str = "_", format = None):
        name, ext = os.path.splitext(name)
        dt = name[-19:]
        if not format:
            format = joiner.join(["%d-%m-%Y", "%H-%M-%S"])
        return datetime.datetime.strptime(dt,format)

    def json(self):
        return dict(datetime=str(datetime.datetime.combine(self.date, self.time)))
