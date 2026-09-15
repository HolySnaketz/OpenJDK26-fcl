from pathlib import Path
import difflib
root=Path(__file__).resolve().parent.parent
source=Path('/home/arron/projects/openjdk26-fcl-build/source/openjdk')
rel='src/java.base/unix/native/libjli/java_md.c'
p=source/rel
before=p.read_text()
text=before.replace('#if defined(__linux__)\n    {','#if defined(__linux__) && !defined(__ANDROID__)\n    {',1)
helper='''#ifdef __ANDROID__
/* FCL imports regular tar entries without executable bits. Restore only our
 * own regular launcher files when invoked inside FCL's process. */
static void RestoreFclExecutePermissions(void) {
    const char* home = getenv("JAVA_HOME");
    if (home == NULL || getenv("FCL_NATIVEDIR") == NULL) return;
    char directory[PATH_MAX];
    int n = snprintf(directory, sizeof(directory), "%s/bin", home);
    if (n <= 0 || n >= sizeof(directory)) return;
    DIR* dir = opendir(directory);
    if (dir != NULL) {
        struct dirent* entry;
        while ((entry = readdir(dir)) != NULL) {
            char path[PATH_MAX];
            n = snprintf(path, sizeof(path), "%s/%s", directory, entry->d_name);
            struct stat st;
            if (n > 0 && n < sizeof(path) && lstat(path, &st) == 0 &&
                S_ISREG(st.st_mode) && st.st_uid == geteuid()) {
                chmod(path, st.st_mode | S_IXUSR);
            }
        }
        closedir(dir);
    }
    char helper[PATH_MAX];
    n = snprintf(helper, sizeof(helper), "%s/lib/jspawnhelper", home);
    struct stat st;
    if (n > 0 && n < sizeof(helper) && lstat(helper, &st) == 0 &&
        S_ISREG(st.st_mode) && st.st_uid == geteuid()) {
        chmod(helper, st.st_mode | S_IXUSR);
    }
}
#endif

'''
text=text.replace('const char*\nSetExecname(char **argv)',helper+'const char*\nSetExecname(char **argv)',1)
text=text.replace('    char* exec_path = NULL;','''#ifdef __ANDROID__
    RestoreFclExecutePermissions();
#endif
    char* exec_path = NULL;''',1)
assert text!=before
p.write_text(text)
(root/'patches/0007-fcl-embedded-launcher.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True),text.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel)))
print('FCL embedded launch path and executable restoration patched')