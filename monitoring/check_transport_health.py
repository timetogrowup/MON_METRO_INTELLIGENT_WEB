"""Check the transport manifests served by production, independently of data builds."""
import argparse
import hashlib
from pathlib import Path
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

def fetch_json(path, maximum=32_000_000):
    request = urllib.request.Request(BASE + path + '?health=' + str(time.time_ns()), headers={'Cache-Control': 'no-cache', 'User-Agent': 'WENARE-Transport-Health/2'})
    with urllib.request.urlopen(request, timeout=20) as response:
        raw = response.read(maximum + 1)
    if len(raw) > maximum:
        raise ValueError('File exceeds size limit')
    return json.loads(raw), raw

def verified(path, meta):
    data, raw = fetch_json(path)
    if len(raw) != meta['bytes'] or hashlib.sha256(raw).hexdigest() != meta['sha256']:
        raise ValueError('Published file integrity mismatch: ' + path)
    return data

def check(folder, now, deep=False, expected_root=None):
    for attempt in range(2):
        try:
            manifest, _ = fetch_json(folder + '/manifest.json')
            result = dict(dataset=folder, **assess(manifest, now))
            if result['state'] not in ('healthy', 'warning'):
                return result
            if expected_root is not None:
                expected = json.loads((expected_root/folder/'manifest.json').read_bytes())
                if manifest != expected:
                    return dict(dataset=folder, state='stale', error='Published manifest differs from the qualified deployment')
            if deep:
                if folder == 'timetable':
                    network, _ = fetch_json('manifest.json')
                    verified('network.json', network)
                    if network['sha256'] != manifest['networkSha256']:
                        raise ValueError('Metro reference and schedules differ')
                    samples = [max(manifest['lines'], key=lambda key: manifest['lines'][key]['bytes'])]
                else:
                    verified(folder+'/index.json', manifest['index'])
                    samples = []
                    for mode in ('rer', 'bus'):
                        lines = [key for key, meta in manifest['lines'].items() if manifest['scope'].get(key.removeprefix('IDFM:')) == mode and meta['groups'] > 0]
                        if not lines:
                            raise ValueError('No usable line for ' + mode)
                        samples.append(max(lines, key=lambda key: manifest['lines'][key]['bytes']))
                for key in samples:
                    meta = manifest['lines'][key]
                    data = verified(folder+'/'+meta['file'], meta)
                    if data['validFromUtc'] != manifest['validFromUtc'] or data['validUntilUtc'] != manifest['validUntilUtc']:
                        raise ValueError('Line validity differs from manifest')
                    if not any(row[0] > now.timestamp() for rows in data['groups'].values() for row in rows):
                        raise ValueError('No future dated departures for ' + key)
                result['verifiedLines'] = samples
            return result
        except Exception as exc:
            error = type(exc).__name__ + ': ' + str(exc)
            failure_state = 'invalid' if isinstance(exc, (ValueError, KeyError, TypeError)) else 'unreachable'
            if attempt == 0:
                time.sleep(2)
    return dict(dataset=folder, state=failure_state, error=error)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--deep', action='store_true')
    parser.add_argument('--expected-root', type=Path)
    parser.add_argument('--attempts', type=int, default=1)
    parser.add_argument('--delay', type=int, default=20)
    args = parser.parse_args()
    for attempt in range(args.attempts):
        now = dt.datetime.now(UTC)
        datasets = [check(folder, now, args.deep, args.expected_root) for folder in ('timetable', 'mobility')]
        report = dict(checkedAtUtc=now.isoformat(), warningHours=WARNING_HOURS, healthy=all(d['state'] == 'healthy' for d in datasets), datasets=datasets)
        if report['healthy'] or attempt + 1 == args.attempts:
            break
        time.sleep(args.delay)
    with open('transport-health.json', 'w') as output:
        json.dump(report, output, ensure_ascii=False, indent=2)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['healthy'] else 1

if __name__ == '__main__':
    sys.exit(main())
