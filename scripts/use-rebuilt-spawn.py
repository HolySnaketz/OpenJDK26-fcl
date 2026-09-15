from pathlib import Path
p=Path(__file__).resolve().parent/'package.py'
s=p.read_text().replace("source=resolve_staged(prefix/'lib'/name)","source=(scratch/f'deps-{arch}'/name) if (scratch/f'deps-{arch}'/name).is_file() else resolve_staged(prefix/'lib'/name)")
s=s.replace("licenses.mkdir(parents=True,exist_ok=True)","licenses.mkdir(parents=True,exist_ok=True)\nshutil.copy2(scratch/f'deps-{arch}/libandroid-spawn-LICENSE',licenses/'rebuilt-libandroid-spawn-LICENSE')")
p.write_text(s)
scratch=Path('/home/arron/projects/openjdk26-fcl-build')
source=scratch/'package-aarch64';target=scratch/'package-aarch64-alignment-attempt'
assert source.parent==scratch and target.parent==scratch and not target.exists()
source.rename(target)