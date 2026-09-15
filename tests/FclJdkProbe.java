import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import javax.tools.ToolProvider;
import java.util.concurrent.TimeUnit;
public class FclJdkProbe {
  public static void main(String[] args) throws Exception {
    System.out.println("JAVA="+Runtime.version()+" ARCH="+System.getProperty("os.arch"));
    if(Runtime.version().feature()!=26) throw new AssertionError("JDK26 required");
    Path work=Files.createTempDirectory("fcl-jdk26-");
    System.out.println("TMP="+work);
    Path source=work.resolve("Hello.java");
    Files.writeString(source,"public class Hello { public static void main(String[] a) { System.out.println(\"CHILD_JAVA_PASS\"); } }",StandardCharsets.UTF_8);
    var compiler=ToolProvider.getSystemJavaCompiler();
    if(compiler==null || compiler.run(null,System.out,System.err,"-d",work.toString(),source.toString())!=0) throw new AssertionError("javac API failed");
    System.out.println("COMPILER_API_PASS");
    for(String gc:new String[]{"-XX:+UseSerialGC","-XX:+UseG1GC"}) {
      Path log=work.resolve(gc.contains("G1")?"g1.log":"serial.log");
      Process child=new ProcessBuilder(Path.of(System.getProperty("java.home"),"bin","java").toString(),gc,"-Xmx96m","-cp",work.toString(),"Hello").redirectErrorStream(true).redirectOutput(log.toFile()).start();
      if(!child.waitFor(30,TimeUnit.SECONDS)) {child.destroyForcibly();throw new AssertionError("Child timed out");}
      String output=Files.readString(log);System.out.println(output);
      if(child.exitValue()!=0 || !output.contains("CHILD_JAVA_PASS")) throw new AssertionError(gc+" child failed");
    }
    System.out.println("JDK_BASIC_PASS (not full game or GUI acceptance)");
  }
}