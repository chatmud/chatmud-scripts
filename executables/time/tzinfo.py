#!/usr/bin/env python

# Ghetto and quick way to output the most up-to-date time zone data from a system as JSON
# Author: distantorigin <admin@anomalousabode.com>

import sys, pytz, time, json
from datetime import datetime, timedelta

data = {}
timezone_country = {}
cc_zones = {}

for code in pytz.country_timezones:
    timezones = pytz.country_timezones[code]
    for timezone in timezones:
        cc_zones[timezone] = code
for i in pytz.common_timezones:
    tz = pytz.timezone(i)
    data[str(tz)] = {}
    now = pytz.utc.localize(datetime.utcnow())
    if len(sys.argv) == 2:
        lt = datetime.fromtimestamp(int(sys.argv[1]))
    else:
        lt = tz.localize(datetime.now())
    tzkey = str(tz)
    data[tzkey]['is_dst'] = int(now.astimezone(tz).dst() != timedelta(0))
    changeovers = []
    if hasattr(tz, '_utc_transition_times'):
        for changeover in tz._utc_transition_times:
            try:
                changeovers.append([int(tz.localize(changeover).dst() != timedelta(0)), int(time.mktime(changeover.timetuple())), tz.localize(changeover).strftime('%Z')])
            except:
                pass
        data[tzkey]['UTC_transitions'] = changeovers
    data[tzkey]['abbrev'] = lt.strftime('%Z')
    data[tzkey]['offset'] = lt.utcoffset().total_seconds()
    try:
        data[tzkey]['country_code'] = cc_zones[tzkey]
    except:
        pass
    data[tzkey]['timestamp'] = now.timestamp()
data = json.dumps(data)
print(data)
