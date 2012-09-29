package org.hive13.wall;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.util.AttributeSet;
import android.view.View;

public class GridEditor extends View {

	public GridEditor(Context context) {
		super(context);
	}
	
	public GridEditor(Context context, AttributeSet attrs) {
		super(context, attrs);
	}

	public GridEditor(Context context, AttributeSet attrs, int defStyle) {
		super(context, attrs, defStyle);
	}

	private int width = -1;
	private int height = -1;
	
	Paint display[][] = null;
	

	@Override
	protected void onDraw(Canvas canvas) {
		super.onDraw(canvas);
		
		if (width < 0 || height < 0) {
			return;
		}
		
		float dx = canvas.getWidth() / (float) width;
		float dy = canvas.getHeight() / (float) height;
		
		for (int y = 0; y < height; ++y) {
			for (int x = 0; x < width; ++x) {
				canvas.drawRect(x * dx, y * dy, (x+1) * dx, (y+1) * dy, display[x][y]);
			}
		}
		
	}
	
	public void setGridSize(int width, int height) {
		this.width = width;
		this.height = height;
		display = new Paint[this.width][this.height];
		
		for (int y = 0; y < height; ++y) {
			for (int x = 0; x < width; ++x) {
				display[x][y] = new Paint();
				display[x][y].setARGB(255, 10*x, 10*y, 0);
			}
		}
		invalidate();
	}
}
