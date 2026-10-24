package com.omarchytv.mobile;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/**
 * Loads all 23 official Omarchy themes from bundled `omarchy_themes.json` (plus MIT community themes)
 * and merges any live themes fetched from the dual GitLab/GitHub mirrors.
 */
public final class ThemeCatalog {

    private ThemeCatalog() {}

    public static final class ThemeEntry {
        public final String id;
        public final String displayName;
        public final String mode;
        public final String bgHex;
        public final String fgHex;
        public final String accentHex;
        public final String accent2Hex;
        public final String greenHex;
        public final String redHex;
        public final String yellowHex;
        public final JSONObject rawColors;

        public ThemeEntry(String id, String displayName, String mode, String bgHex, String fgHex,
                          String accentHex, String accent2Hex, String greenHex, String redHex,
                          String yellowHex, JSONObject rawColors) {
            this.id = id;
            this.displayName = displayName;
            this.mode = mode;
            this.bgHex = bgHex;
            this.fgHex = fgHex;
            this.accentHex = accentHex;
            this.accent2Hex = accent2Hex;
            this.greenHex = greenHex;
            this.redHex = redHex;
            this.yellowHex = yellowHex;
            this.rawColors = rawColors;
        }

        public int bgColor() { return parseHexColor(bgHex, 0xFF1A1B26); }
        public int fgColor() { return parseHexColor(fgHex, 0xFFA9B1D6); }
        public int accentColor() { return parseHexColor(accentHex, 0xFF7AA2F7); }
        public int accent2Color() { return parseHexColor(accent2Hex, 0xFFBB9AF7); }
        public int greenColor() { return parseHexColor(greenHex, 0xFF9ECE6A); }
        public int redColor() { return parseHexColor(redHex, 0xFFF7768E); }
        public int yellowColor() { return parseHexColor(yellowHex, 0xFFE0AF68); }
    }

    public static List<ThemeEntry> parseThemesJson(String jsonText) {
        Map<String, ThemeEntry> map = new LinkedHashMap<>();
        try {
            JSONObject root = new JSONObject(jsonText);
            JSONObject themesObj = root.optJSONObject("themes");
            if (themesObj == null) themesObj = root;

            List<String> keys = new ArrayList<>();
            for (Iterator<String> it = themesObj.keys(); it.hasNext(); ) {
                keys.add(it.next());
            }
            Collections.sort(keys);
            // Put tokyo-night first as the flagship default
            if (keys.remove("tokyo-night")) {
                keys.add(0, "tokyo-night");
            }

            for (String key : keys) {
                JSONObject c = themesObj.optJSONObject(key);
                if (c == null) continue;
                String mode = c.optString("mode", "dark");
                String bg = c.optString("background", "#1a1b26");
                String fg = c.optString("foreground", "#a9b1d6");
                String accent = c.optString("accent", c.optString("blue", "#7aa2f7"));
                String accent2 = c.optString("bright_magenta", c.optString("magenta", "#bb9af7"));
                String green = c.optString("green", "#9ece6a");
                String red = c.optString("red", "#f7768e");
                String yellow = c.optString("yellow", "#e0af68");
                map.put(key, new ThemeEntry(key, formatDisplayName(key), mode, bg, fg,
                        accent, accent2, green, red, yellow, c));
            }
        } catch (JSONException ignored) {
        }
        return new ArrayList<>(map.values());
    }

    public static List<ThemeEntry> loadFromStream(InputStream in) throws IOException {
        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        byte[] buf = new byte[4096];
        int n;
        while ((n = in.read(buf)) > 0) {
            bos.write(buf, 0, n);
        }
        return parseThemesJson(new String(bos.toByteArray(), StandardCharsets.UTF_8));
    }

    public static String formatDisplayName(String id) {
        if (id == null || id.isEmpty()) return "Tokyo Night";
        String[] parts = id.split("-");
        StringBuilder sb = new StringBuilder();
        for (String p : parts) {
            if (p.isEmpty()) continue;
            if (sb.length() > 0) sb.append(' ');
            sb.append(Character.toUpperCase(p.charAt(0))).append(p.substring(1));
        }
        return sb.toString();
    }

    public static int parseHexColor(String hex, int fallback) {
        if (hex == null) return fallback;
        String clean = hex.trim().toLowerCase(Locale.ROOT);
        if (clean.startsWith("#") && clean.length() == 7) {
            try {
                return 0xFF000000 | Integer.parseInt(clean.substring(1), 16);
            } catch (NumberFormatException ignored) {
            }
        }
        return fallback;
    }
}
