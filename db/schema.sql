-- Drop the database if it already exists
DROP DATABASE IF EXISTS moffat_bay;

-- Create the database
CREATE DATABASE moffat_bay;

-- Use this database
USE moffat_bay;

-- --------------------------------------------------------
-- Table structure for table `customer`
-- --------------------------------------------------------
CREATE TABLE `customer` (
  `CustomerID` int(11) NOT NULL AUTO_INCREMENT,
  `FirstName` varchar(50) NOT NULL,
  `LastName` varchar(50) NOT NULL,
  `Email` varchar(100) NOT NULL UNIQUE,
  `Phone` varchar(20) DEFAULT NULL,
  `PasswordHash` varchar(255) NOT NULL,
  `RegistrationDate` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`CustomerID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Table structure for table `roomtype`
-- --------------------------------------------------------
CREATE TABLE `roomtype` (
  `RoomTypeID` int(11) NOT NULL AUTO_INCREMENT,
  `TypeName` varchar(50) NOT NULL UNIQUE,
  `BedConfiguration` varchar(50) DEFAULT NULL,
  `PricePerNight` decimal(8,2) NOT NULL,
  `MaxOccupancy` int(11) NOT NULL,
  PRIMARY KEY (`RoomTypeID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Table structure for table `amenity`
-- --------------------------------------------------------
CREATE TABLE `amenity` (
  `AmenityID` int(11) NOT NULL AUTO_INCREMENT,
  `Name` varchar(50) NOT NULL UNIQUE,
  `Description` text DEFAULT NULL,
  PRIMARY KEY (`AmenityID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Table structure for table `room`
-- --------------------------------------------------------
CREATE TABLE `room` (
  `RoomID` int(11) NOT NULL AUTO_INCREMENT,
  `RoomNumber` varchar(10) NOT NULL UNIQUE,
  `RoomTypeID` int(11) NOT NULL,
  `ADAAccessible` tinyint(1) DEFAULT 0,
  `Description` text DEFAULT NULL,
  PRIMARY KEY (`RoomID`),
  KEY `RoomTypeID` (`RoomTypeID`),
  CONSTRAINT `room_ibfk_1` FOREIGN KEY (`RoomTypeID`) REFERENCES `roomtype` (`RoomTypeID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Table structure for table `roomamenity`
-- --------------------------------------------------------
CREATE TABLE `roomamenity` (
  `RoomID` int(11) NOT NULL,
  `AmenityID` int(11) NOT NULL,
  PRIMARY KEY (`RoomID`,`AmenityID`),
  KEY `AmenityID` (`AmenityID`),
  CONSTRAINT `roomamenity_ibfk_1` FOREIGN KEY (`RoomID`) REFERENCES `room` (`RoomID`),
  CONSTRAINT `roomamenity_ibfk_2` FOREIGN KEY (`AmenityID`) REFERENCES `amenity` (`AmenityID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Table structure for table `reservation`
-- --------------------------------------------------------
CREATE TABLE `reservation` (
  `ReservationID` int(11) NOT NULL AUTO_INCREMENT,
  `CustomerID` int(11) NOT NULL,
  `RoomID` int(11) NOT NULL,
  `CheckInDate` date NOT NULL,
  `CheckOutDate` date NOT NULL,
  `NumberOfGuests` int(11) NOT NULL,
  `ReservationStatus` enum('Pending','Confirmed','Cancelled') DEFAULT 'Pending',
  `DateReserved` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`ReservationID`),
  KEY `CustomerID` (`CustomerID`),
  KEY `RoomID` (`RoomID`),
  CONSTRAINT `reservation_ibfk_1` FOREIGN KEY (`CustomerID`) REFERENCES `customer` (`CustomerID`),
  CONSTRAINT `reservation_ibfk_2` FOREIGN KEY (`RoomID`) REFERENCES `room` (`RoomID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Table structure for table `auditlog`
-- --------------------------------------------------------
CREATE TABLE `auditlog` (
  `AuditLogID` int(11) NOT NULL AUTO_INCREMENT,
  `CustomerID` int(11) DEFAULT NULL,
  `Action` varchar(50) NOT NULL,
  `Description` text DEFAULT NULL,
  `Timestamp` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`AuditLogID`),
  KEY `CustomerID` (`CustomerID`),
  CONSTRAINT `auditlog_ibfk_1` FOREIGN KEY (`CustomerID`) REFERENCES `customer` (`CustomerID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;