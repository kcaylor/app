# forecast.io icons:
# clear-day, clear-night, rain, snow,
# sleet, wind, fog, cloudy, partly-cloudy-day
# or partly-cloudy-night


def weather_icon(condition=None):

    conditions = {
        'clear-day': 'wi-day-sunny',
        'clear-night': 'wi-night-clear',
        'rain': 'wi-rain',
        'snow': 'wi-snow',
        'fog': 'wi-fog',
        'cloudy': 'wi-cloudy',
        'partly-cloudy-day': 'wi-day-cloudy',
        'partly-cloudy-night': 'wi-night-cloudy',
        'default': ''
    }
    if condition:
        if condition in conditions:
            return conditions[condition]
        else:
            return conditions['default']
    else:
        return conditions['default']
