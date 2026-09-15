from pathlib import Path
import os,subprocess,shlex,sys,fcntl
root=Path(__file__).resolve().parent.parent
arch=sys.argv[1]
assert arch in ('arm','aarch64')
old=Path('/home/arron/projects/openjdk26-android-build')
scratch=Path('/home/arron/projects/openjdk26-fcl-build')
lock=open('/tmp/.jdk26-staging.lock','w')
fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
assert Path('/data/TERMUX_ARCH').read_text().strip()==arch,'Switch staging ABI first'
spec=(old/f'build-{arch}/openjdk-26/src/build/linux-{arch}-server-release/spec.gmk').read_text()
line=next(line for line in spec.splitlines() if line.startswith('CONFIGURE_COMMAND_LINE := '))
args=shlex.split(line.split(' := ',1)[1])
args=[a for a in args if not a.startswith(('--with-extra-ldflags=','--with-vendor-name=','--with-version-opt='))]
args+=['--with-extra-ldflags=-L/data/data/com.termux/files/usr/lib -Wl,--enable-new-dtags -Wl,--as-needed -landroid-shmem -landroid-spawn','--with-vendor-name=Local FCL OpenJDK Port','--with-version-opt=fcl','--with-version-build=35']
ndk=old/f'build-{arch}/_cache/android-r29-api-28-v5/bin'
env=os.environ.copy()
env['PATH']=str(ndk)+':'+str(old/'toolchains/bootjdk25/bin')+':'+env['PATH']
triple='aarch64-linux-android' if arch=='aarch64' else 'arm-linux-androideabi'
env['CC']=str(ndk/(triple+'-clang'))
env['CXX']=str(ndk/(triple+'-clang++'))
build=scratch/f'build-{arch}'
build.mkdir(exist_ok=True)
if '--resume' not in sys.argv:
    with (root/f'logs/configure-{arch}.log').open('w') as log:
        subprocess.run(['bash',str(scratch/'source/openjdk/configure'),*args],cwd=build,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
print('Configured '+arch,flush=True)
with (root/f'logs/build-{arch}.log').open('a') as log:
    subprocess.run(['make','images','JOBS=8'],cwd=build,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
print('make images completed: '+arch,flush=True)