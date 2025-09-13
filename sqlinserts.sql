INSERT INTO classrooms (id, name, allowed_bssids, allowed_ble_ids)
VALUES (1, 'Room 101', ARRAY['00:11:22:33:44:55','66:77:88:99:AA:BB'], ARRAY['beacon-uuid-1','beacon-uuid-2']);

INSERT INTO students (student_id, name) VALUES ('S123','Alice'), ('S124','Bob');
