from pathlib import Path
import shutil,subprocess,tempfile,hashlib,json
root=Path(__file__).resolve().parent.parent
scratch=Path('/home/arron/projects/openjdk26-fcl-build')
work=Path(tempfile.mkdtemp(prefix='source-bundle-',dir=scratch))
name='openjdk26-fcl-source';bundle=work/name;bundle.mkdir()
shutil.copytree(scratch/'source/openjdk',bundle/'openjdk',symlinks=True)
for directory in ['patches','scripts','tests','research','dependency-sources']:
    shutil.copytree(root/directory,bundle/directory,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
for file in ['README.md','BUILD.zh-CN.md','INSTALL.zh-CN.md']:
    shutil.copy2(root/file,bundle/file)
archive=work/(name+'.tar.xz')
print('Compressing FCL patched source...',flush=True)
subprocess.run(['tar','--sort=name','--owner=0','--group=0','--numeric-owner','-I','xz -T4 -6','-cf',str(archive),'-C',str(work),name],check=True)
subprocess.run(['xz','-t',str(archive)],check=True)
final=root/'dist'/archive.name
shutil.copy2(archive,final)
with final.open('rb') as f: digest=hashlib.file_digest(f,'sha256').hexdigest()
(final.parent/(final.name+'.sha256')).write_text(digest+'  '+final.name+'\n')
print(json.dumps({'file':str(final),'bytes':final.stat().st_size,'sha256':digest}),flush=True)