package org.hive13.wall;

import java.net.MalformedURLException;
import java.net.URL;
import org.hive13.wall.WallCommunication.HttpOperation;

import android.os.Bundle;
import android.preference.PreferenceManager;
import android.app.Activity;
import android.content.Intent;
import android.content.SharedPreferences;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.TextView;

public class WallActivity extends Activity
//implements OnSharedPreferenceChangeListener
{
	final static String TAG = WallActivity.class.getSimpleName();
	
	WallCommunication comm = null;
	
	private int width = -1;
	private int height = -1;
	private String name = "";

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
        
        GridEditor wall = (GridEditor) findViewById(R.id.gridEditor);
        wall.setParentWall(this);
        
		try {
			URL dest = new URL("http://" + hostname + ":" + port + "/display/");
	        progressView.setText("Trying to connect...");
	        comm = new WallCommunication(this, dest);
	        comm.startAsyncOp(HttpOperation.GET_SPECS);
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
	        try {
		        GridEditor wall = (GridEditor) findViewById(R.id.gridEditor);
				comm.startAsyncOp(HttpOperation.CLEAR_DISPLAY);
		        wall.clearGrid();
			} catch (MalformedURLException e) {
				Log.e(TAG, "Cannot form URL: " + e.getMessage());
			}
			break;
		case R.id.menu_refresh:
			refreshPreview();
			break;
		default:
			break;
		}
		return super.onOptionsItemSelected(item);	
    }
    
    public GridEditor setupGrid(int width, int height) {

    	this.width = width;
    	this.height = height;
    	
        GridEditor wall = (GridEditor) findViewById(R.id.gridEditor);
        wall.setGridSize(width,  height);
 
        refreshPreview();
        
		return wall;
    }
    
    public void setProgressText(String text) {
        TextView progressView = (TextView) findViewById(R.id.progressView);
        progressView.setVisibility(TextView.VISIBLE);
        progressView.setText(text);
    }
    
    public void refreshPreview() {
        
        if (comm == null) {
        	Log.e(TAG, "WallCommunication was never initialized!");
        	return;
        }
        
		try {
			comm.startAsyncOp(HttpOperation.GET_FRAMEBUFFER);
		} catch (MalformedURLException e) {
			Log.e(TAG, "Error refreshing: " + e.getMessage());
		}

    }
    
    public void onPress(int x, int y, int r, int g, int b) {
    	 
        if (comm == null) {
        	Log.e(TAG, "WallCommunication was never initialized!");
        	return;
        }
        
		try {
			String param = String.format("?x=%d&y=%d&r=%d&g=%d&b=%d", x, y, r, g, b);
			comm.startAsyncOp(HttpOperation.UPDATE_PIXEL, param);
		} catch (MalformedURLException e) {
			Log.e(TAG, "Error updating: " + e.getMessage());
		}

    }
    
    /*
    public void onSharedPreferenceChanged(SharedPreferences sharedPreferences, String key) {
        if (key.equals(SetupActivity.KEY_PREF_HOSTNAME)) {
            sharedPreferences.getString(key, "");
        } else if (key.equals(SetupActivity.KEY_PREF_PORT)) {
            sharedPreferences.getString(key, "");
        }
    }
    */	
}

