CREATE TABLE students (
  id SERIAL PRIMARY KEY,
  student_id VARCHAR(100) UNIQUE NOT NULL, -- e.g., roll no
  name TEXT NOT NULL
);

CREATE TABLE classrooms (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  allowed_bssids TEXT[],       -- array of known wifi BSSID strings
  allowed_ble_ids TEXT[]       -- array of known BLE beacon ids (UUIDs)
);

CREATE TABLE attendance (
  id SERIAL PRIMARY KEY,
  student_id VARCHAR(100) REFERENCES students(student_id),
  classroom_id INTEGER REFERENCES classrooms(id),
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT now(),
  wifi_bssids TEXT[],
  ble_ids TEXT[],
  device_id TEXT,
  status VARCHAR(20) DEFAULT 'PENDING', -- ACCEPTED / REJECTED / PENDING
  reason TEXT
);
