package com.omarchytv.mobile;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.RectF;
import android.graphics.Typeface;
import android.widget.LinearLayout;

/**
 * Custom Omarchy TUI / Hyprland double-line bordered container (`╔══╡ TITLE ╞══╗`)
 * with non-overlapping title cutout and Tokyo Night / dynamic theme colors.
 */
public final class TuiBoxView extends LinearLayout {

    private final Paint borderPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint fillPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint titleBgPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint titleTextPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final RectF outerRect = new RectF();
    private final RectF innerRect = new RectF();

    private String titleText = "";
    private int bgColor = 0xFF16161E;
    private int borderColor = 0xFF7AA2F7;
    private int titleColor = 0xFFBB9AF7;

    public TuiBoxView(Context context, String title, Typeface monoBold) {
        super(context);
        setOrientation(VERTICAL);
        setWillNotDraw(false);
        this.titleText = title != null ? "╡ " + title + " ╞" : "";

        float dp = context.getResources().getDisplayMetrics().density;
        int padH = Math.round(14 * dp);
        int padTop = Math.round(22 * dp);
        int padBot = Math.round(12 * dp);
        setPadding(padH, padTop, padH, padBot);

        borderPaint.setStyle(Paint.Style.STROKE);
        borderPaint.setStrokeWidth(1.6f * dp);

        fillPaint.setStyle(Paint.Style.FILL);
        titleBgPaint.setStyle(Paint.Style.FILL);

        titleTextPaint.setTypeface(monoBold != null ? monoBold : Typeface.MONOSPACE);
        titleTextPaint.setTextSize(11.5f * dp);
        applyColors(bgColor, borderColor, titleColor);
    }

    public void setTitleText(String title) {
        this.titleText = title != null ? "╡ " + title + " ╞" : "";
        invalidate();
    }

    public void applyColors(int bg, int border, int title) {
        this.bgColor = bg;
        this.borderColor = border;
        this.titleColor = title;
        fillPaint.setColor(bg);
        titleBgPaint.setColor(bg);
        borderPaint.setColor(border);
        titleTextPaint.setColor(title);
        invalidate();
    }

    @Override
    protected void onDraw(Canvas canvas) {
        float dp = getResources().getDisplayMetrics().density;
        float inset = 4f * dp;
        float gap = 3f * dp;

        outerRect.set(inset, inset + 4f * dp, getWidth() - inset, getHeight() - inset);
        innerRect.set(outerRect.left + gap, outerRect.top + gap, outerRect.right - gap, outerRect.bottom - gap);

        canvas.drawRoundRect(outerRect, 3f * dp, 3f * dp, fillPaint);
        canvas.drawRoundRect(outerRect, 3f * dp, 3f * dp, borderPaint);
        borderPaint.setAlpha(150);
        canvas.drawRoundRect(innerRect, 2f * dp, 2f * dp, borderPaint);
        borderPaint.setAlpha(255);

        if (titleText != null && !titleText.isEmpty()) {
            float textW = titleTextPaint.measureText(titleText);
            float left = outerRect.left + 14f * dp;
            float top = outerRect.top - 7f * dp;
            float right = left + textW + 10f * dp;
            float bottom = outerRect.top + 9f * dp;
            canvas.drawRect(left, top, right, bottom, titleBgPaint);
            canvas.drawText(titleText, left + 5f * dp, outerRect.top + 4.5f * dp, titleTextPaint);
        }
        super.onDraw(canvas);
    }
}
