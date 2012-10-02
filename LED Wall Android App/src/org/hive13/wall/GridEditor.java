package org.hive13.wall;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.util.AttributeSet;
import android.util.Log;
import android.view.MotionEvent;
import android.view.View;

public class GridEditor extends View 
implements View.OnTouchListener {
	final static String TAG = GridEditor.class.getSimpleName();

	public GridEditor(Context context) {
		super(context);
		this.setOnTouchListener(this);
	}
	
	public GridEditor(Context context, AttributeSet attrs) {
		super(context, attrs);
		this.setOnTouchListener(this);
	}

	public GridEditor(Context context, AttributeSet attrs, int defStyle) {
		super(context, attrs, defStyle);
		this.setOnTouchListener(this);
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

    public boolean onTouch(View v, MotionEvent event) {
        
        float point[] = new float[] { event.getX(), event.getY() };
     
        float dx = v.getWidth() / (float) width;
        float dy = v.getHeight() / (float) height;
        display[(int) (point[0] / dx)][(int) (point[1] / dy)].setARGB(255, 255, 255, 255);
        Log.i(TAG, "" + point[0] + ","  + point[1]);
        v.invalidate();
        
        return true;
    }
    
	
	public void setGridSize(int width, int height) {
		this.width = width;
		this.height = height;
		display = new Paint[this.width][this.height];
		
		for (int y = 0; y < height; ++y) {
			for (int x = 0; x < width; ++x) {
				display[x][y] = new Paint();
				//display[x][y].setARGB(255, 10*x, 10*y, 0);
			}
		}
		invalidate();
	}

	public void setPixel(int x, int y, int r, int g, int b) {
		display[x][y].setARGB(255, r, g, b);
	}
	
	public void clearGrid() {
		for (int y = 0; y < height; ++y) {
			for (int x = 0; x < width; ++x) {
				display[x][y].setARGB(255, 0, 0, 0);
			}
		}
		invalidate();
	}
	
	public int getGridWidth() {
		return width;
	}
	
	public int getGridHeight() {
		return height;
	}
	
}
