"""Check the transport manifests served by production, independently of data builds."""
import datetime as dt
import json
import sys
import time
import urllib.request

BASE = 'https://timetogrowup.github.io/WENARE/distribution/'
UTC = dt.timezone.utc
WARNING_HOURS = 18

def assess(manifest, now):
    try:
        start = dt.datetime.fromisoformat(manifest['validFromUtc'].replace('Z', '+00:00'))
        end = dt.datetime.fromisoformat(manifest['validUntilUtc'].replace('Z', '+00:00'))
        if start.tzinfo is None or end.tzinfo is None or start >= end:
            raise ValueError('invalid validity window')
        hours = (end - now).total_seconds() / 3600
        state = 'future' if start > now else 'expired' if hours <= 0 else 'warning' if hours < WARNING_HOURS else 'healthy'
        return dict(state=state, hoursRemaining=round(hours, 2), validUntilUtc=end.isoformat())
    except (KeyError, ValueError, TypeError, AttributeError):
        return dict(state='invalid', error='Période de validité absente ou incorrecte')

def check(folder, now):
    error = None
    for attempt in range(2):
        try:
            request = urllib.request.Request(BASE + folder + '/manifest.json?health=' + str(time.time_ns()), headers={'Cache-Control': 'no-cache', 'User-Agent': 'WENARE-Transport-Health/1'})
            with urllib.request.urlopen(request, timeout=20) as response:
                manifest = json.load(response)
            return dict(dataset=folder, **assess(manifest, now))
        except Exception as exc:
            error = type(exc).__name__ + ': ' + str(exc)
            if attempt == 0:
                time.sleep(2)
    return dict(dataset=folder, state='unreachable', error=error)

def main():
    now = dt.datetime.now(UTC)
    datasets = [check(folder, now) for folder in ('timetable', 'mobility')]
    report = dict(checkedAtUtc=now.isoformat(), warningHours=WARNING_HOURS, healthy=all(d['state'] == 'healthy' for d in datasets), datasets=datasets)
    with open('transport-health.json', 'w') as output:
        json.dump(report, output, ensure_ascii=False, indent=2)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['healthy'] else 1

if __name__ == '__main__':
    sys.exit(main())
