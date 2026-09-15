from pathlib import Path
p=Path(__file__).resolve().parent/'probe-cacio.py'
s=p.read_text().replace('import subprocess,re','import subprocess,re,os')
s=s.replace("options=re.findall", """compat=work/'compat';compat.mkdir(exist_ok=True)
source=scratch/'source/openjdk/src/java.desktop/share/classes'
subprocess.run([str(jdk/'bin/javac'),'--patch-module','java.desktop='+str(source),'-d',str(compat),str(source/'sun/java2d/SurfaceManagerFactory.java'),str(source/'sun/awt/image/SunVolatileImage.java')],check=True)
options=re.findall""")
s=s.replace("args=[str(jdk/'bin/java'),*options", "args=[str(jdk/'bin/java'),'--patch-module','java.desktop='+str(compat),*options")
s=s.replace("result=subprocess.run(args,cwd=work,stdout=log,stderr=subprocess.STDOUT,timeout=45)","env=os.environ.copy();env['LD_LIBRARY_PATH']=env.get('LD_LIBRARY_PATH','')\n    result=subprocess.run(args,cwd=work,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=45)")
p.write_text(s)