from pathlib import Path
import struct
root=Path('/home/arron/projects/openjdk26-fcl-build/package-aarch64/lib')
for p in root.rglob('*.so*'):
    if not p.is_file(): continue
    d=p.read_bytes()
    if not d.startswith(b'\x7fELF') or d[4]!=2: continue
    off=struct.unpack_from('<Q',d,32)[0]; size,num=struct.unpack_from('<HH',d,54)
    aligns=[struct.unpack_from('<IIQQQQQQ',d,off+i*size)[7] for i in range(num) if struct.unpack_from('<I',d,off+i*size)[0]==1]
    if min(aligns)<16384: print(p.name,hex(min(aligns)))