# ClassAttendanceSystem
Smart Attendance System is an AI-powered solution designed to automate and optimize attendance tracking. Instead of relying on manual registers or basic ID swipes, this system uses Face Recognition, Geo Location, and Day Detection to identify individuals accurately and mark their attendance in real-time.

1) System overview (quick)
Student app (Android): on “Mark Attendance” it:
checks GPS/geo-fence (optional),
scans Wi-Fi APs (BSSIDs) in range,
scans BLE beacons (advertised UUIDs) in range,
sends { studentId, classroomId, wifiBssids[], bleIds[], timestamp, deviceId } to backend.

Backend (Node.js/Express):
verifies that at least one known classroom Wi-Fi AP or BLE beacon is present, AND the student is registered for that classroom/time-slot,
stores attendance record to DB,
runs anomaly checks (e.g., same device used for many student IDs in short time).

Admin Web Dashboard (optional): 
view attendance & alerts.
You can demo without physical BLE beacons by running a teacher phone as a BLE advertiser or using known classroom Wi-Fi BSSIDs.

2) Tech stack & tools
Android Studio (Kotlin)
Node.js (v18+), Express
PostgreSQL (or SQLite for quick demo)
Optional: ngrok (for exposing local backend to device during dev)

3) Database schema (Postgres SQL)
Saved as schema.sql

4) Backend: Node.js + Express (minimal)
Installed packages
Created index.js

5) Android app (Kotlin) — key parts
NOTE: Wi-Fi scanning and BLE scanning require runtime permissions. Wi-Fi scan results on Android 9+ require location permission and device location enabled. For testing, run on a real device.
Created a new Android Studio project (Kotlin). Added permissions in AndroidManifest.xml

Important notes about Android scanning:
On Android 9+ you need location enabled and location permission to get scan results.
scanResults is best-effort — results depend on device and OS.
BLE scanning requires Bluetooth enabled and BLE devices advertising.

6) Register classroom & students (example SQL inserts)
INSERT INTO classrooms (id, name, allowed_bssids, allowed_ble_ids)
VALUES (1, 'Room 101', ARRAY['00:11:22:33:44:55','66:77:88:99:AA:BB'], ARRAY['beacon-uuid-1','beacon-uuid-2']);
INSERT INTO students (student_id, name) VALUES ('S123','Alice'), ('S124','Bob');

