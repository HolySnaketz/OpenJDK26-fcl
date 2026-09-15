/*
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
