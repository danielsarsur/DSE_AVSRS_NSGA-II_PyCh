"""
The SimPy Environment is extended with the execute and select functions.
These are used to make simulation in SimPy more similar to Chi.

These execute function is used to execute a communicator.
E.g. Environment.execute( Channel.receive() )
Which executes a receive task.

The select function is used to execute ONLY one of the given communicators, 
When one is executed, the other communicators all are aborted.
E.g. Environment.select( Channel.receive(), Channel.send(entity) )
Which executes EITHER a receive or a send.

"""
# ==========================================================
# IMPORTS
# ==========================================================
import simpy
from simpy import AnyOf
from numpy import random
from PyCh import CommunicationEvent

# ==========================================================
# Environment
# ==========================================================
class Environment(simpy.Environment):

    @property
    def time(self):
        """ Returns the current simulation time

        This is an alternative to environment.now more similar to Chi

        :return: the current simulation time
        """
        return self.now

    def delay(self, time):
        """ Can be used to delay a process for a specific duration

        This is an alternative to environment.timeout() more similar to Chi
        can be used in a process using "yield environment.delay(time)"

        :param time: the (simulation) time duration during which the process must wait
        :return: a SimPy timeout event
        """
        return self.timeout(time)

    @staticmethod
    def execute(communication_event):
        """ Used to communicate over a channel using "yield environment.execute(communication_event)"

        This function can be used in a process to communicate over a channel.
        It is used as following: "yield environment.execute(communication_event)"
        The process will continue after the yield statement when communication has occurred.

        When used with a receiver it can also be used as "entity = yield environment.execute(receiver)"
        to return the received entity. This can also be obtained later using receiver.entity

        :param communication_event: The communication_event (sender/receiver)
        """
        communication_event.start_process()

        return communication_event.communication

    def select(self, *events):  # TODO: documentation
        """ The select function allows a process to wait for one of a list senders/receivers to communicate.

        This is useful if it is unknown which communication_event (sender/receiver) will first be ready.
        The process will wait till one of the communication_events has communicated (which is the selected
        communication_event), at which point communication by the other communication_events is 'aborted'.
        If multiple communication_events are able to communicate at the same time, then only one is selected at random.

        Can be used through either:

        - "environment.select(*communication_events)"
        - or "environment.select(communication_event1, communication_event2, ...)"
        - or a combination of both: "environment.select(*communication_events123, communication_event4, ...)"

        The process will continue after the yield statement when communication has occurred.

        If at least one of the communication_events is a receiver, then:
        "entity = yield environment.select(*communication_events)"
        returns the received entity if a receiver is selected.
        If a sender is selected, the yield statement returns None

        :param communication_events: the communication_events of which only one will be selected
        """

        # Removes all events of NoneType (for which the guard is false)
        events = [c for c in events if c]
        # Check if the correct input is given, and if not, give an error.
        communication_events = []
        other_events = []
        for c in events:
            if isinstance(c, CommunicationEvent):
                communication_events.append(c)
                if c.communication_started:
                    raise ValueError(
                        'The communication_event has already started its process,'
                        'which is not allowed when used with the select statement.'
                    )
            if not isinstance(c, CommunicationEvent):
                if isinstance(c, simpy.Event):
                    other_events.append(c)
                else:
                    raise TypeError(
                        'One of the events is of an incorrect type.'
                    )
            if self != c.env:
                raise ValueError(
                    'It is not allowed to mix events from different '
                    'environments'
                )

        # Only one communication_event is selected. Every communication_event must know who the other communication_events are.
        # The reason is that the communication_events must communicate to each other
        for c in communication_events:
            other_communication_events = [x for x in communication_events if x != c]
            c.mutual_exclusive_communication_events.extend(other_communication_events)

        def _select_process(env, communication_events, other_events):
            """ the selection process used by the select statement"""

            # start the send/receive processes for all communication_events.
            # The order in which processes are started determines their prioritization
            # We reshuffle this order randomly to randomize prioritization
            # Note: it would also be acceptable to keep the order of the list unchanged.
            random.shuffle(communication_events)

            for c in communication_events:
                c.start_process()

            # start waiting till one of the processes is selected
            events = [c.communication for c in communication_events]
            events.extend(other_events)
            yield AnyOf(env, events)

            entity = None
            for c in communication_events:
                if c.selected:
                    entity = c.communication.value
            for e in other_events:
                if e.processed:
                    entity = e.value
                    # Other event was selected, so we need to manually unregister all communication events.
                    for c in communication_events:
                        c.unregister()
            return entity

        return self.process(_select_process(self, communication_events, other_events))


# ==========================================================
# Selected function
# ==========================================================
def selected(communication_event):
    """ Used to evaluate if a communication_event has been selected.

    :param communication_event: the communication_event (sender/receiver)
    :return: a bool which denotes if the communication_event has been selected or not
    """
    if communication_event is None:
        return False
    elif isinstance(communication_event, CommunicationEvent):
        return communication_event.selected
    else:
        raise TypeError(
            'The input is of the incorrect type.'
        )

# ==========================================================
# Ready function
# ==========================================================
def ready(event):
    """ Used to evaluate if an event has finished

    :param event: the event
    :return: a bool which denotes if the event has finished
    """
    if event is None:
        return False
    elif isinstance(event, simpy.Event):
        return event.processed
    else:
        raise TypeError(
            'The input is of the incorrect type.'
        )

# ==========================================================
# Ready function
# ==========================================================
def output(event):
    """ Used to evaluate if an event has finished

    :param event: the event
    :return: a bool which denotes if the event has finished
    """
    if event is None:
        return False
    elif isinstance(event, simpy.Event):
        return event.value
    else:
        raise TypeError(
            'The input is of the incorrect type.'
        )

# ==========================================================
# Process decorator
# ==========================================================
def process(func):
    """ A decorator for process definitions.

    The first argument of a process should always be its environment, e.g.:

    @process
    def Server(env,...):
        ...

    Look up python decorators for more information.
    """
    def wrapper(*args, **kwargs):
        """"""
        # first check if any of the arguments is an environment
        env = None
        for arg in args:
            if isinstance(arg, Environment):
                env = arg

        if not env:
            raise TypeError(
                'The first argument of a process should always'
                'be its Environment.'
            )
        return env.process(func(*args, **kwargs))

    return wrapper
