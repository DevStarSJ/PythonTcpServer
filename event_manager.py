ENCODING = 'utf-8'

def translate_protocol(bytes):
    tokens = bytes.decode(ENCODING).split('|')

    sequence_number = None
    event_type = None
    from_id = None
    to_id = None

    if len(tokens) > 1:
        sequence_number = int(tokens[0])
        event_type = tokens[1]

    if len(tokens) > 2:
        from_id = int(tokens[2])

    if len(tokens) > 3:
        to_id = int(tokens[3])

    return sequence_number, event_type, from_id, to_id
