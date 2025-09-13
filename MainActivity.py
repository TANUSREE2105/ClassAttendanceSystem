import android.Manifest
import android.bluetooth.BluetoothAdapter
import android.bluetooth.le.ScanCallback
import android.bluetooth.le.ScanResult
import android.content.Context
import android.content.Intent
import android.net.wifi.WifiManager
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.util.Log
import android.widget.Button
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import kotlinx.coroutines.*
import org.json.JSONArray
import org.json.JSONObject
import java.net.URL
import javax.net.ssl.HttpsURLConnection

class MainActivity : AppCompatActivity() {

    private lateinit var wifiManager: WifiManager
    private val bleFound = mutableSetOf<String>()
    private val wifiFound = mutableSetOf<String>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        wifiManager = applicationContext.getSystemService(Context.WIFI_SERVICE) as WifiManager

        val requestPermissionLauncher = registerForActivityResult(
            ActivityResultContracts.RequestMultiplePermissions()
        ) { perms ->
            // permissions granted or not
        }

        requestPermissionLauncher.launch(arrayOf(
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.ACCESS_COARSE_LOCATION
        ))

        val markBtn = findViewById<Button>(R.id.buttonMark)
        markBtn.setOnClickListener {
            startScanAndSend()
        }
    }

    private fun startScanAndSend() {
        wifiFound.clear(); bleFound.clear()
        scanWifi()
        scanBle()
        // Give time for scans to collect results, then send (simple approach)
        GlobalScope.launch(Dispatchers.Main) {
            delay(3000)
            sendAttendance()
        }
    }

    private fun scanWifi() {
        if (!wifiManager.isWifiEnabled) wifiManager.isWifiEnabled = true
        // start scan
        wifiManager.startScan()
        val results = wifiManager.scanResults
        for (r in results) {
            wifiFound.add(r.BSSID) // BSSID is MAC of AP
        }
        Log.d("ATT", "Wifi found: $wifiFound")
    }

    private fun scanBle() {
        val bluetoothAdapter = BluetoothAdapter.getDefaultAdapter() ?: return
        val scanner = bluetoothAdapter.bluetoothLeScanner ?: return
        val cb = object : ScanCallback() {
            override fun onScanResult(callbackType: Int, result: ScanResult?) {
                result?.scanRecord?.deviceName?.let { name ->
                    bleFound.add(name)
                }
                result?.device?.address?.let { addr ->
                    bleFound.add(addr)
                }
            }
        }
        scanner.startScan(cb)
        // stop after 2.5s
        GlobalScope.launch(Dispatchers.Main) {
            delay(2500)
            scanner.stopScan(cb)
            Log.d("ATT", "BLE found: $bleFound")
        }
    }

    private fun sendAttendance() {
        val studentId = "S123"                 // replace with actual registered student id
        val classroomId = 1                   // sample classroom id
        val deviceId = Settings.Secure.getString(contentResolver, Settings.Secure.ANDROID_ID)

        val payload = JSONObject().apply {
            put("studentId", studentId)
            put("classroomId", classroomId)
            put("wifiBssids", JSONArray(wifiFound.toList()))
            put("bleIds", JSONArray(bleFound.toList()))
            put("deviceId", deviceId)
        }
        // Simple network call on background thread
        GlobalScope.launch(Dispatchers.IO) {
            try {
                val url = URL("http://YOUR_BACKEND_IP:3000/api/attendance/mark")
                val conn = url.openConnection() as HttpsURLConnection
                conn.requestMethod = "POST"
                conn.setRequestProperty("Content-Type", "application/json")
                conn.doOutput = true
                conn.outputStream.write(payload.toString().toByteArray())
                val code = conn.responseCode
                val resp = conn.inputStream.bufferedReader().readText()
                Log.d("ATT", "Response $code : $resp")
            } catch (e: Exception) {
                Log.e("ATT", "Error sending", e)
            }
        }
    }
}
