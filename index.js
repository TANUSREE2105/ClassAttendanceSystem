const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const { Pool } = require('pg');

const pool = new Pool({
  connectionString: process.env.DATABASE_URL || 'postgres://postgres:password@localhost:5432/attendance'
});

const app = express();
app.use(cors());
app.use(bodyParser.json());

// simple helper to query DB
async function query(q, params){ const r = await pool.query(q, params); return r.rows; }

/**
 * Mark attendance endpoint
 * Expects: { studentId, classroomId, wifiBssids: [], bleIds: [], deviceId }
 */
app.post('/api/attendance/mark', async (req, res) => {
  try {
    const { studentId, classroomId, wifiBssids = [], bleIds = [], deviceId } = req.body;
    if (!studentId || !classroomId) return res.status(400).json({error:'studentId and classroomId required'});

    // fetch classroom config
    const cls = (await query('SELECT * FROM classrooms WHERE id=$1', [classroomId]))[0];
    if (!cls) return res.status(404).json({error:'classroom not found'});

    // check intersection with allowed bssids or ble ids
    const intersect = (arrA, arrB) => arrA.filter(x => arrB.includes(x));
    const foundWiFi = intersect(wifiBssids, cls.allowed_bssids || []);
    const foundBle = intersect(bleIds, cls.allowed_ble_ids || []);

    let status = 'REJECTED';
    let reason = 'No known wifi/ble found';
    if (foundWiFi.length > 0 || foundBle.length > 0) {
      status = 'ACCEPTED';
      reason = `Found wifi:${foundWiFi.length} ble:${foundBle.length}`;
    }

    // Save attendance row
    await pool.query(
      `INSERT INTO attendance(student_id, classroom_id, wifi_bssids, ble_ids, device_id, status, reason)
       VALUES($1,$2,$3,$4,$5,$6,$7)`,
      [studentId, classroomId, wifiBssids, bleIds, deviceId, status, reason]
    );

    // Basic anomaly detection: has this device been used for >3 different studentIds in last 10 minutes?
    const anomalies = await query(
      `SELECT COUNT(DISTINCT student_id) as cnt FROM attendance
       WHERE device_id=$1 AND timestamp > NOW() - INTERVAL '10 minutes'`, [deviceId]
    );
    const cnt = parseInt(anomalies[0].cnt, 10);
    if (cnt > 3) {
      // flagging (in real system push notif or admin notice)
      console.warn(`Anomaly: device ${deviceId} used for ${cnt} students recently`);
    }

    res.json({status, reason});
  } catch (err) {
    console.error(err);
    res.status(500).json({error:'server error'});
  }
});

app.listen(3000, () => console.log('Backend listening on :3000'));
