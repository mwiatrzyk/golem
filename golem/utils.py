def number_of_times_to_string(value):
    if value == 0:
        return 'never'
    elif value == 1:
        return 'once'
    elif value == 2:
        return 'twice'
    else:
        return "%s times" % value
