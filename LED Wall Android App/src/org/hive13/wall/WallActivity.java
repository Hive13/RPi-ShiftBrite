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
import android.widget.GridView;
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
			new GetInfoTask().execute(dest);
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
		default:
			break;
		}
		return super.onOptionsItemSelected(item);	
    }
    
    private void setupGrid() {
    	
        GridEditor wall = (GridEditor) findViewById(R.id.gridEditor);
        wall.setGridSize(width,  height);
        
    }

	private class GetInfoTask extends AsyncTask<URL, Integer, String> {
		private boolean error = false;
		
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
				error = true;
				result = e.getMessage();
			}
			return result;
		}

		protected void onPostExecute(String result) {
	        TextView progressView = (TextView) findViewById(R.id.progressView);
	        
			if (error) {
				progressView.setText("Error: " + result);
			} else {
				String reply[] = result.split(";");
				width = Integer.parseInt(reply[0]);
				height = Integer.parseInt(reply[1]);
				name = reply[2];
				progressView.setText("Found '" + name + "', " + width + "x" + height + " display");
				setupGrid();
			}
		}

	}
}

