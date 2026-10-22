package com.omarchytv.home;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;

import org.json.JSONObject;
import org.junit.Test;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Iterator;

public class ThemeTest {

    @Test
    public void parsesHyprlandColours() {
        assertEquals(0xFF7AA2F7, Theme.parse("#7aa2f7", 0));
        assertEquals(0xFF1E1E1E, Theme.parse("rgb(1e1e1e)", 0));
        assertEquals(0xAA595959, Theme.parse("rgba(595959aa)", 0));
        int[] g = Theme.gradient("rgba(26a269ee) rgba(2ec27eee) 45deg", 0);
        assertEquals(0xEE26A269, g[0]);
        assertEquals(0xEE2EC27E, g[1]);
        int[] one = Theme.gradient("rgba(8a8588ee) 45deg", 0);
        assertEquals(one[0], one[1]);
    }

    @Test
    public void tokyoNightFallbackMapsToItself() {
        Theme t = Theme.cur();
        assertEquals(0xFF7AA2F7, t.map(0xFF7AA2F7));
        assertEquals(0x80A9B1D6, t.map(0x80A9B1D6));   // alpha kept
        assertEquals(0xAA595959, t.inactiveBorder);    // default/hypr/looknfeel.lua
        assertEquals(0xFF123456, t.map(0xFF123456));   // unknown colours untouched
    }

    @Test
    public void bundledPalettesCoverEveryStockThemeAndStayReadable() throws Exception {
        String json = new String(Files.readAllBytes(Paths.get("src/main/assets/omarchy_themes.json")), StandardCharsets.UTF_8);
        JSONObject themes = new JSONObject(json).getJSONObject("themes");
        assertTrue(themes.length() >= 20);
        for (Iterator<String> it = themes.keys(); it.hasNext(); ) {
            String name = it.next();
            JSONObject c = themes.getJSONObject(name);
            for (String k : new String[]{"accent", "background", "foreground", "dark_foreground", "selection", "muted"}) {
                assertNotNull(name + " " + k, c.optString(k, null));
            }
            int bg = Theme.parse(c.getString("background"), 0), fg = Theme.parse(c.getString("foreground"), 0);
            int dim = Theme.readable(Theme.parse(c.getString("dark_foreground"), 0), fg, bg);
            double cr = Surfaces.contrast(Surfaces.luminance(dim & 0xFFFFFF), Surfaces.luminance(bg & 0xFFFFFF));
            assertTrue(name + " dim text " + cr, cr >= 4.5 || dim == fg);
        }
    }
}
