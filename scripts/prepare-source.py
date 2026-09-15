from pathlib import Path
import subprocess,shutil,difflib,json
root=Path(__file__).resolve().parent.parent
old=Path('/mnt/d/projects/arron/shuoshuo-07/openjdk26-android')
scratch=Path('/home/arron/projects/openjdk26-fcl-build')
source=scratch/'source/openjdk'
if source.exists(): raise SystemExit('Source already exists; refusing to reset')
(source.parent).mkdir(parents=True,exist_ok=True)
subprocess.run(['unzip','-q',str(old/'downloads/openjdk-26+35_src.zip'),'-d',str(source.parent)],check=True)
(root/'patches').mkdir(exist_ok=True)
for patch in sorted((old/'recipes/openjdk-26').glob('*.patch')):
    content=patch.read_text().replace('@TERMUX_PREFIX@','/usr')
    (root/'patches'/patch.name).write_text(content)
    result=subprocess.run(['patch','--batch','--fuzz=0','-p1'],input=content,cwd=source,text=True,capture_output=True)
    if result.returncode: raise SystemExit(result.stdout+result.stderr)
changes={}
def replace(path,before,after):
    p=source/path
    text=p.read_text()
    assert before in text,path+': missing match'
    changes.setdefault(path,text)
    p.write_text(text.replace(before,after))
replace('src/hotspot/os/linux/os_linux.cpp','  return "/usr/tmp";','  const char* tmp = ::getenv("TMPDIR");\n  return (tmp != nullptr && tmp[0] != 0) ? tmp : "/data/local/tmp";')
replace('src/hotspot/os/posix/perfMemory_posix.cpp','#define TMP_BUFFER_LEN (4+22)','#define TMP_BUFFER_LEN (MAXPATHLEN+32)')
replace('src/hotspot/os/posix/perfMemory_posix.cpp','  assert(strlen(tmpdir) == 4, "No longer using /tmp - update buffer size");','  assert(strlen(tmpdir) < MAXPATHLEN, "Temporary directory path is too long");')
replace('src/java.base/unix/native/libjava/java_props_md.c','    sprops.tmp_dir = P_tmpdir;','''    sprops.tmp_dir = P_tmpdir;
#ifdef __ANDROID__
    const char* android_tmp = getenv("TMPDIR");
    sprops.tmp_dir = (android_tmp != NULL && android_tmp[0] != 0)
        ? android_tmp : "/data/local/tmp";
#endif''')
replace('src/jdk.attach/linux/classes/sun/tools/attach/VirtualMachineImpl.java','Path.of("/usr/tmp")','Path.of(System.getenv().getOrDefault("TMPDIR", System.getProperty("java.io.tmpdir")))')
replace('src/java.base/linux/classes/sun/nio/fs/LinuxFileSystem.java','getMountEntries("/usr/etc/mtab")','getMountEntries("/proc/mounts")')
replace('src/java.base/unix/native/libjava/ProcessImpl_md.c','return ":/usr/bin";','return ":/system/bin";')
replace('src/java.base/unix/native/libjli/java_md.c','"/usr/bin/java"','"/system/bin/java"')
replace('src/java.desktop/unix/native/common/awt/fontpath.c','    char *useFC = getenv("USE_J2D_FONTCONFIG");','''#ifdef __ANDROID__
    // FCL supplies JAVA_HOME; keep font discovery independent of a Termux prefix.
    const char* java_home = getenv("JAVA_HOME");
    if (java_home != NULL && getenv("FONTCONFIG_FILE") == NULL) {
        char config_path[PATH_MAX];
        int n = snprintf(config_path, sizeof(config_path), "%s/conf/fonts/fonts.conf", java_home);
        if (n > 0 && n < sizeof(config_path)) setenv("FONTCONFIG_FILE", config_path, 0);
    }
#endif
    char *useFC = getenv("USE_J2D_FONTCONFIG");''')
patch=''.join(''.join(difflib.unified_diff(before.splitlines(True),(source/path).read_text().splitlines(True),fromfile='a/'+path,tofile='b/'+path)) for path,before in changes.items())
(root/'patches/0006-fcl-runtime-paths.patch').write_text(patch)
(root/'research/source.json').write_text(json.dumps({'fclCommit':'f06b5c539b42c58172e33204dbd8e4220bd49403','jdk':'26+35 RI','scratch':str(scratch),'forge':'26.2-65.1.0','gameVersionAssumption':'26.2'},indent=2)+'\n')
print('Prepared independent FCL source:',source)