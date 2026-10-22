package com.omarchytv.home;

import android.app.Activity;
import android.graphics.Color;
import android.graphics.drawable.ColorDrawable;
import android.view.Gravity;
import android.view.KeyEvent;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.LinearLayout;
import android.widget.PopupWindow;
import android.widget.TextView;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;

/**
 * A small Walker-style menu in a floating Hyprland window: a "> title" header and monospace rows with
 * an optional value on the right. Supports submenus (Back returns to the parent) and rows that update
 * their value in place. Used for the logo (settings) menu and the tile context menu.
 */
final class AsciiMenu {

    interface Action {
        /** Runs on OK. Return true to keep the menu open (e.g. after cycling a value). */
        boolean run(Row row);
    }

    static final class Row {
        final String label;
        String value;
        final Action action;
        /** Explanatory line: dimmed, not focusable, does nothing. */
        boolean hint;
        TextView valueView;

        Row(String label, String value, Action action) {
            this.label = label;
            this.value = value;
            this.action = action;
        }

        void setValue(String v) {
            value = v;
            if (valueView != null) TextFx.decrypt(valueView, v, 200);
        }
    }

    static final class Page {
        final String title;
        final List<Row> rows = new ArrayList<>();
        /** Runs when this page stops being visible (Back to the parent, or the menu closed). */
        Runnable onLeave;

        Page(String title) {
            this.title = title;
        }

        Page add(String label, String value, Action action) {
            rows.add(new Row(label, value, action));
            return this;
        }

        /** A non-actionable hint row (comment colour, skipped by the D-pad). */
        Page hint(String label) {
            Row r = new Row(label, null, null);
            r.hint = true;
            rows.add(r);
            return this;
        }
    }

    private final Activity activity;
    private final PopupWindow popup;
    private final LinearLayout rows;
    private final Deque<Page> stack = new ArrayDeque<>();
    private final float density;

    AsciiMenu(Activity activity, int widthDp) {
        this.activity = activity;
        density = activity.getResources().getDisplayMetrics().density;
        View panel = Theme.applied(LayoutInflater.from(activity).inflate(R.layout.popup_inputs, null, false));
        rows = panel.findViewById(R.id.rows);
        Theme.apply(panel);
        panel.setBackground(Theme.cur().menuCard(density));   // Omarchy shell [menu] card
        popup = new PopupWindow(panel, (int) (widthDp * density), ViewGroup.LayoutParams.WRAP_CONTENT, true);
        popup.setBackgroundDrawable(new ColorDrawable(Color.TRANSPARENT));   // needed for Back to dismiss
        popup.setOutsideTouchable(true);
        popup.setAnimationStyle(0);
        popup.setOnDismissListener(() -> {
            leave(stack.peek());
            if (dismissListener != null) dismissListener.onDismiss();
        });
    }

    private PopupWindow.OnDismissListener dismissListener;

    void setOnDismiss(PopupWindow.OnDismissListener l) {
        dismissListener = l;
    }

    private static void leave(Page p) {
        if (p != null && p.onLeave != null) {
            Runnable r = p.onLeave;
            p.onLeave = null;
            r.run();
        }
    }

    /** v2.10: below the anchor, or above it when it would run off the bottom (tile menus on the bottom app row). */
    private void showFitting(View anchor) {
        View content = popup.getContentView();
        content.measure(View.MeasureSpec.makeMeasureSpec(popup.getWidth(), View.MeasureSpec.EXACTLY),
                View.MeasureSpec.makeMeasureSpec(0, View.MeasureSpec.UNSPECIFIED));
        int ph = content.getMeasuredHeight(), gap = (int) (6 * density);
        int[] loc = new int[2];
        anchor.getLocationOnScreen(loc);
        int screenH = anchor.getRootView().getHeight();
        popup.setClippingEnabled(true);
        if (loc[1] + anchor.getHeight() + gap + ph > screenH && loc[1] - gap - ph >= 0) {
            popup.showAsDropDown(anchor, 0, -(anchor.getHeight() + gap + ph), Gravity.START);
        } else {
            popup.showAsDropDown(anchor, 0, gap, Gravity.START);
        }
    }

    void showBelow(View anchor, Page page) {
        if (anchor == null || anchor.getWindowToken() == null || !anchor.isAttachedToWindow()) return;   // v2.10: activity gone (emulator crash)
        stack.clear();
        render(page);
        showFitting(anchor);
        focusFirst();
    }

    /** Reopens a submenu (after a live-preview rebuild) with Back still leading to its parent. */
    void showBelow(View anchor, Page parent, Page page) {
        if (anchor == null || anchor.getWindowToken() == null || !anchor.isAttachedToWindow()) return;
        stack.clear();
        stack.push(parent);
        render(page);
        showFitting(anchor);
        focusFirst();
    }

    /** Focuses the row with this label (keeps the cursor on the setting being stepped). */
    void focusRow(String label) {
        for (int i = 1; i < rows.getChildCount(); i++) {
            TextView t = rows.getChildAt(i).findViewById(R.id.title);
            if (t != null && label.contentEquals(t.getText())) {
                rows.getChildAt(i).requestFocus();
                return;
            }
        }
    }

    /** Opens a submenu; Back returns here. */
    void push(Page page) {
        render(page);
        focusFirst();
    }

    void dismiss() {
        popup.dismiss();
    }

    boolean isShowing() {
        return popup.isShowing();
    }

    private void render(Page page) {
        stack.push(page);
        rows.removeAllViews();
        LayoutInflater inf = LayoutInflater.from(activity);
        TextView header = (TextView) Theme.applied(inf.inflate(R.layout.menu_header, rows, false));
        rows.addView(header);
        TextFx.type(header, "> " + page.title, 220);
        for (Row r : page.rows) {
            View v = Theme.applied(inf.inflate(R.layout.item_menu, rows, false));
            TextView t = v.findViewById(R.id.title);
            TextView val = v.findViewById(R.id.value);
            t.setText(r.label);
            val.setText(r.value == null ? "" : r.value);
            val.setVisibility(r.value == null ? View.GONE : View.VISIBLE);
            r.valueView = val;
            if (r.hint) {
                v.setFocusable(false);
                v.setClickable(false);
                t.setTextColor(Theme.m(0xFF7F88B3));   // text_dim: dimmed, still >= 4.5:1
                t.setSingleLine(false);   // v2.10: hints wrap instead of ending in "…" (HomeCheck)
                t.setMaxLines(4);
                t.setEllipsize(null);
                rows.addView(v);
                continue;
            }
            v.setOnClickListener(x -> {
                boolean keep = r.action != null && r.action.run(r);
                if (!keep && stack.peek() == page && popup.isShowing()) popup.dismiss();
            });
            v.setOnKeyListener((x, keyCode, e) -> {
                if (keyCode != KeyEvent.KEYCODE_BACK || stack.size() <= 1) return false;
                if (e.getAction() == KeyEvent.ACTION_UP) {
                    leave(stack.pop());
                    Page parent = stack.pop();
                    render(parent);
                    focusFirst();
                }
                return true;
            });
            rows.addView(v);
        }
        rows.measure(View.MeasureSpec.UNSPECIFIED, View.MeasureSpec.UNSPECIFIED);
        if (popup.isShowing()) popup.update(popup.getWidth(), ViewGroup.LayoutParams.WRAP_CONTENT);
    }

    private void focusFirst() {
        for (int i = 1; i < rows.getChildCount(); i++) {
            if (rows.getChildAt(i).isFocusable()) {
                rows.getChildAt(i).requestFocus();
                return;
            }
        }
    }
}
