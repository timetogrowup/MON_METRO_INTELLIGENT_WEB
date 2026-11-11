"""Reject a claimed four-day window without actual dated departures on each day."""
import collections
import datetime as dt
import json
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo('Europe/Paris')

def coverage(root, manifest):
    first = dt.datetime.fromisoformat(manifest['validFromUtc']).astimezone(TZ).date()
    last = dt.datetime.fromisoformat(manifest['validUntilUtc']).astimezone(TZ).date()
    required = {str(first + dt.timedelta(days=i)) for i in range(4)}
    if (last-first).days != 4:
        raise ValueError('Four real service days required')
    counts = collections.Counter()
    for meta in manifest['lines'].values():
        data = json.loads((root/meta['file']).read_bytes())
        for rows in data['groups'].values():
            for row in rows:
                counts[str(dt.datetime.fromtimestamp(row[0], TZ).date())] += 1
    if not required <= counts.keys():
        raise ValueError('Missing dated departures for reserve days: ' + str(sorted(required-counts.keys())))
    return dict(counts)

def main():
    for folder in ['timetable', 'mobility']:
        root = Path('distribution')/folder
        print(folder, coverage(root, json.loads((root/'manifest.json').read_bytes())))

if __name__ == '__main__': main()
