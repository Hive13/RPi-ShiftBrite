#!/usr/bin/env python

class Message:
    """A series of messages that AsyncDisplayManager handles."""
    pass

class StopMessage:
    """Message telling the process to quit."""
    pass

class NextMessage:
    """Message telling the process to switch to a different visualization routine.
    If 'tag' is None, it will pick one at random."""
    def __init__(self, tag = None):
        self.tag = tag

class DelayMessage:
    """Message to change the current frame delay. newFrameDelay is in seconds."""
    # TODO: Throw exception with negative values
    def __init__(self, newFrameDelay):
        self.newFrameDelay = newFrameDelay

class AddRoutineMessage:
    """Message to add a new visualization routine (i.e. Demo subclass) to the
    process. 'tag' is the index by which you may identify it."""
    def __init__(self, tag, demo):
        self.tag = tag
        self.demo = demo

