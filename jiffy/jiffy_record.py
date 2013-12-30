from datetime import datetime

class JiffyRecord(object):

    """JiffyRecord"""

    def __init__(self, line):
        """Convert a csv line to jiffy record """
        elements = line.split(',')
        self.customer = elements[0]
        self.project = elements[1]
        self.task = elements[2]
        self.start = datetime.strptime(elements[3], '%Y-%m-%d %H:%M:%S')
        self.stop = datetime.strptime(elements[4], '%Y-%m-%d %H:%M:%S')
        self.duration = int(elements[5])
        self.note = elements[6]

    def output(self):
        """Print out current object"""
        start = self.start.strftime('%Y-%m-%d %H:%M:%S')
        stop = self.stop.strftime('%Y-%m-%d %H:%M:%S')
        print('%s %s: (%s - %s) %d' % (self.customer, self.project, start, stop, self.duration))

    def is_commute_to_work(self):
        return (self.customer == '"Me"' and self.project == '"Commute"'
               and self.start.hour <= 11 and self.start.hour >= 9)

    def is_commute_after_work(self):
        return (self.customer == '"Me"' and self.project == '"Commute"'
               and self.start.hour >= 18 and self.start.hour <= 23)

    def is_houzz(self):
        return self.customer == '"Houzz"' and self.project == '"Work"'
