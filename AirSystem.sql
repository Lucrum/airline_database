-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:8889
-- Generation Time: May 02, 2022 at 08:48 PM
-- Server version: 5.7.34
-- PHP Version: 7.4.21

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `AirSystem`
--

-- --------------------------------------------------------

--
-- Table structure for table `airline`
--

CREATE TABLE `airline` (
  `airline_name` varchar(20) NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `airline`
--

INSERT INTO `airline` (`airline_name`) VALUES
('American'),
('China Eastern'),
('Delta'),
('United');

-- --------------------------------------------------------

--
-- Table structure for table `airline_staff`
--

CREATE TABLE `airline_staff` (
  `username` varchar(32) NOT NULL,
  `s_password` varchar(200) DEFAULT NULL,
  `airline_name` varchar(20) DEFAULT NULL,
  `first_name` varchar(20) NOT NULL,
  `last_name` varchar(20) NOT NULL,
  `date_of_birth` date DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `airline_staff`
--

INSERT INTO `airline_staff` (`username`, `s_password`, `airline_name`, `first_name`, `last_name`, `date_of_birth`) VALUES
('tc9152', 'tc19782244', 'China Eastern', 'Timothy', 'Charleson', '1978-08-07'),
('ys723', '123321', 'United', 'James', 'Green', '1999-09-30'),
('111', '12333', 'rnh', 'huau', 'sbfu', '2022-04-26');

-- --------------------------------------------------------

--
-- Table structure for table `airline_staff_phone_number`
--

CREATE TABLE `airline_staff_phone_number` (
  `username` varchar(32) NOT NULL,
  `phone_number` varchar(20) NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `airline_staff_phone_number`
--

INSERT INTO `airline_staff_phone_number` (`username`, `phone_number`) VALUES
('111', ','),
('111', '1'),
('111', '2'),
('111', '3'),
('111', '4'),
('111', '5'),
('111', '6'),
('tc9152', '9186552837');

-- --------------------------------------------------------

--
-- Table structure for table `airplane`
--

CREATE TABLE `airplane` (
  `airplane_id` varchar(20) NOT NULL,
  `num_of_seats` int(11) DEFAULT NULL,
  `manufacturer` varchar(50) DEFAULT NULL,
  `age` varchar(20) DEFAULT NULL,
  `airline_name` varchar(20) DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `airplane`
--

INSERT INTO `airplane` (`airplane_id`, `num_of_seats`, `manufacturer`, `age`, `airline_name`) VALUES
('747-400', 568, 'Boeing Commercial Airplanes', '28', 'China Eastern'),
('A380', 525, 'Airbus', '17', 'China Eastern'),
('A340-500', 313, 'Airbus', '15', 'China Eastern'),
('A325', 130, 'Airbus', '3', 'United'),
('787-300', 418, 'Boeing', '4', 'United'),
('479-9', 418, 'Boeing', '1', 'United'),
('777-300', 432, 'Boeing', '6', 'Delta');

-- --------------------------------------------------------

--
-- Table structure for table `airport`
--

CREATE TABLE `airport` (
  `airport_code` varchar(5) NOT NULL,
  `airport_name` varchar(50) DEFAULT NULL,
  `country` varchar(50) DEFAULT NULL,
  `city` varchar(50) DEFAULT NULL,
  `type` varchar(20) DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `airport`
--

INSERT INTO `airport` (`airport_code`, `airport_name`, `country`, `city`, `type`) VALUES
('JFK', 'John F. Kennedy International Airport', 'United States of America', 'New York City', 'Both'),
('PVG', 'Shanghai Pudong International Airport', 'China', 'Shanghai', 'International'),
('SFO', 'San Francisco International Airport', 'United States', 'San Francisco', 'Both'),
('BOS', 'Logan International Airport', 'United States', 'Boston', 'Both');

-- --------------------------------------------------------

--
-- Table structure for table `customer`
--

CREATE TABLE `customer` (
  `email` varchar(50) NOT NULL,
  `first_name` varchar(20) NOT NULL,
  `last_name` varchar(20) NOT NULL,
  `c_password` varchar(200) DEFAULT NULL,
  `state` varchar(50) DEFAULT NULL,
  `city` varchar(50) DEFAULT NULL,
  `street` varchar(50) DEFAULT NULL,
  `building_number` varchar(10) DEFAULT NULL,
  `phone_number` varchar(20) DEFAULT NULL,
  `passport_number` varchar(20) DEFAULT NULL,
  `passport_expiration` date DEFAULT NULL,
  `passport_country` varchar(50) DEFAULT NULL,
  `date_of_birth` date DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `customer`
--

INSERT INTO `customer` (`email`, `first_name`, `last_name`, `c_password`, `state`, `city`, `street`, `building_number`, `phone_number`, `passport_number`, `passport_expiration`, `passport_country`, `date_of_birth`) VALUES
('carlT@hotmail.com', 'Carl', 'Thorne', 'paSsword', 'Arkansas', 'Conway', 'Christian Street', '1918', '5016612021', 'Q12438925', '2025-07-14', 'United States of America', '1918-02-11'),
('sallyM@yahoo.com', 'Sally', 'Margarine', 'apple38', 'Montana', 'Lewis Town', 'West Pine Street', '509', '4063244777', 'P05937291', '2022-08-22', 'United States of America', '1975-12-31'),
('trevrP@gmail.com', 'Trevor', 'Pine', 'skateislove1', 'California', 'Bakersfield', 'L Street', '1309', '6614446422', 'R19357534', '2027-04-20', 'United States of America', '1989-04-19'),
('carolk@gmail.com', 'Carol', 'King', '456654', 'New York', 'New York', 'Union Square West', '25', '9875068921', 'EH8874378', '2023-05-31', 'China', '1988-06-09');

-- --------------------------------------------------------

--
-- Table structure for table `flight`
--

CREATE TABLE `flight` (
  `flight_number` varchar(10) NOT NULL,
  `flight_status` varchar(10) DEFAULT NULL,
  `departure_date_time` varchar(20) NOT NULL,
  `airline_name` varchar(20) NOT NULL,
  `airplane_id` varchar(20) DEFAULT NULL,
  `departure_airport_code` varchar(5) DEFAULT NULL,
  `arrival_airport_code` varchar(5) DEFAULT NULL,
  `arrival_date_time` varchar(20) DEFAULT NULL,
  `base_price` decimal(6,2) DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `flight`
--

INSERT INTO `flight` (`flight_number`, `flight_status`, `departure_date_time`, `airline_name`, `airplane_id`, `departure_airport_code`, `arrival_airport_code`, `arrival_date_time`, `base_price`) VALUES
('102', 'On-time', '2022-04-01 13:27:00', 'China Eastern', 'A340-500', 'JFK', 'PVG', '2022-04-02 15:02:00', '500.00'),
('103', 'On-time', '2022-04-06 08:15:00', 'China Eastern', '747-400', 'PVG', 'JFK', '2022-04-09 02:36:00', '585.00'),
('104', 'On-time', '2022-04-12 12:00:00', 'China Eastern', '747-400', 'JFK', 'PVG', '2022-04-13 13:15:00', '650.00'),
('4588', 'Delayed', '2022-05-28', 'United', 'B777-89', 'JFK', 'SFO', '2022-04-30 21:34:56', '200.00'),
('9962', 'On-time', '2022-06-23', 'American', 'A325', 'JFK', 'BOS', '2022-06-23', '399.00'),
('8893', 'Delayed', '2022-04-13', 'American', '787-300', 'PVG', 'SFO', '2022-04-14', '899.00'),
('7349', 'On-time', '2022-02-09', 'United', '787-300', 'BOS', 'SFO', '2022-02-09', '199.00');

-- --------------------------------------------------------

--
-- Table structure for table `ratings`
--

CREATE TABLE `ratings` (
  `customer_email` varchar(50) NOT NULL,
  `flight_number` varchar(10) DEFAULT NULL,
  `rating` float DEFAULT NULL,
  `comments` tinytext
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `ratings`
--

INSERT INTO `ratings` (`customer_email`, `flight_number`, `rating`, `comments`) VALUES
('carlT@hotmail.com', '102', 4.8, 'I love it!'),
('sallyM@yahoo.com', '102', 4.2, 'It was a flight to die for.'),
('trevrP@gmail.com', '104', 3, 'Not good.'),
('sallyM@yahoo.com', '104', 4, 'Not bad!');

-- --------------------------------------------------------

--
-- Table structure for table `ticket`
--

CREATE TABLE `ticket` (
  `ticket_id` varchar(20) NOT NULL,
  `customer_email` varchar(50) DEFAULT NULL,
  `travel_class` varchar(20) DEFAULT NULL,
  `airline_name` varchar(20) DEFAULT NULL,
  `flight_number` varchar(10) DEFAULT NULL,
  `departure_date_time` datetime DEFAULT NULL,
  `sold_price` decimal(6,2) DEFAULT NULL,
  `purchase_date_time` datetime DEFAULT NULL,
  `card_type` varchar(32) DEFAULT NULL,
  `name_on_card` varchar(40) DEFAULT NULL,
  `expiration_date` date DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `ticket`
--

INSERT INTO `ticket` (`ticket_id`, `customer_email`, `travel_class`, `airline_name`, `flight_number`, `departure_date_time`, `sold_price`, `purchase_date_time`, `card_type`, `name_on_card`, `expiration_date`) VALUES
('1200546', 'carlT@hotmail.com', 'Economy Class', 'China Eastern', '102', '2022-04-01 13:27:00', '540.39', '2022-01-26 20:57:38', 'Credit', 'Carl Thorne', '2025-04-01'),
('5438554', 'sallyM@yahoo.com', 'Business Class', 'China Eastern', '104', '2022-04-12 12:00:00', '742.12', '2022-03-30 09:23:12', 'Debit', 'Sally Margarine', '2027-02-01'),
('9237545', 'trevrP@gmail.com', 'First class', 'China Eastern', '103', '2022-04-06 08:15:00', '1244.00', '2021-12-24 02:01:19', 'Debit', 'Trevor Pine', '2022-05-01'),
('7882334', 'carlT@hotmail.com', 'Economy Class', 'United', '7349', '2022-04-27 13:27:00', '733.14', '2022-04-11 18:49:30', 'Credit', 'Carl Thorne', '2024-04-01'),
('1234567', 'carlT@hotmail.com', 'First Class', 'United', '4588', '2022-05-28 19:30:00', '860.99', '2022-02-01 15:33:38', 'Credit', 'Carl Thorne', '2024-05-01'),
('7654321', 'sallyM@yahoo.com', 'Business Class', 'China Eastern', '102', '2022-04-01 13:27:00', '988.98', '2022-03-26 20:57:38', 'Credit', 'Sally Margarine', '2027-02-01'),
('2969530', 'carolk@gmail.com', 'Economy Class', 'United', '4588', '2022-05-28 00:00:00', '200.00', '2022-05-02 15:23:58', 'Credit', 'CK', '2022-07-01');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `airline`
--
ALTER TABLE `airline`
  ADD PRIMARY KEY (`airline_name`);

--
-- Indexes for table `airline_staff`
--
ALTER TABLE `airline_staff`
  ADD PRIMARY KEY (`username`),
  ADD KEY `airline_name` (`airline_name`);

--
-- Indexes for table `airline_staff_phone_number`
--
ALTER TABLE `airline_staff_phone_number`
  ADD PRIMARY KEY (`username`,`phone_number`);

--
-- Indexes for table `airplane`
--
ALTER TABLE `airplane`
  ADD PRIMARY KEY (`airplane_id`);

--
-- Indexes for table `airport`
--
ALTER TABLE `airport`
  ADD PRIMARY KEY (`airport_code`);

--
-- Indexes for table `customer`
--
ALTER TABLE `customer`
  ADD PRIMARY KEY (`email`);

--
-- Indexes for table `flight`
--
ALTER TABLE `flight`
  ADD PRIMARY KEY (`flight_number`,`departure_date_time`,`airline_name`),
  ADD KEY `airline_name` (`airline_name`),
  ADD KEY `airplane_id` (`airplane_id`),
  ADD KEY `departure_airport_code` (`departure_airport_code`,`arrival_airport_code`);

--
-- Indexes for table `ticket`
--
ALTER TABLE `ticket`
  ADD PRIMARY KEY (`ticket_id`),
  ADD KEY `customer_email` (`customer_email`),
  ADD KEY `airline_name` (`airline_name`),
  ADD KEY `flight_number` (`flight_number`,`departure_date_time`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
