from pathlib import Path
import subprocess
root=Path(__file__).resolve().parent.parent
scratch=Path('/home/arron/projects/openjdk26-fcl-build')
jdk=scratch/'host-jdk26'
classes=scratch/'probe-classes';classes.mkdir(exist_ok=True)
output=root/'dist/acceptance-tests';output.mkdir(exist_ok=True)
for name in ['FclJdkProbe','CacioProbe']:
    subprocess.run([str(jdk/'bin/javac'),'-d',str(classes),str(root/f'tests/{name}.java')],check=True)
    subprocess.run([str(jdk/'bin/jar'),'--create','--file',str(output/(name+'.jar')),'--main-class',name,'-C',str(classes),name+'.class'],check=True)
    print('Built acceptance jar',name)
with (root/'logs/jdk-probe-host26.log').open('w') as log:
    subprocess.run([str(jdk/'bin/java'),'-jar',str(output/'FclJdkProbe.jar')],stdout=log,stderr=subprocess.STDOUT,check=True)
print('Host JDK probe passed; Android remains untested')