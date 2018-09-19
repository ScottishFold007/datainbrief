


def get_hours(description):
    # search for hours
    words_for_hour = {'hour', 'time', 'stunde', 'ora', 'heure', 'uur', 'tunnin', 'timme', 'saat', 'hora'}

    if any(word in description for word in words_for_hour):
        # add details to item info
        hours = 'hour in description'
    else:
        hours = 'no hour info'

    return hours