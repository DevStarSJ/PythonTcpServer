from datetime import datetime
from appsettings import get_appsettings

appsettings = get_appsettings()

ENCODING = 'utf-8'
LOG_DEBUG = appsettings["logLevel"] == "debug"


def now():
    return str(datetime.now())

def get_message(event):
    if event.event_type == 'B':
        return '[{0}][{1}] : Broadcast message.'.format(now(), event.sequence_number)
    elif event.event_type == 'S':
        return '[{0}][{1}] : [{2}] profile updated.'.format(now(), event.sequence_number, event.from_id)
    elif event.event_type == 'P':
        return '[{0}][{1}] : [{2}] send message to you.'.format(now(), event.sequence_number, event.from_id)
    elif event.event_type == 'F':
        return '[{0}][{1}] : [{2}] follows you.'.format(now(), event.sequence_number, event.from_id)

    return None

def get_log_message(event):
    if event.event_type == 'B':
        return '[{0}][{1}] : Broadcast message.'.format(now(), event.sequence_number)
    elif event.event_type == 'S':
        return '[{0}][{1}] : [{2}] profile updated.'.format(now(), event.sequence_number, event.from_id)
    elif event.event_type == 'P':
        return '[{0}][{1}] : [{2}] send message to [{3}].'.format(now(), event.sequence_number, event.from_id, event.to_id)
    elif event.event_type == 'F':
        return '[{0}][{1}] : [{2}] follows [{3}].'.format(now(), event.sequence_number, event.from_id, event.to_id)
    elif event.event_type == 'U':
        return '[{0}][{1}] : [{2}] unfollows [{3}].'.format(now(), event.sequence_number, event.from_id, event.to_id)
    return None

def log_print(message):
    if LOG_DEBUG:
        print(message)

class ConsoleClientLogger(object):
    def __init__(self):
        pass

    def log(self, event):
        message = get_log_message(event)
        if not message == None:
            log_print(message)

    def quit_log(self, id):
        log_print('[{0}] : [{1}] quit.'.format(now(), id))

    def connect_log(self, peer):
        log_print('[{0}] : [{1}] connected.'.format(now(), peer.name))

    def regist_log(self, peer):
        log_print('[{0}] : [{1}] regist ID [{2}]'.format(now(), peer.name, peer.id))


class ConsoleEventLogger(object):
    def __init__(self):
        pass

    def event_message_log(self, peer, message):
        string_message = message \
            if type(message) == str \
            else message.decode(ENCODING)
        log_print('[Event][{0}][{1}] : {2}'.format(now(), peer.name, string_message))

    def connect_log(self, peer):
        log_print('[Event][{0}][{1}] : connected.'.format(now(), peer.name))

    def quit_log(self, peer):
        log_print('[Event][{0}][{1}] : quit.'.format(now(), peer.name))
