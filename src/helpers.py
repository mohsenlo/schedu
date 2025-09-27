def split_time(time: str) -> tuple[int, int]:
    try:
        h, m = map(int, time.split(":"))
    except:
        raise RuntimeError("Invalid time!!!")
    return h, m


def end_is_on_tomorrow(start_time: str, end_time: str):
    h1, m1 = split_time(start_time)
    h2, m2 = split_time(end_time)
    t1 = h1 * 60 + m1
    t2 = h2 * 60 + m2
    if t2 < t1:
        return True
    else:
        return False


def convert_time_to_minute(time: str):
    h, m = map(int, time.split(":"))
    return h * 60 + m


def convert_minute_to_time(minute: str):
    h = int(int(minute) / 60)
    m = int(minute) % 60
    return str(h) + ":" + str(m)
