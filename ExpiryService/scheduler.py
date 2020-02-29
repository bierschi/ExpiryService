import logging
import time
import sched


class Scheduler:
    """ class Scheduler to schedule events for matches

    USAGE:
            scheduler = Scheduler()
            scheduler.run()

    """
    def __init__(self):
        self.logger = logging.getLogger('ExpiryService')
        self.logger.info('create class Scheduler')

        # create scheduler
        self.scheduler = sched.scheduler(time.time, time.sleep)

    def register_events(self, timestamp, handler, prio, *args):
        """ register events to execute

        :param timestamp: start timestamp
        :param handler: handler function
        :param prio: prio for the event
        :param args: variable arguments

        :return event id
        """
        event_id = self.scheduler.enterabs(timestamp, prio, handler, argument=args)
        return event_id

    def get_event_queue(self):
        """ get current event queue

        :return: event queue
        """
        return self.scheduler.queue

    def is_queue_empty(self):
        """ is current queue empty

        :return: bool, true or false
        """
        return self.scheduler.empty()

    def cancel_event(self, eventid):
        """ cancels an event

        :param eventid: specific event id
        """
        self.scheduler.cancel(event=eventid)

    def run(self, blocking=True):
        """ runs the scheduler

        """
        self.scheduler.run(blocking=blocking)

    def periodic(self, interval, action, args=()):
        """ creates a periodic task

        :param interval: periodic interval
        :param action: action handler
        :param args: args for the action handler
        """
        self.scheduler.enter(interval, 1, self.periodic, (interval, action, args))
        action(*args)


if __name__ == '__main__':
    scheduler = Scheduler()
    scheduler.periodic(10, scheduler.test, (5, ))
    scheduler.run(blocking=True)
