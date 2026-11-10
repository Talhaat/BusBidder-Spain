# File for turning "HH:MM" times into minutes and back

def to_minutes(time_text):
    hours, minutes = time_text.split(":")
    return int(hours) * 60 + int(minutes)

def to_time_text(minutes):
    minutes = minutes % (24 * 60)
    return f"{minutes // 60:02d}:{minutes % 60:02d}"

def to_duration_text(minutes):
    if minutes < 60:
        return f"{minutes} min"
    return f"{minutes // 60} h {minutes % 60:02d} min"
