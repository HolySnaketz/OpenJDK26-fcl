from pathlib import Path
import subprocess,tempfile,zipfile,json,hashlib
root=Path(__file__).resolve().parent.parent
scratch=Path('/home/arron/projects/openjdk26-fcl-build')
source=scratch/'source/openjdk'
patches=sorted((root/'patches').glob('*.patch'))
proof=Path(tempfile.mkdtemp(prefix='patch-proof-',dir=scratch))
paths={line[6:] for patch in patches for line in patch.read_text().splitlines() if line.startswith('+++ b/')}
with zipfile.ZipFile('/mnt/d/projects/arron/shuoshuo-07/openjdk26-android/downloads/openjdk-26+35_src.zip') as archive:
    names=set(archive.namelist())
    for name in paths:
        if 'openjdk/'+name not in names: continue
        path=proof/name;path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(archive.read('openjdk/'+name))
logs=[]
for patch in patches:
    result=subprocess.run(['patch','--batch','--fuzz=0','-p1','-i',str(patch)],cwd=proof,text=True,capture_output=True)
    logs.append(patch.name+'\n'+result.stdout+result.stderr)
    if result.returncode: raise SystemExit('\n'.join(logs))
for name in paths: assert (proof/name).read_bytes()==(source/name).read_bytes(),name
(root/'logs/patch-proof.log').write_text('\n'.join(logs))
(root/'research/patch-verification.json').write_text(json.dumps({'patches':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in patches},'filesCompared':len(paths),'zeroFuzz':True,'matchesCompiledSource':True},indent=2)+'\n')
print('Verified',len(patches),'patches;',len(paths),'files match compiled source')