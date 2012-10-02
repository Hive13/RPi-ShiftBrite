package org.hive13.wall;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLConnection;

import android.os.AsyncTask;
import android.os.Bundle;
import android.preference.PreferenceManager;
import android.app.Activity;
import android.content.Intent;
import android.content.SharedPreferences;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.TextView;

public class WallActivity extends Activity {
	final static String TAG = WallActivity.class.getSimpleName();
	
	int width = -1;
	int height = -1;
	String name = "";

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_wall);
        
    }
    
    @Override
    public void onResume() {
        super.onResume();
        
        // TODO: Move this ID into preferences.
        int id = 0;
        
        SharedPreferences sharedPref = PreferenceManager.getDefaultSharedPreferences(this);
        String hostname = sharedPref.getString(SetupActivity.KEY_PREF_HOSTNAME, "");
        String port = sharedPref.getString(SetupActivity.KEY_PREF_PORT, "");
        
        TextView hostnameView = (TextView) findViewById(R.id.hostnameView);
        hostnameView.setText(hostname + ":" + port);
        
        TextView progressView = (TextView) findViewById(R.id.progressView);
        progressView.setVisibility(TextView.VISIBLE);
        
		try {
			URL dest = new URL("http://" + hostname + ":" + port + "/display/specs/" + id);
	        progressView.setText("Trying to connect...");
			new HttpTask(HttpOperation.GET_SPECS).execute(dest);
		} catch (MalformedURLException e) {
			progressView.setText("Error with URL!");
			Log.e(TAG, "Error making URL: " + e.getMessage());
		}
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.activity_wall, menu);
        return true;
    }
    
    @Override
    public boolean onOptionsItemSelected (MenuItem item) {
    	switch (item.getItemId()) {
		case R.id.menu_settings:
			Intent intent = new Intent(this, SetupActivity.class);
			startActivity(intent);
			break;
		case R.id.menu_clearwall:
			
			break;
		default:
			break;
		}
		return super.onOptionsItemSelected(item);	
    }
    
    private void setupGrid() {
    	
        GridEditor wall = (GridEditor) findViewById(R.id.gridEditor);
        wall.setGridSize(width,  height);
 
        int id = 0;
        // TODO: Factor these out (they're repeated)
        SharedPreferences sharedPref = PreferenceManager.getDefaultSharedPreferences(this);
        String hostname = sharedPref.getString(SetupActivity.KEY_PREF_HOSTNAME, "");
        String port = sharedPref.getString(SetupActivity.KEY_PREF_PORT, "");
        
		URL dest;
		try {
			dest = new URL("http://" + hostname + ":" + port + "/display/" + id);
			new HttpTask(HttpOperation.GET_FRAMEBUFFER).execute(dest);
		} catch (MalformedURLException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
    }

    private enum HttpOperation { GET_SPECS, GET_FRAMEBUFFER, UPDATE_PIXEL, ERROR };
    
	private class HttpTask extends AsyncTask<URL, Integer, String> {
		
		private HttpOperation op;
		
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
	        TextView progressView = (TextView) findViewById(R.id.progressView);
	        
	        switch(op) {
	        case ERROR:
				progressView.setText("Error: " + result);
	        	break;
	        case GET_SPECS:
	        	{
	        		String reply[] = result.split(";");
					width = Integer.parseInt(reply[0]);
					height = Integer.parseInt(reply[1]);
					name = reply[2];
					progressView.setText("Found '" + name + "', " + width + "x" + height + " display");
					setupGrid();
	        	}
				break;
	        case GET_FRAMEBUFFER:
		        {
			        GridEditor wall = (GridEditor) findViewById(R.id.gridEditor);
	        		String reply[] = result.split(";");
	        		final int width = wall.getGridWidth();
	        		for (int i = 0; i < reply.length / 3; ++i) {
	        			int r = Integer.parseInt(reply[3*i + 0]);
	        			int g = Integer.parseInt(reply[3*i + 1]);
	        			int b = Integer.parseInt(reply[3*i + 2]);
	        			wall.setPixel(i % width, i / width, r, g, b);
	        		}
	        		wall.invalidate();
		        }
	        	break;
	        case UPDATE_PIXEL:
	        	// TODO: Look for 'OK'?
	        	break;
	        }
		}
	}
}

