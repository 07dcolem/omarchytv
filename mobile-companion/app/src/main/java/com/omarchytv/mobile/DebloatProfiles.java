package com.omarchytv.mobile;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;

/**
 * Brand-aware, 100% reversible Android TV / Google TV debloat profiles.
 *
 * Strict safety invariants:
 * 1. ONLY uses `pm disable-user --user 0 <pkg>` (NEVER `pm uninstall`).
 * 2. NEVER disables `com.google.android.tungsten.setupwraith` (breaks Wi-Fi on Android 14 / Google TV).
 * 3. NEVER disables `com.google.android.gms` (Play Services) or `com.google.android.apps.mediashell` (Chromecast).
 * 4. NEVER disables Live TV / HDMI input services (`com.sony.dtv.tvx`, `com.tcl.tv`, `com.android.tv`, etc.).
 * 5. Every disabled package can be re-enabled in 1 tap with `pm enable --user 0 <pkg>`.
 */
public final class DebloatProfiles {

    private DebloatProfiles() {}

    public static final class PackageEntry {
        public final String packageName;
        public final String label;
        public final boolean protectedSystem;

        public PackageEntry(String packageName, String label, boolean protectedSystem) {
            this.packageName = packageName;
            this.label = label;
            this.protectedSystem = protectedSystem;
        }
    }

    public static final class BrandProfile {
        public final String id;
        public final String displayName;
        public final String notes;
        public final List<PackageEntry> packages;

        public BrandProfile(String id, String displayName, String notes, List<PackageEntry> packages) {
            this.id = id;
            this.displayName = displayName;
            this.notes = notes;
            this.packages = Collections.unmodifiableList(packages);
        }
    }

    /** Hardcoded immutable set of system/network/cast/live-tv packages that must NEVER be disabled. */
    public static final Set<String> PROTECTED_PACKAGES;
    static {
        Set<String> s = new LinkedHashSet<>(Arrays.asList(
                "com.omarchytv.home",
                "com.omarchytv.launcher",
                "com.omarchytv.mobile",
                "com.google.android.tungsten.setupwraith", // Wi-Fi / setup on Google TV & Android 14
                "com.google.android.gms",                  // Google Play Services
                "com.google.android.gsf",                  // Google Services Framework
                "com.android.vending",                     // Google Play Store
                "com.google.android.apps.mediashell",      // Chromecast built-in
                "com.google.android.tv.remote.service",    // Android TV remote service
                "com.android.providers.settings",          // System settings provider
                "com.android.settings",                    // System settings
                "com.android.tv.settings",                 // Android TV settings
                "com.sony.dtv.tvx",                        // Sony Bravia Live TV / HDMI
                "com.sony.dtv.tvinput.external",           // Sony HDMI inputs
                "com.sony.dtv.tvinput.tuner",              // Sony DVB tuner
                "com.sony.dtv.braviasyncservice",          // Sony HDMI-CEC Bravia Sync
                "com.tcl.tv",                              // TCL Live TV & HDMI
                "com.tcl.tvinput",                         // TCL TV input
                "com.android.tv"                           // Reference Live TV
        ));
        PROTECTED_PACKAGES = Collections.unmodifiableSet(s);
    }

    public static boolean isProtected(String pkg) {
        if (pkg == null) return true;
        String clean = pkg.trim();
        return clean.isEmpty() || PROTECTED_PACKAGES.contains(clean);
    }

    private static final Map<String, BrandProfile> PROFILES = new LinkedHashMap<>();
    static {
        register("sony-bravia", "Sony Bravia (ATV2 / ATV3 / Google TV)",
                "Keeps Bravia Sync (CEC), Live TV (tvx), HDMI inputs, Chromecast & Play Services.",
                new PackageEntry("tv.samba.ssm", "Samba TV ACR Telemetry", false),
                new PackageEntry("com.sony.dtv.sonyselect", "Sony Select App Store Promos", false),
                new PackageEntry("com.sony.dtv.promos", "Sony Home Screen Promos", false),
                new PackageEntry("com.sony.dtv.discovery", "Sony Content Discovery", false),
                new PackageEntry("com.sony.dtv.bivlinfo", "Sony Bravia Internet Video Link", false),
                new PackageEntry("com.sony.dtv.tvlaunchercustomizer", "Sony Stock Launcher Customizer", false),
                new PackageEntry("com.google.android.tvrecommendations", "Android TV Sponsored Row", false),
                new PackageEntry("android.autoinstalls.config.sony.bravia", "Sony Forced Auto-Installs", false),
                new PackageEntry("com.sony.dtv.demomode", "Retail Store Demo Mode", false),
                new PackageEntry("com.sony.dtv.demosupport", "Retail Demo Support", false),
                new PackageEntry("com.sony.dtv.multiscreendemo", "Multi-Screen Retail Demo", false),
                new PackageEntry("com.sony.dtv.da.service", "Sony Data Analytics Agent", false),
                new PackageEntry("com.qterics.da.product", "Qterics Device Telemetry", false),
                new PackageEntry("com.sony.dtv.sonybugreportsys", "Sony Background Bug Reporter", false),
                new PackageEntry("com.google.android.tv.bugreportsender", "Google TV Bug Report Sender", false),
                new PackageEntry("com.google.android.feedback", "Google Feedback Agent", false),
                new PackageEntry("com.sony.dtv.customersupport", "Sony Customer Support Nag", false),
                new PackageEntry("com.sony.dtv.smarthelp", "Sony SmartHelp Overlay", false),
                new PackageEntry("com.sony.dtv.imanual", "Sony Built-in i-Manual", false),
                new PackageEntry("com.google.android.youtube.tvmusic", "YouTube Music TV Stub", false),
                new PackageEntry("com.google.android.videos", "Google Play Movies & TV Banner", false),
                new PackageEntry("com.google.android.play.games", "Google Play Games Stub", false),
                new PackageEntry("com.google.android.tungsten.setupwraith", "Wi-Fi / SetupWraith (NEVER TOUCH)", true),
                new PackageEntry("com.google.android.apps.mediashell", "Chromecast Built-in (NEVER TOUCH)", true),
                new PackageEntry("com.sony.dtv.tvx", "Sony Live TV & HDMI (NEVER TOUCH)", true)
        );

        register("google-tv", "Google TV Streamer / Chromecast",
                "Safe profile for Android 12-14 Google TV. Protects setupwraith (Wi-Fi) & Chromecast.",
                new PackageEntry("com.google.android.tvrecommendations", "Sponsored Recommendations Row", false),
                new PackageEntry("android.autoinstalls.config.google.gtvpai", "Google TV Partner Auto-Installs", false),
                new PackageEntry("com.google.android.feedback", "Google Telemetry Feedback", false),
                new PackageEntry("com.google.android.tv.bugreportsender", "Google TV Bug Report Sender", false),
                new PackageEntry("com.google.android.youtube.tvmusic", "YouTube Music Promo Tile", false),
                new PackageEntry("com.google.android.videos", "Google TV Shop / Videos Stub", false),
                new PackageEntry("com.google.android.play.games", "Google Play Games Stub", false),
                new PackageEntry("com.google.android.tungsten.setupwraith", "Wi-Fi / SetupWraith (NEVER TOUCH)", true),
                new PackageEntry("com.google.android.apps.mediashell", "Chromecast Built-in (NEVER TOUCH)", true),
                new PackageEntry("com.google.android.gms", "Google Play Services (NEVER TOUCH)", true)
        );

        register("sharp-aquos", "Sharp AQUOS Android / Google TV",
                "Safe debloat for Sharp AQUOS sets. Keeps AQUOS tuner, HDMI inputs, and Wi-Fi stack.",
                new PackageEntry("tv.samba.ssm", "Samba TV ACR Telemetry", false),
                new PackageEntry("com.google.android.tvrecommendations", "Android TV Ad Recommendations", false),
                new PackageEntry("com.google.android.feedback", "Google Feedback Telemetry", false),
                new PackageEntry("com.google.android.tv.bugreportsender", "Google Bug Report Sender", false),
                new PackageEntry("com.google.android.youtube.tvmusic", "YouTube Music Promo Tile", false),
                new PackageEntry("com.google.android.videos", "Google Play Movies & TV", false),
                new PackageEntry("com.google.android.play.games", "Google Play Games", false),
                new PackageEntry("com.google.android.tungsten.setupwraith", "Wi-Fi / SetupWraith (NEVER TOUCH)", true),
                new PackageEntry("com.google.android.apps.mediashell", "Chromecast Built-in (NEVER TOUCH)", true)
        );

        register("tcl-gtv", "TCL Google TV / Android TV (G10 / BeyondTV)",
                "Removes TCL ChannelPlus, TIAS & store demo while keeping com.tcl.tv (Live TV + HDMI).",
                new PackageEntry("com.tcl.tv.plus", "TCL TV+ Promo App", false),
                new PackageEntry("com.tcl.channelplus", "TCL Live FAST Ad Channels", false),
                new PackageEntry("com.tcl.tv.tclhome_passive", "TCL Boot Home Promo Pusher", false),
                new PackageEntry("com.tcl.partnercustomizer", "TCL Sponsored Home Rows", false),
                new PackageEntry("com.tcl.interactive", "TCL TIAS Background Telemetry", false),
                new PackageEntry("com.tcl.smartlink.core", "TCL Silent CustomInstallService", false),
                new PackageEntry("com.tcl.exhibit", "TCL Retail Exhibit Demo", false),
                new PackageEntry("com.tcl.esticker", "TCL Retail E-Sticker Overlay", false),
                new PackageEntry("com.tcl.ocean.instructions", "TCL Ocean E-Manual", false),
                new PackageEntry("com.tcl.repairguide", "TCL Repair Guide", false),
                new PackageEntry("android.autoinstalls.config.google.gtvpai", "Partner Auto-Installs", false),
                new PackageEntry("com.google.android.feedback", "Google Feedback Agent", false),
                new PackageEntry("com.tcl.tv", "TCL Live TV & HDMI (NEVER TOUCH)", true),
                new PackageEntry("com.google.android.tungsten.setupwraith", "Wi-Fi / SetupWraith (NEVER TOUCH)", true),
                new PackageEntry("com.google.android.apps.mediashell", "Chromecast Built-in (NEVER TOUCH)", true)
        );

        register("hisense-tv", "Hisense Android / Google TV",
                "Disables Samba ACR & Hisense store promos while preserving TV inputs & Chromecast.",
                new PackageEntry("tv.samba.ssm", "Samba TV ACR Telemetry", false),
                new PackageEntry("com.hisense.tv.partnercustomizer", "Hisense Home Row Promos", false),
                new PackageEntry("com.hisense.store.tv", "Hisense App Store Banner", false),
                new PackageEntry("com.google.android.tvrecommendations", "Sponsored Recommendations Row", false),
                new PackageEntry("com.google.android.feedback", "Google Feedback Telemetry", false),
                new PackageEntry("com.google.android.videos", "Google Play Movies & TV", false),
                new PackageEntry("com.google.android.play.games", "Google Play Games", false),
                new PackageEntry("com.google.android.tungsten.setupwraith", "Wi-Fi / SetupWraith (NEVER TOUCH)", true),
                new PackageEntry("com.google.android.apps.mediashell", "Chromecast Built-in (NEVER TOUCH)", true)
        );

        register("xiaomi-mitv", "Xiaomi Mi TV / PatchWall",
                "Disables PatchWall ad service & Mi store bloat while keeping HDMI/AV inputs & Cast.",
                new PackageEntry("com.mitv.tvhome", "Xiaomi PatchWall Home Bloat", false),
                new PackageEntry("com.xiaomi.mitv.advertise", "Xiaomi System Ad Service", false),
                new PackageEntry("com.xiaomi.mitv.shop", "Xiaomi TV Mall", false),
                new PackageEntry("com.xiaomi.statistic", "Xiaomi Telemetry Collector", false),
                new PackageEntry("com.mitv.gallery", "Mi TV Ad Screensaver Gallery", false),
                new PackageEntry("com.google.android.tvrecommendations", "Sponsored Recommendations Row", false),
                new PackageEntry("com.google.android.feedback", "Google Feedback Telemetry", false),
                new PackageEntry("com.google.android.videos", "Google Play Movies & TV", false),
                new PackageEntry("com.google.android.play.games", "Google Play Games", false),
                new PackageEntry("com.google.android.tungsten.setupwraith", "Wi-Fi / SetupWraith (NEVER TOUCH)", true),
                new PackageEntry("com.google.android.apps.mediashell", "Chromecast Built-in (NEVER TOUCH)", true)
        );
    }

    private static void register(String id, String name, String notes, PackageEntry... entries) {
        PROFILES.put(id, new BrandProfile(id, name, notes, Arrays.asList(entries)));
    }

    public static List<BrandProfile> allProfiles() {
        return new ArrayList<>(PROFILES.values());
    }

    public static BrandProfile getProfile(String id) {
        BrandProfile p = PROFILES.get(id);
        return p != null ? p : PROFILES.get("sony-bravia");
    }

    public static String matchBrandProfileId(String manufacturer, String model) {
        String s = ((manufacturer == null ? "" : manufacturer) + " " + (model == null ? "" : model))
                .toLowerCase(Locale.ROOT);
        if (s.contains("sony") || s.contains("bravia")) return "sony-bravia";
        if (s.contains("sharp") || s.contains("aquos")) return "sharp-aquos";
        if (s.contains("tcl") || s.contains("beyondtv")) return "tcl-gtv";
        if (s.contains("hisense")) return "hisense-tv";
        if (s.contains("xiaomi") || s.contains("mitv") || s.contains("mibox")) return "xiaomi-mitv";
        return "google-tv";
    }
}
