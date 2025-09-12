-- =========================================================
-- Moffat Bay – Seed Data (development)
-- This script clears existing rows and inserts sample data.
-- Run AFTER schema.sql has created the database & tables.
-- =========================================================

-- Make sure we target the right database
USE moffat_bay;

-- 1) Temporarily disable FK checks to allow truncates in any order
SET FOREIGN_KEY_CHECKS = 0;

-- 2) Clear tables
TRUNCATE TABLE auditlog;
TRUNCATE TABLE reservation;
TRUNCATE TABLE roomamenity;
TRUNCATE TABLE room;
TRUNCATE TABLE amenity;
TRUNCATE TABLE roomtype;
TRUNCATE TABLE customer;

-- 3) Re-enable FK checks
SET FOREIGN_KEY_CHECKS = 1;

-- =========================
-- Room Types
-- =========================
INSERT INTO roomtype (RoomTypeID, TypeName, BedConfiguration, PricePerNight, MaxOccupancy) VALUES
(1, 'Standard Queen',   '1 Queen',              129.00, 2),
(2, 'Standard Double',  '2 Full',               149.00, 4),
(3, 'Deluxe King',      '1 King',               179.00, 2),
(4, 'Bay View Suite',   '1 King + Sofa Bed',    229.00, 4);

-- =========================
-- Amenities
-- =========================
INSERT INTO amenity (AmenityID, Name, Description) VALUES
(1, 'WiFi',        'High-speed wireless internet'),
(2, 'Ocean View',  'Partial or full view of the bay'),
(3, 'Mini-Fridge', 'In-room mini-fridge'),
(4, 'Breakfast',   'Continental breakfast'),
(5, 'Parking',     'On-site self-parking'),
(6, 'ADA Shower',  'Accessible roll-in shower');

-- =========================
-- Rooms
-- =========================
-- Note: ADAAccessible uses 0/1 (false/true)
INSERT INTO room (RoomID, RoomNumber, RoomTypeID, ADAAccessible, Description, ImagePath) VALUES
(101, '101', 1, 0, 'Cozy queen, garden side', 'images/room101.jpeg'),
(102, '102', 2, 0, 'Two full beds, courtyard', 'images/room102.jpeg'),
(103, '103', 2, 1, 'ADA room with two full beds', 'images/room103.jpeg'),
(201, '201', 3, 0, 'King room, partial bay view', 'images/room201.jpeg'),
(202, '202', 3, 0, 'King room, near elevator', 'images/room202.jpeg'),
(301, '301', 4, 0, 'Top-floor suite, full bay view', 'images/room301.jpeg');

-- =========================
-- Room ↔ Amenity (many-to-many)
-- =========================
INSERT INTO roomamenity (RoomID, AmenityID) VALUES
(101, 1), (101, 3), (101, 5),
(102, 1), (102, 3), (102, 5),
(103, 1), (103, 3), (103, 5), (103, 6),
(201, 1), (201, 2), (201, 3), (201, 5),
(202, 1), (202, 3), (202, 5),
(301, 1), (301, 2), (301, 3), (301, 4), (301, 5);

-- =========================
-- Customers
-- =========================
-- Note: The PasswordHash data is hashed (use Password123 for testing)
INSERT INTO customer (CustomerID, FirstName, LastName, Email, Phone, PasswordHash, RegistrationDate) VALUES
(1, 'Amit', 'Rizal', 'amit@example.com', '555-1000',
'scrypt:32768:8:1$qf39ADPITLzbzecX$57a22d2620dbf5dd3ee8e93e9b0a4dc6bfacb18152e7d6048596849e0aba97078796a84d736317983992c38212a5f12e7b86c83770242041da112160ab63b6ae',
NOW()),
(2, 'Noel', 'Miranda', 'noel@example.com', '555-1001',
'scrypt:32768:8:1$H7Q2OgjMdZZ9Tcdj$dc94b8678b5a1cc7b98b32311d5c8ac9b01caf1810d767566db9d36ebd0a0afd40c6f96ef1cca11ba98c631dfccbebd23d1ba040ef317026995ae1d7bd03bf08',
NOW()),
(3, 'Kyle', 'McCarthy', 'kyle@example.com', '555-1002',
'scrypt:32768:8:1$NTfSLirCkDBcUAfL$0e7cfadfee241137a205c52231b81812346ab729fe23157eb0586b245592bea741ede17edc7c28e4b98042364368ba5115e1685af95540c397f75a3f1e9cb741',
NOW()),
(4, 'Steve', 'Stylin', 'steve@example.com', '555-1003',
'scrypt:32768:8:1$0ihRndprtPUGeWmJ$722f006e4b0e229318f5704e46b82e71afd5073efca789fc01786969dd5afc21ca7dba0039fe6a93a5050a0bb5e67529c3e3b8e6f5bfd018b975494a34f3ac47',
NOW()),
(5, 'Riese', 'Bohnak', 'riese@example.com', '555-1004',
'scrypt:32768:8:1$Qy6h6ICLkhLk2L8e$d289243739d17306d3ff3e817be2e4512480e4223abbedf6eee80fbf2026a1cf6eea2488bb7e62c19c2b80fdfd68b1cc89f02e7bb35587f90eb32561b4560693',
NOW());

-- =========================
-- Reservations
-- =========================
INSERT INTO reservation (ReservationID, CustomerID, RoomID, CheckInDate, CheckOutDate, NumberOfGuests, ReservationStatus, DateReserved) VALUES
(1001, 1, 201, '2025-09-06', '2025-09-09', 2, 'Confirmed', NOW()),
(1002, 2, 101, '2025-09-02', '2025-09-04', 2, 'Pending',   NOW()),
(1003, 3, 301, '2025-09-29', '2025-10-02', 3, 'Confirmed', NOW()),
(1004, 1, 103, '2025-10-14', '2025-10-16', 2, 'Cancelled', NOW());

-- =========================
-- Audit Log
-- =========================
INSERT INTO auditlog (AuditLogID, CustomerID, Action, Description, Timestamp) VALUES
(5001, 1, 'Login',               'Customer logged in',                                  NOW()),
(5002, 1, 'Reservation Created', 'Reservation 1001 created for Room 201',               NOW()),
(5003, 2, 'Reservation Created', 'Reservation 1002 created for Room 101',               NOW()),
(5004, 3, 'Reservation Created', 'Reservation 1003 created for Room 301',               NOW()),
(5005, NULL, 'System',           'Nightly job: availability refresh completed',         NOW());

-- =========================
-- Auto-increment adjustments (for nicer ID ranges)
-- =========================
ALTER TABLE roomtype    AUTO_INCREMENT = 100;
ALTER TABLE amenity     AUTO_INCREMENT = 100;
ALTER TABLE room        AUTO_INCREMENT = 500;
ALTER TABLE customer    AUTO_INCREMENT = 1000;
ALTER TABLE reservation AUTO_INCREMENT = 2000;
ALTER TABLE auditlog    AUTO_INCREMENT = 6000;