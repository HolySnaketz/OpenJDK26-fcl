import java.awt.*;
import java.awt.image.BufferedImage;
import javax.imageio.ImageIO;
import javax.swing.*;
import java.io.File;
public class CacioProbe {
  public static void main(String[] args) throws Exception {
    Thread.setDefaultUncaughtExceptionHandler((thread,error) -> { error.printStackTrace(); System.exit(1); });
    System.out.println("JAVA="+Runtime.version());
    System.out.println("TOOLKIT="+Toolkit.getDefaultToolkit().getClass().getName());
    System.out.println("GRAPHICS="+GraphicsEnvironment.getLocalGraphicsEnvironment().getClass().getName());
    SwingUtilities.invokeAndWait(() -> {
      JFrame frame=new JFrame("JDK26 FCL bridge probe");
      JPanel panel=new JPanel();
      JButton button=new JButton("Swing");
      final int[] clicks={0};
      button.addActionListener(e -> clicks[0]++);
      panel.add(button);
      panel.add(new Button("AWT"));
      panel.add(new JTextField("Java26",12));
      frame.add(panel); frame.pack(); frame.setVisible(true);
      java.awt.image.VolatileImage volatileImage=frame.createVolatileImage(32,32);
      if(volatileImage==null) throw new AssertionError("No volatile image");
      volatileImage.validate(frame.getGraphicsConfiguration());
      Graphics2D vg=volatileImage.createGraphics();
      vg.setColor(Color.GREEN);vg.fillRect(0,0,32,32);vg.dispose();
      if(volatileImage.getSnapshot().getRGB(8,8)!=Color.GREEN.getRGB()) throw new AssertionError("Volatile image drawing failed");
      volatileImage.flush();
      if (Boolean.getBoolean("fcl.probe.clipboard")) try {
        var clipboard=Toolkit.getDefaultToolkit().getSystemClipboard();
        clipboard.setContents(new java.awt.datatransfer.StringSelection("jdk26-fcl"),null);
        if(!"jdk26-fcl".equals(clipboard.getData(java.awt.datatransfer.DataFlavor.stringFlavor))) throw new AssertionError("Clipboard failed");
      } catch(Exception e) { throw new RuntimeException(e); }
      button.doClick();
      if(clicks[0]!=1) throw new AssertionError("Swing action failed");
      BufferedImage image=new BufferedImage(frame.getWidth(),frame.getHeight(),BufferedImage.TYPE_INT_ARGB);
      Graphics2D graphics=image.createGraphics();frame.paint(graphics);graphics.dispose();
      try { ImageIO.write(image,"png",new File("cacio-probe.png")); } catch(Exception e) { throw new RuntimeException(e); }
      frame.dispose();
      System.out.println("AWT_SWING_OFFSCREEN_PASS");
    });
    System.exit(0);
  }
}