from pathlib import Path
import subprocess,sys,shutil,json,hashlib,re,tarfile,struct
root=Path(__file__).resolve().parent.parent
scratch=Path('/home/arron/projects/openjdk26-fcl-build')
old=Path('/home/arron/projects/openjdk26-android-build')
arch=sys.argv[1]; assert arch in ('aarch64','arm')
build=scratch/f'build-{arch}'
image=build/'images/jdk'
current=Path('/data/TERMUX_ARCH').read_text().strip()
staging=Path('/data/data') if current==arch else old/f'staging/{arch}-data'
prefix=staging/'com.termux/files/usr'
package=scratch/f'package-{arch}'
if package.exists(): raise SystemExit('Package staging already exists; inspect before regenerating')
shutil.copytree(image,package,symlinks=False)
readelf=old/'toolchains/android-ndk-r29/toolchains/llvm/prebuilt/linux-x86_64/bin/llvm-readelf'
system={'libc.so','libm.so','libdl.so','liblog.so','libandroid.so','libz.so','libEGL.so','libGLESv2.so','libGLESv1_CM.so','libOpenSLES.so','libjnigraphics.so','libaaudio.so','libvulkan.so'}
def elf(p):
    return p.is_file() and p.open('rb').read(4)==b'\x7fELF'
def needed(p):
    return re.findall(r'\(NEEDED\).*?\[(.*?)\]',subprocess.check_output([str(readelf),'-d',str(p)],text=True))
def resolve_staged(path):
    for unused in range(16):
        if not path.is_symlink(): return path
        target=path.readlink()
        original='/data/data/com.termux/files/usr/'
        if str(target).startswith(original): path=prefix/str(target)[len(original):]
        else: path=target if target.is_absolute() else path.parent/target
    raise RuntimeError('Symlink cycle: '+str(path))
provenance={}
# These are also loaded by name instead of through DT_NEEDED.
queue=['libfontconfig.so','libfreetype.so','libcups.so']
files=[p for p in package.rglob('*') if elf(p)]
for p in files: queue.extend(needed(p))
while queue:
    name=queue.pop()
    if name in system or (package/'lib'/name).exists() or any(p.name==name for p in files): continue
    source=(scratch/f'deps-{arch}'/name) if (scratch/f'deps-{arch}'/name).is_file() else resolve_staged(prefix/'lib'/name)
    if not source.is_file(): raise SystemExit('Missing dependency '+name)
    target=package/'lib'/name
    shutil.copy2(source,target)
    provenance[name]={'source':str(source),'originalSha256':hashlib.sha256(source.read_bytes()).hexdigest()}
    files.append(target)
    queue.extend(needed(target))
# Materialized aliases avoid FCL's nonstandard relative-symlink rewriting.
for name,alias in [('libfontconfig.so','libfontconfig.so.1'),('libcups.so','libcups.so.2'),('libfreetype.so','libfreetype.so.6')]:
    if not (package/'lib'/alias).exists(): shutil.copy2(package/'lib'/name,package/'lib'/alias)
(package/'conf/fonts').mkdir(parents=True,exist_ok=True)
(package/'conf/fonts/fonts.conf').write_text('''<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd">
<fontconfig><dir>/system/fonts</dir><dir>/product/fonts</dir><cachedir prefix="xdg">fontconfig</cachedir></fontconfig>
''')
# Preserve third-party license notices supplied with the exact dependency sysroot.
licenses=package/'legal/fcl-bundled-dependencies'
licenses.mkdir(parents=True,exist_ok=True)
shutil.copy2(scratch/f'deps-{arch}/libandroid-spawn-LICENSE',licenses/'rebuilt-libandroid-spawn-LICENSE')
for path in (prefix/'share/doc').glob('*/copyright'):
    resolved=resolve_staged(path)
    if resolved.is_file(): shutil.copy2(resolved,licenses/(path.parent.name+'-copyright'))
records=[]
for path in package.rglob('*'):
    if not elf(path): continue
    rel=path.relative_to(package)
    origin='$ORIGIN'
    if rel.parts[0]=='bin': origin='$ORIGIN/../lib:$ORIGIN/../lib/server'
    elif rel.parent==Path('lib/server'): origin='$ORIGIN:$ORIGIN/..'
    elif rel.parts[0]=='lib': origin='$ORIGIN:$ORIGIN/server'
    subprocess.run(['patchelf','--page-size','16384' if arch=='aarch64' else '4096','--set-rpath',origin,str(path)],check=True)
    data=path.read_bytes()
    bits,machine=data[4],struct.unpack_from('<H',data,18)[0]
    assert (bits,machine)==((2,183) if arch=='aarch64' else (1,40)),str(rel)
    assert '/data/data/com.termux' not in subprocess.check_output([str(readelf),'-d',str(path)],text=True)
    deps=needed(path)
    for name in deps:
        assert name in system or any(p.name==name for p in (package/'lib').rglob('*')),str(rel)+': '+name
    phoff=struct.unpack_from('<Q' if bits==2 else '<I',data,32 if bits==2 else 28)[0]
    phsize,phnum=struct.unpack_from('<HH',data,54 if bits==2 else 42)
    aligns=[]
    for i in range(phnum):
        fields=struct.unpack_from('<IIQQQQQQ' if bits==2 else '<IIIIIIII',data,phoff+i*phsize)
        if fields[0]==1: aligns.append(fields[7])
    if arch=='aarch64': assert min(aligns)>=16384,str(rel)
    records.append({'path':str(rel),'needed':deps,'runpath':origin,'loadAlignments':aligns})
required=['release','bin/java','bin/javac','bin/jar','bin/jhsdb','lib/libawt_xawt.so','lib/libfontmanager.so','lib/libfreetype.so','lib/server/libjvm.so','jmods/java.desktop.jmod','include/jni.h','man/man1/java.1']
for p in required: assert (package/p).is_file(),p
assert 'JAVA_VERSION="26"' in (package/'release').read_text()
manifest={'architecture':arch,'fclVersion':'1.3.3.1','fclCommit':'f06b5c539b42c58172e33204dbd8e4220bd49403','minimumAndroidApi':28,'status':'candidate-not-device-validated','fclImportChanges':'FCL replaces lib/libawt_xawt.so with its APK bridge','knownIssues':['ARM32 upstream SA backend missing'] if arch=='arm' else [],'dependencyProvenance':provenance,'elfChecks':records}
(root/f'dist/openjdk26-fcl-{arch}.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
# FCL requires release directly at the archive root, not a wrapping directory.
archive=scratch/f'openjdk26-fcl-{arch}.tar.xz'
subprocess.run(['tar','--sort=name','--owner=0','--group=0','--numeric-owner','-I','xz -T4 -6','-cf',str(archive),'-C',str(package),'.'],check=True)
subprocess.run(['xz','-t',str(archive)],check=True)
with tarfile.open(archive,'r:xz') as tar:
    names={m.name.removeprefix('./') for m in tar}
    assert set(required)<=names
final=root/'dist'/archive.name
shutil.copy2(archive,final)
with final.open('rb') as f: digest=hashlib.file_digest(f,'sha256').hexdigest()
(root/'dist'/(archive.name+'.sha256')).write_text(digest+'  '+archive.name+'\n')
print(json.dumps({'file':str(final),'bytes':final.stat().st_size,'sha256':digest,'elfFiles':len(records),'bundledDependencies':len(provenance)}),flush=True)