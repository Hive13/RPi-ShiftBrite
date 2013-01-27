package org.hive13.wall;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ScheduledThreadPoolExecutor;
import java.util.concurrent.TimeUnit;

import android.graphics.Color;
import android.os.AsyncTask;
import android.util.Log;

public class WallCommunication {
	final static String TAG = WallCommunication.class.getSimpleName();
	
	private ScheduledThreadPoolExecutor pool = new ScheduledThreadPoolExecutor(1);
	
	// This is the WallActivity that owns us, as we need to make calls back to
	// it for certain async operations.
	private WallActivity parent = null;
	
	// This is a queue of updates that are not yet committed.
	// (It's a map since updates to the same pixel coordinate should overwrite
	// old ones)
	volatile private Map<PixelCoordinate, Integer> updateQueue = new HashMap<PixelCoordinate, Integer>();
	
	// This is the grid we receive back from WallActivity, as we must set its
	// pixels directly.
	private GridEditor grid = null;
	
	// baseUrl: URL up to the point commands should be added,
	// e.g. http://192.168.0.100:8080/display
	private URL baseUrl = null;
	
	// The ID of the display which this object targets 
	private int displayId;
	
	public WallCommunication(WallActivity parent, URL baseUrl, int dispId) {
		this.baseUrl = baseUrl;
		this.parent = parent;
		this.displayId = dispId;
	}
	
	// This queues an update to the display. Actual updating will wait until
	// the next bulk update is submitted.
	public void queueUpdate(PixelCoordinate coord, int color) {
		updateQueue.put(coord, color);
	}
	
	// This is an async call to retrieve the specs of the remote display.
	public void getDisplaySpecs() throws MalformedURLException {
		URL dest = new URL(baseUrl, "specs/" + displayId);
		HttpTask task = new HttpTask(dest, "GET", "") {
			@Override
			protected void onPostExecute(String result) {
				if (checkErrors(result)) return;
				
	    		String reply[] = result.split(";");
				int width = Integer.parseInt(reply[0]);
				int height = Integer.parseInt(reply[1]);
				String name = reply[2];
				parent.setProgressText("Found '" + name + "', " + width + "x" + height + " display");
				grid = parent.setupGrid(width, height);
			}
		};
		task.execute();
	}
	
	// This is an async call to query the current state of the remote display,
	// should it fall out of sync with our local copy.
	public void getDisplayState() throws MalformedURLException {
		URL dest = new URL(baseUrl, "" + displayId);
		HttpTask task = new HttpTask(dest, "GET", "") {
			@Override
			protected void onPostExecute(String result) {
				if (checkErrors(result)) return;
				
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
		};
		task.execute();
	}

	public void clearDisplay() throws MalformedURLException {
		
		// Clearing should cancel any updates in progress.
		updateQueue.clear();
		
		URL dest = new URL(baseUrl, "clear/" + displayId);
		HttpTask task = new HttpTask(dest, "GET", "") {
			
			@Override
			protected void onPostExecute(String result) {
				if (checkErrors(result)) return;
				
				if (result.equals("OK")) {
					Log.i(TAG, "Reply looks good!");
					grid.clearGrid();
				} else {
					Log.w(TAG, "Received reply: " + result);
				}
			}	
		};
		task.execute();
	}
	
	private void updateDisplay() {
		
		URL dest = null;
		try {
			dest = new URL(baseUrl, "" + displayId);
		} catch (MalformedURLException e) {
			// What do we do here with an exception?
			// If we can't make a URL, there is no sense in building up the
			// HTTP body.
			return;
		}
		
		// Build up a body for the HTTP PUT
		String body = "";
	
		// Move the update queue to our local copy (for us to safely use) and
		// make a new update queue (for other threads to safely modify).
		Map<PixelCoordinate, Integer> oldQueue = updateQueue;
		updateQueue = new HashMap<PixelCoordinate, Integer>();
		for (PixelCoordinate coord : oldQueue.keySet()) {
			int color = oldQueue.get(coord);
			body += coord.x + ";" +
					coord.y + ";" +
					Color.red(color) + ";" +
					Color.green(color) + ";" +
					Color.blue(color) + "\n";
		}
		
		HttpTask task = new HttpTask(dest, "PUT", body) {
			@Override
			protected void onPostExecute(String result) {
				if (checkErrors(result)) return;
				
				if (result.equals("OK")) {
					Log.i(TAG, "Reply looks good!");
				}
				
			}
		};
		
		task.execute();
	}
	
	public void startUpdates() {
		Runnable cmd = new Runnable() {
			@Override
			public void run() {
				// If no updates are waiting, don't bother.
				if (updateQueue.size() == 0) {
					return;
				}
				updateDisplay();
			}
		};
		pool.scheduleAtFixedRate(cmd, 0, 100, TimeUnit.MILLISECONDS);
	}
	
	public void stopUpdates() {
		pool.shutdown();
		try {
			pool.awaitTermination(250, TimeUnit.MILLISECONDS);
		} catch (InterruptedException e) {
			Log.w(TAG, "Timeout waiting for HTTP update!");
		}
	}

	private abstract class HttpTask extends AsyncTask<Object, Integer, String> {
		
		protected URL destUrl = null;
		
		protected String method = "GET";
		
		protected String body = "";
		
		protected boolean error = false;
		
		public HttpTask(URL dest, String method, String body) {
			this.destUrl = dest;
			this.method = method;
			this.body = body;
		}
				
		@Override
		protected String doInBackground(Object... ignore) {
			// This isn't guaranteed to run in the same thread, so don't touch
			// anything in the GUI here.
			HttpURLConnection conn;
			String result = null;
			try {
				conn = (HttpURLConnection) destUrl.openConnection();
				if (conn == null) {
					error = true;
					throw new Exception("Invalid URL!");
				}
				conn.setRequestMethod(method);
				
				if (body != null && body.length() > 0) {
					conn.setDoOutput(true);
					OutputStreamWriter out = new OutputStreamWriter(conn.getOutputStream());
					out.write(body);
					out.close();
				}
				
				InputStream is = conn.getInputStream();
				InputStreamReader isr = new InputStreamReader(is);
				BufferedReader rd = new BufferedReader(isr);
				result = rd.readLine();
				
			} catch (Exception e) {
				result = e.getMessage();
			}
			return result;
		}
		
		protected boolean checkErrors(String result) {
			if (result == null) {
				parent.setProgressText("Error; result is null?");
				return true;
			}
			
			if (error) {
				parent.setProgressText("Error: " + result);
				return true;
			} else {
				return false;
			}
		}
	}
		
}