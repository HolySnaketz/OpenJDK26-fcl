from pathlib import Path
import difflib
root=Path(__file__).resolve().parent.parent
source=Path('/home/arron/projects/openjdk26-fcl-build/source/openjdk')
rel='src/java.desktop/share/classes/sun/java2d/SurfaceManagerFactory.java'
text='''/*
 * Compatibility bridge for the Cacio version bundled with FCL 1.3.3.1.
 * Distributed under GPL version 2 with the Classpath exception, as in LICENSE.
 */
package sun.java2d;

import sun.awt.image.SunVolatileImage;
import sun.awt.image.VolatileSurfaceManager;

/** Legacy Cacio integration point; ordinary JDK26 graphics retain their factory. */
public abstract class SurfaceManagerFactory {
    private static volatile SurfaceManagerFactory instance;

    public static SurfaceManagerFactory getInstance() {
        SurfaceManagerFactory factory = instance;
        if (factory == null) throw new IllegalStateException("No SurfaceManagerFactory installed");
        return factory;
    }

    public static synchronized void setInstance(SurfaceManagerFactory factory) {
        if (factory == null) throw new IllegalArgumentException("factory must not be null");
        if (instance != null) throw new IllegalStateException("SurfaceManagerFactory already installed");
        instance = factory;
    }

    public static SurfaceManagerFactory getInstalledInstance() {
        return instance;
    }

    public abstract VolatileSurfaceManager createVolatileManager(SunVolatileImage image, Object context);
}
'''
(source/rel).write_text(text)
patch=''.join(difflib.unified_diff([],text.splitlines(True),fromfile='/dev/null',tofile='b/'+rel))
rel2='src/java.desktop/share/classes/sun/awt/image/SunVolatileImage.java'
p=source/rel2
before=p.read_text()
needle='''        // GraphicsConfig may provide some specific surface manager'''
after='''        sun.java2d.SurfaceManagerFactory legacyFactory =
                sun.java2d.SurfaceManagerFactory.getInstalledInstance();
        if ((caps == null || caps.isAccelerated()) && legacyFactory != null) {
            return legacyFactory.createVolatileManager(this, context);
        }
        // GraphicsConfig may provide some specific surface manager'''
assert needle in before
p.write_text(before.replace(needle,after,1))
patch+=''.join(difflib.unified_diff(before.splitlines(True),p.read_text().splitlines(True),fromfile='a/'+rel2,tofile='b/'+rel2))
(root/'patches/0008-cacio-surface-manager-compat.patch').write_text(patch)
print('Restored Cacio surface factory API and integrated volatile image creation')