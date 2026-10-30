"""Publish only this reviewed app via an existing Git Credential Manager login.

No credentials are printed, written into repository files, or passed as shell arguments.
"""
from pathlib import Path
import json,os,subprocess,sys
import requests

ROOT=Path(__file__).resolve().parents[1]
STATE=ROOT/'PUBLISH_STATUS.local.json'
ENV=os.environ.copy();ENV['GIT_TERMINAL_PROMPT']='0';ENV['GCM_INTERACTIVE']='never'
def git(*args,check=True):
    r=subprocess.run(['git',*args],cwd=ROOT,env=ENV,text=True,capture_output=True,timeout=120)
    if check and r.returncode:raise RuntimeError(r.stderr[-2000:])
    return r.stdout.strip()
def credential():
    r=subprocess.run(['git','credential','fill'],cwd=ROOT,env=ENV,input='protocol=https\nhost=github.com\n\n',text=True,capture_output=True,timeout=15)
    data=dict(line.split('=',1) for line in r.stdout.splitlines() if '=' in line)
    if not data.get('password'):raise RuntimeError('GitHub sign-in is not available to Git Credential Manager yet. Complete the pending device authorization first.')
    return data['password']
def save(data):STATE.write_text(json.dumps(data,indent=2),encoding='utf-8')
def main():
    s=requests.Session();s.headers.update({'Authorization':'Bearer '+credential(),'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','User-Agent':'Landslide-Research-Atlas-Publisher'})
    def api(method,path,body=None,allow=()):
        r=s.request(method,'https://api.github.com'+path,json=body,timeout=40)
        if r.status_code>=400 and r.status_code not in allow:
            try:msg=r.json().get('message','Request failed')
            except ValueError:msg='Request failed'
            raise RuntimeError(f'GitHub {method} {path}: HTTP {r.status_code}: {msg}')
        return r
    u=api('GET','/user').json();login=u['login'];slug='landslide-atlas';repo=f'{login}/{slug}'
    state=json.loads(STATE.read_text()) if STATE.exists() else {}
    existing=api('GET','/repos/'+repo,allow=(404,))
    if existing.status_code==404:
        r=api('POST','/user/repos',{'name':slug,'description':'Source-linked India landslide research atlas: regional exploration, local contributions and reproducible figures.','private':False,'auto_init':False})
        info=r.json();state={'repository':repo,'repository_url':info['html_url'],'created_in_this_task':True};save(state)
    elif not(state.get('repository')==repo and state.get('created_in_this_task')):
        raise RuntimeError('A repository with the requested name already exists. It has not been modified; choose a destination explicitly.')
    print('Repository:',state['repository_url'],flush=True)
    if not(ROOT/'.git').exists():git('init','-b','main')
    git('config','user.name',u.get('name') or login)
    git('config','user.email',f"{u['id']}+{login}@users.noreply.github.com")
    url=f'https://github.com/{repo}.git'
    remote=git('remote','get-url','origin',check=False)
    if remote and remote!=url:raise RuntimeError('Existing origin differs from the selected repository; no push made.')
    if not remote:git('remote','add','origin',url)
    public=[]
    for path in ROOT.rglob('*'):
        if not path.is_file() or any(x in {'.git','.cache','node_modules','test-output','__pycache__'} for x in path.relative_to(ROOT).parts):continue
        if path==STATE or path.suffix in {'.log','.zip','.pyc'}:continue
        if path.suffix.lower() in {'.pdf','.tif','.joblib','.exe'}:raise RuntimeError('Unexpected publication file type: '+path.name)
        public.append(path.relative_to(ROOT).as_posix())
    git('add','--',*sorted(public))
    if git('diff','--cached','--name-only'):git('commit','-m','Add source-linked India landslide research atlas')
    sha=git('rev-parse','HEAD');state['commit']=sha;state['public_files']=len(public);save(state)
    git('push','-u','origin','HEAD:main');print('Pushed reviewed commit:',sha,flush=True)
    p=api('GET','/repos/'+repo+'/pages',allow=(404,))
    if p.status_code==404:api('POST','/repos/'+repo+'/pages',{'build_type':'workflow'})
    elif p.json().get('build_type')!='workflow':api('PUT','/repos/'+repo+'/pages',{'build_type':'workflow'})
    page=api('GET','/repos/'+repo+'/pages').json();state['pages_url']=page['html_url'];state['deployment_status']='configured; awaiting Actions result';save(state)
    api('POST','/repos/'+repo+'/actions/workflows/pages.yml/dispatches',{'ref':'main'})
    print('Pages configured:',state['pages_url'],flush=True)
    print('Actions:',state['repository_url']+'/actions',flush=True)

if __name__=='__main__':
    try:main()
    except Exception as e:print(str(e),file=sys.stderr);sys.exit(1)
