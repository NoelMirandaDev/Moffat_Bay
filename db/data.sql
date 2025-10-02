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
TRUNCATE TABLE team_member_contribution;
TRUNCATE TABLE team_member;

-- 3) Re-enable FK checks
SET FOREIGN_KEY_CHECKS = 1;

-- =========================
-- Room Types
-- =========================
INSERT INTO roomtype (RoomTypeID, TypeName, BedConfiguration, PricePerNight, MaxOccupancy) VALUES
(1, 'Standard Queen',  '1 Queen', 141.75, 2),
(2, 'Standard Double', '2 Full',  126.00, 4),
(3, 'Deluxe King',     '1 King',  168.00, 2),
(4, 'Bay View Suite',  '2 Queen', 157.50, 4);

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
(101, '101', 1, 0, 'Cozy queen, garden side',                                   'images/room101.jpeg'),
(102, '102', 2, 0, 'Two full beds, courtyard',                                  'images/room102.jpeg'),
(103, '103', 2, 1, 'ADA room with two full beds',                               'images/room103.jpeg'),
(201, '201', 3, 0, 'King room, partial bay view',                               'images/room201.jpeg'),
(202, '202', 3, 0, 'King room, near elevator',                                  'images/room202.jpeg'),
(301, '301', 4, 0, 'Top-floor suite with two identical full bay view bedrooms', 'images/room301.jpeg');

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
(3, 'Kyle', 'Marlia-Conner', 'kyle@example.com', '555-1002',
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
(1002, 2, 101, '2025-09-02', '2025-09-04', 2, 'Confirmed', NOW()),
(1003, 3, 301, '2025-09-29', '2025-10-02', 3, 'Confirmed', NOW()),
(1004, 1, 103, '2025-10-14', '2025-10-16', 2, 'Cancelled', NOW());

-- =========================
-- Audit Log
-- =========================
INSERT INTO auditlog (AuditLogID, CustomerID, Action, Description, Timestamp) VALUES
(5001, 1, 'Login',               'Customer logged in',                          NOW()),
(5002, 1, 'Reservation Created', 'Reservation 1001 created for Room 201',       NOW()),
(5003, 2, 'Reservation Created', 'Reservation 1002 created for Room 101',       NOW()),
(5004, 3, 'Reservation Created', 'Reservation 1003 created for Room 301',       NOW()),
(5005, NULL, 'System',           'Nightly job: availability refresh completed', NOW());

-- ===========================
-- Team Member TABLE
-- ===========================
INSERT INTO team_member (first_name, middle_name, last_name, role, bio, fun_fact, linkedin_url, github_url, email, profile_image) VALUES
-- Noel (1)
('Noel', 'Yobani', 'Miranda', 'Project Manager and Full Stack Developer',
 'With a passion for continuous growth, I am currently completing my third bachelor’s degree in Software Development at Bellevue University, graduating in October 2025. I also hold bachelor’s degrees in Sociology and Criminal Justice and recently served as a backend software engineering intern at SuperFile.\n\nMy expertise is in web development with a strong focus on security, and within this project my role as project manager and full stack developer centers on backend development while guiding the team’s progress.\n\nI am committed to lifelong learning, seeking challenges that strengthen my technical abilities and collaborative skills.',
 'Outside of coding, I enjoy exploring the wilderness with my fiancé, where we find inspiration and balance through hiking and connecting with nature.',
 'https://www.linkedin.com/in/nymirandadev',
 'https://github.com/NoelMirandaDev',
 'nymiranda.dev@gmail.com',
 'Noel_profile.jpg'
),
-- Kyle (2)
('Kyle', 'James', 'Marlia-Conner', 'Developer',
 'While growing up in rural Southern Oregon, I was a farm hand until I moved out. At that point I knew I wanted to work in technology as the only way I could communicate with my friends was due to the internet connection I had. Though idealistically I would like to work with a group to bring entertainment and joyful memories to people, I have found that I like to work in design and we all see/interact with fondly.',
 'Information and learning how things work/are created are my obsession. Though the term has its negative connotation, I aim to be a “Jack of all trades, master of none”. My passion, though, is with entertainment and every little inner working part that comes with it. Whether it be the physical aspects of a film/TV show (Directing, Lighting, Practical and Special Effects, Casting, Script Writing, etc.), or the digital ones (Visual Effects, Simulations, Sculpting, Rigging, Performance Capture), learning.',
 NULL,
 NULL,
 'kyleconner13@outlook.com',
 'Kyle_profile.jpg'
),
-- Steve (3)
('Steve', NULL, 'Stylin', 'Database Designer, Frontend & Backend Developer',
 'Steve was born in Haiti and holds a degree in Computer Science. She began her career as an Analyst Programmer for four years before being promoted to Junior Database Administrator, and three years later advancing to Senior DBA in Haiti.\n\nCurrently, Steve is expanding her expertise at Bellevue University, pursuing studies in Software Development to gain a broader perspective in the field.',
 'Steve loves hiking and camping. Her favorite authors include Eckhart Tolle, Stephen King, Edgar Allan Poe, and Nicholas Sparks. She is also fascinated by Egyptian history.',
 NULL,
 'https://github.com/sstylin',
 NULL,
 'Steve_profile.JPG'
),
-- Riese (4)
('Riese', NULL, 'Bohnak', 'Developer',
 'Riese is an innovative developer who excels at solving complex technical problems and bringing creative solutions to the team.\n\nTheir adaptability and dedication help ensure project milestones are met.',
 'Riese enjoys spending time with his family and loves running.',
 NULL,
 'https://github.com/Rojo234',
 NULL,
 'Riese_profile.jpg'
),
-- Amit (5)
('Amit', NULL, 'Rizal', 'Developer',
 'I am currently pursuing a degree in Software Development, with a strong focus on frontend technologies and user experience design. I previously went to college for supply chain and logistics and after completing about 1 and half year I decided to switch to software development.',
 'I enjoy outdoor adventures and road trips, and I also love exploring new music playlists.',
 NULL,
 NULL,
 'amitrizal@hotmail.com',
 'Amit_profile.jpg'
);

-- ========================
-- Team Member_contribution 
-- ========================
INSERT INTO team_member_contribution (team_member_id, contribution) VALUES
-- Noel
(1, 'Initialized the Moffat Bay project and repository structure'),
(1, 'Created the project README file'),
(1, 'Connected the database and configured application settings'),
(1, 'Implemented CSRF protection across all forms'),
(1, 'Developed the login (backend) and logout (frontend and backend) functionality'),
(1, 'Built the room reservation system: frontend and backend for room listings with pagination and detailed room booking page, and backend for the reservation summary page'),
(1, 'Implemented the reservation lookup backend'),
(1, 'Implemented secure password hashing during registration and contributed to backend validation for the registration process'),
(1, 'Handled session management across the application'),
(1, 'Refactored and modularized the codebase to improve reusability and scalability'),
(1, 'Broke down the routes page into a dedicated services layer to separate concerns and improve maintainability'),
(1, 'Led the team by breaking down tasks, updating the Kanban board, reviewing code, and providing constructive feedback throughout development'),
-- Kyle
(2, 'Created the main blueprint for the style guide the website will utilize'),
(2, 'Designed and implemented a pop-up login window (much like AirBnB or Kayak) that keeps the user on the page they were on'),
-- Steve
(3, 'Created the Technical Design Document (TDD) for the project'),
(3, 'Created the Entity Relationship Diagram (ERD) for the application database'),
(3, 'Developed the backend of the landing page'),
(3, 'Leading the development of the About Us page (frontend and backend)'),
-- Riese
(4, 'Registration Page Functional Test'),
(4, 'Reservation Summary page Frontend'),
(4, 'Registration Page Frontend & Backend'),
-- Amit
(5, 'Registration and reservation pages.'),
(5, 'Collaborated on user interface design and prototype');

-- =========================
-- Auto-increment adjustments (for nicer ID ranges)
-- =========================
ALTER TABLE roomtype    AUTO_INCREMENT = 100;
ALTER TABLE amenity     AUTO_INCREMENT = 100;
ALTER TABLE room        AUTO_INCREMENT = 500;
ALTER TABLE customer    AUTO_INCREMENT = 1000;
ALTER TABLE reservation AUTO_INCREMENT = 2000;
ALTER TABLE auditlog    AUTO_INCREMENT = 6000;
