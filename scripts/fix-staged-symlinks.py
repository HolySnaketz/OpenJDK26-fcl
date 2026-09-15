from pathlib import Path
p=Path(__file__).resolve().parent/'package.py'
s=p.read_text()
s=s.replace("provenance={}\n",'''def resolve_staged(path):
    for unused in range(16):
        if not path.is_symlink(): return path
        target=path.readlink()
        original='/data/data/com.termux/files/usr/'
        if str(target).startswith(original): path=prefix/str(target)[len(original):]
        else: path=target if target.is_absolute() else path.parent/target
    raise RuntimeError('Symlink cycle: '+str(path))
provenance={}
''')
s=s.replace("source=prefix/'lib'/name","source=resolve_staged(prefix/'lib'/name)")
s=s.replace("    shutil.copy2(path,licenses/(path.parent.name+'-copyright'))","    resolved=resolve_staged(path)\n    if resolved.is_file(): shutil.copy2(resolved,licenses/(path.parent.name+'-copyright'))")
p.write_text(s)
scratch=Path('/home/arron/projects/openjdk26-fcl-build')
source=scratch/'package-aarch64'
target=scratch/'package-aarch64-first-attempt'
assert source.parent==scratch and target.parent==scratch and not target.exists()
source.rename(target)