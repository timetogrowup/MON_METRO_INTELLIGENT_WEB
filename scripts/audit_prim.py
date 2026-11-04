"""Report configuration presence only. Never read, print or persist the key value."""
import json, os, pathlib, datetime

def report(environ):
    configured=bool(environ.get('PRIM_API_KEY','').strip())
    return {'schemaVersion':1,'checkedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'expectedSecret':'PRIM_API_KEY','configured':configured,'liveCallPerformed':False,'status':'configured_not_qualified' if configured else 'blocked_missing_expected_secret','limitations':['Presence is not proof of API rights, coverage, quotas or working authentication.','No provider request and no secret value stored.','Hosting remains separately required.']}

if __name__=='__main__':
    data=report(os.environ);pathlib.Path('prim_access_status.json').write_text(json.dumps(data,indent=2)+'\n');print('PRIM_ACCESS_STATUS',json.dumps(data))

