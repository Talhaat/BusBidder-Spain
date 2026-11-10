# Time helpers - turn "HH:MM" text into minutes and back


#Function to turn "HH:MM" text into minutes after midnight
# Input is time as "HH:MM" text, return minutes as an int, like "06:30" -> 390.
def to_minutes(time_text):
    hours, minutes = time_text.split(":")
    return int(hours) * 60 + int(minutes)


#Function to turn minutes after midnight back into "HH:MM" text, wrapping past midnight
# Input is minutes as an int, return text like 390 -> "06:30" and 1500 -> "01:00".
def to_time_text(minutes):
    minutes = minutes % (24 * 60)
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


#Function to write a number of minutes as readable text
# Input is minutes as an int, return text like 25 -> "25 min" and 125 -> "2 h 05 min".
def to_duration_text(minutes):
    if minutes < 60:
        return f"{minutes} min"
    return f"{minutes // 60} h {minutes % 60:02d} min"
