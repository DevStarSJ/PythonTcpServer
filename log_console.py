from datetime import datetime

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

class ConsoleLogger(object):
    def __init__(self):
        pass

    def log(self, event):
        print(get_log_message(event))

    def quit_log(self, id):
        print('[{0}] : [{1}] quit.'.format(now(), id))

    def connect_log(self, peer):
        print('[{0}] : [{1}] connected'.format(now(), peer.name))

    def regist_log(self, peer):
        print('[{0}] : [{1}] regist ID [{2}]'.format(now(), peer.name, peer.id))
