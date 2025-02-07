def minutes_to_average(times):
    total_seconds = 0
    for time in times:
        minutes, seconds = map(int, time.split(":"))
        total_seconds += minutes * 60 + seconds

    average_seconds = total_seconds / len(times)

    return average_seconds

def minutes_to_average_print(times):
    total_seconds = 0
    for time in times:
        minutes, seconds = map(int, time.split(":"))
        total_seconds += minutes * 60 + seconds
    if len(times) != 0:
        average_seconds = total_seconds / len(times)

        average_minutes = int(average_seconds // 60)
        average_seconds = int(average_seconds % 60)

        return f'{average_minutes:02}:{average_seconds:02}'
    else:
        return '00:00'

def time_to_minutes(time_str):
    # Split the string into minutes and seconds
    minutes, seconds = map(int, time_str.split(":"))
    
    # Convert to minutes as a decimal (seconds divided by 60)
    total_minutes = minutes + seconds / 60
    
    return total_minutes

def time_to_seconds(time_str):
    minutes, seconds = map(int, time_str.split(":"))
    total_seconds = minutes * 60 + seconds 
    return total_seconds
