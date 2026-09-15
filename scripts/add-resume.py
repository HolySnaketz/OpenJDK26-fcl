from pathlib import Path
p=Path(__file__).resolve().parent/'build.py'
s=p.read_text()
a=s.index("with (root/f'logs/configure-")
b=s.index("print('Configured",a)
s=s[:a]+"if '--resume' not in sys.argv:\n"+''.join('    '+line+'\n' for line in s[a:b].splitlines())+s[b:]
s=s.replace("with (root/f'logs/build-{arch}.log').open('w') as log:","with (root/f'logs/build-{arch}.log').open('a') as log:")
p.write_text(s)