package org.hive13.wall;

import android.content.SharedPreferences;
import android.content.SharedPreferences.OnSharedPreferenceChangeListener;
import android.os.Bundle;
import android.preference.Preference;
import android.preference.PreferenceActivity;
import android.preference.PreferenceManager;

public class SetupActivity extends PreferenceActivity
implements OnSharedPreferenceChangeListener {
	
	public static final String KEY_PREF_HOSTNAME = "org.hive13.wall.HostnameKey";
	public static final String KEY_PREF_PORT = "org.hive13.wall.PortKey";
	public static final String KEY_PREF_PRESSURE = "org.hive13.wall.PressureKey";
	
	@Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        PreferenceManager.setDefaultValues(this, R.xml.preferences, false);
        
        addPreferencesFromResource(R.xml.preferences);
        
    }
	
	@Override
	protected void onResume() {
		super.onResume();
		getPreferenceScreen().getSharedPreferences().registerOnSharedPreferenceChangeListener(this);
	}
	
	@Override
	protected void onPause() {
		super.onPause();
		getPreferenceScreen().getSharedPreferences().registerOnSharedPreferenceChangeListener(this);
	}
	
    public void onSharedPreferenceChanged(SharedPreferences sharedPreferences, String key) {
        if (key.equals(KEY_PREF_HOSTNAME) || key.equals(KEY_PREF_PORT)) {
            Preference pref = findPreference(key);
            // Set summary to be the user-description for the selected value
            pref.setSummary(sharedPreferences.getString(key, ""));
        } else if (key.equals(KEY_PREF_PRESSURE)) {
            //Preference pref = findPreference(key);
            //pref.setSummary(sharedPreferences.getBoolean(key, false) ? "true" : "false");
        }
    }	
}
