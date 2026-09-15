from pathlib import Path
import subprocess,re,os
root=Path(__file__).resolve().parent.parent
scratch=Path('/home/arron/projects/openjdk26-fcl-build')
work=scratch/'cacio-probe';work.mkdir(exist_ok=True)
jdk=scratch/'host-jdk26'
subprocess.run([str(jdk/'bin/javac'),'-d',str(work),str(root/'tests/CacioProbe.java')],check=True)
compat=work/'compat';compat.mkdir(exist_ok=True)
source=scratch/'source/openjdk/src/java.desktop/share/classes'
subprocess.run([str(jdk/'bin/javac'),'--patch-module','java.desktop='+str(source),'-d',str(compat),str(source/'sun/java2d/SurfaceManagerFactory.java'),str(source/'sun/awt/image/SunVolatileImage.java')],check=True)
options=re.findall(r'res.add\("(--add-(?:exports|opens)=[^"]+)"\)',(root/'research/CacioJavaArgs.java').read_text())
classpath=':'.join(str(p) for p in (root/'research/cacio').glob('*.jar'))
args=[str(jdk/'bin/java'),'--patch-module','java.desktop='+str(compat),*options,'-Djava.awt.headless=false','-Dcacio.managed.screensize=800x600','-Dcacio.font.fontmanager=sun.awt.X11FontManager','-Dcacio.font.fontscaler=sun.font.FreetypeFontScaler','-Xbootclasspath/a:'+classpath,'-javaagent:'+str(root/'research/cacio/cacio-agent.jar'),'-cp',str(work),'CacioProbe']
with (root/'logs/cacio-host26.log').open('w') as log:
    env=os.environ.copy();env['LD_LIBRARY_PATH']=env.get('LD_LIBRARY_PATH','')
    result=subprocess.run(args,cwd=work,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=45)
print('Host Cacio probe exit',result.returncode)
print((root/'logs/cacio-host26.log').read_text()[-6500:])