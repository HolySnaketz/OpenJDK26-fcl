from pathlib import Path
import subprocess,shutil
root=Path(__file__).resolve().parent.parent
old=Path('/home/arron/projects/openjdk26-android-build')
scratch=Path('/home/arron/projects/openjdk26-fcl-build')
source=old/'termux-packages/packages/libandroid-spawn'
ndk=old/'toolchains/android-ndk-r29/toolchains/llvm/prebuilt/linux-x86_64'
for arch,triple in [('aarch64','aarch64-linux-android'),('arm','armv7a-linux-androideabi')]:
    output=scratch/f'deps-{arch}'
    output.mkdir(exist_ok=True)
    subprocess.run([str(ndk/'bin'/f'{triple}28-clang++'),'-shared','-fPIC','-O2','-Wl,-z,max-page-size=16384','-Wl,-soname,libandroid-spawn.so','-static-libstdc++','-I'+str(source),str(source/'posix_spawn.cpp'),'-o',str(output/'libandroid-spawn.so')],check=True)
    shutil.copy2(source/'LICENSE',output/'libandroid-spawn-LICENSE')
    print('Rebuilt libandroid-spawn for',arch)
# Keep its exact source alongside the FCL recipe.
shutil.copytree(source,root/'dependency-sources/libandroid-spawn',dirs_exist_ok=True)