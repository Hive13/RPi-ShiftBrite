package org.hive13.wall;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLConnection;
import java.util.HashMap;
import java.util.Map;

import android.os.AsyncTask;
import android.util.Log;

    
public class WallCommunication {
	final static String TAG = WallCommunication.class.getSimpleName();
	
	// This is the WallActivity that owns us, as we need to make calls back to
	// it for certain async operations.
	WallActivity parent = null;
	
	// This is the grid we receive back from WallActivity, as we must set its
	// pixels directly.
	GridEditor grid = null;
	
	public enum HttpOperation { GET_SPECS, GET_FRAMEBUFFER, UPDATE_PIXEL, CLEAR_DISPLAY, ERROR };
	
	// baseUrl: URL up to the point commands should be added,
	// e.g. http://192.168.0.100:8080/display
	URL baseUrl = null;
	
	// This stores a mapping between different HTTP operations, and what URL
	// suffix is used to access it.
	Map<HttpOperation, String> opSuffix = null;
	
	public WallCommunication(WallActivity parent, URL baseUrl) {
		this.baseUrl = baseUrl;
		this.parent = parent;
		
		if (opSuffix == null) {
			opSuffix = new HashMap<HttpOperation, String>();
			opSuffix.put(HttpOperation.GET_SPECS, "specs/");
			opSuffix.put(HttpOperation.GET_FRAMEBUFFER, "");
			opSuffix.put(HttpOperation.CLEAR_DISPLAY, "clear/");
			opSuffix.put(HttpOperation.UPDATE_PIXEL, "update/");
		}
	}
	
	public void startAsyncOp(HttpOperation op) throws MalformedURLException {
		startAsyncOp(op, "");
	}
	
	public void startAsyncOp(HttpOperation op, String parameterString) throws MalformedURLException {
		// FIXME: '0' needs to not be hard-coded!
		URL dest = new URL(baseUrl, opSuffix.get(op) + "0" + parameterString);
		Log.i(TAG, "Using the URL: " + dest.toString());
		new HttpTask(op).execute(dest);
	}

	private class HttpTask extends AsyncTask<URL, Integer, String> {
		
		HttpOperation op = null;
		
		public HttpTask(HttpOperation op) {
			this.op = op;
		}
				
		@Override
		protected String doInBackground(URL... urls) {
			URLConnection conn;
			String result = null;
			try {
				conn = urls[0].openConnection();
				InputStream is = conn.getInputStream();
				InputStreamReader isr = new InputStreamReader(is);
				BufferedReader rd = new BufferedReader(isr);
				result = rd.readLine();
			} catch (IOException e) {
				op = HttpOperation.ERROR;
				result = e.getMessage();
			}
			return result;
		}
		
		@Override
		protected void onPostExecute(String result) {
	        
	        switch(op) {
	        case ERROR:
	        	parent.setProgressText("Error: " + result);
	        	break;
	        case GET_SPECS:
	        	{
	        		String reply[] = result.split(";");
					int width = Integer.parseInt(reply[0]);
					int height = Integer.parseInt(reply[1]);
					String name = reply[2];
					parent.setProgressText("Found '" + name + "', " + width + "x" + height + " display");
					grid = parent.setupGrid(width, height);
	        	}
				break;
	        case GET_FRAMEBUFFER:
		        {
	        		String reply[] = result.split(";");
	        		final int width = grid.getGridWidth();
	        		for (int i = 0; i < reply.length / 3; ++i) {
	        			int r = Integer.parseInt(reply[3*i + 0]);
	        			int g = Integer.parseInt(reply[3*i + 1]);
	        			int b = Integer.parseInt(reply[3*i + 2]);
	        			grid.setPixel(i % width, i / width, r, g, b);
	        		}
	        		grid.invalidate();
		        }
	        	break;
	        case UPDATE_PIXEL:
	        	// TODO: Look for 'OK'?
	        	break;
	        }
		}

	}

}