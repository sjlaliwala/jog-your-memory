import datetime

def reformat_date_string(date_str, from_format, to_format):
    try:
        return datetime.datetime.strptime(date_str, from_format).strftime(to_format)
    except ValueError:
        raise ValueError('could not reformat date string')

def date_string_to_date_time(date_str, from_format):
    try:
        return datetime.datetime.strptime(date_str, from_format)
    except ValueError:
        raise ValueError('could not parse date_str')


