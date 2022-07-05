-- phpMyAdmin SQL Dump
-- version 4.7.4
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: APRIL 11, 2021 
-- Server version: 10.1.30-MariaDB
-- PHP Version: 7.2.1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `scs`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE `admin` (
  `admin_id` int NOT NULL,
  `name` varchar(50) NOT NULL,
  `surname` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(50) NOT NULL,
  `mobile number` bigint NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


--
-- Dumping data for table `admin`
--

INSERT INTO `admin` (`admin_id`, `email`, `password`, `mobile number`, `name`, `surname`) VALUES
(1, 'admin@gmail.com', 'admin@1A%&', 1234567095, 'Chandramani', 'Kumar'),
(2, 'admin1@gmail.com', 'admin1#2D%$', 3124567893, 'Singhal', 'Oberoi');

--
-- Table structure for table `jobseeker`
--

CREATE TABLE `jobseeker` (
  `jobseeker_id` int NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `phone_number` bigint NOT NULL,
  `address` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(50) NOT NULL,
  `status` varchar(2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- --------------------------------------------------------

--
-- Table structure for table `profile`
--

CREATE TABLE `profile` (
  `profile_id` int NOT NULL,
  `college` varchar(50) NOT NULL,
  `department` varchar(50) NOT NULL,
  `education` varchar(60) NOT NULL,
  `jobseeker_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- --------------------------------------------------------

--
-- Table structure for table `resume`
--

CREATE TABLE `resume` (
  `resume_id` int NOT NULL,
  `filename` varchar(501) NOT NULL,
  `jobseeker_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Table structure for table `interview`
--

CREATE TABLE `interview` (
  `interview_num` int NOT NULL,
  `job_id` int NOT NULL,
  `date` date NOT NULL,
  `time` time NOT NULL,
  `jobseeker_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


--
-- Table structure for table `apply`
--

CREATE TABLE `apply` (
  `jobseeker_id` int NOT NULL,
  `job_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


--
-- Table structure for table `result`
--

CREATE TABLE `result` (
  `result_id` int NOT NULL,
  `jobseeker_id` int NOT NULL,
  `job_id` int NOT NULL,
  `status` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


--
-- Table structure for table `job`
--

CREATE TABLE `job` (
  `job_id` int NOT NULL,
  `company_id` int NOT NULL,
  `job_title` varchar(70) NOT NULL,
  `job_type` varchar(70) NOT NULL,
  `job_description` varchar(1001) NOT NULL,
  `job_salary` bigint NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `job` (`job_id`, `company_id`, `job_title`, `job_type`, `job_description`, `job_salary`) VALUES
(1, 1, 'studenttrainee', 'se', 'fgdfgfgfggf', '32444'),
(2, 2, 'fte', 'data eng', 'tgertet', '23423'),
(3, 3, 'intern', 'security eng', 'kjkjhlklk', '13453'),
(4, 4, 'summerintern', 'automation eng', 'nvncmbcc', '34321');
--
-- Table structure for table `company`
--

CREATE TABLE `company` (
  `company_id` int NOT NULL,
  `name` varchar(50) NOT NULL,
  `location` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `company` (`company_id` , `name`, `location`) VALUES
(1,'sams','bengaluru'),
(2,'asd','klkta'),
(3,'atl','engln'),
(4,'cres','dljh');
-- --------------------------------------------------------

--
-- Indexes for dumped tables
--

--
-- Indexes for table `jobseeker`
--
ALTER TABLE `jobseeker`
  ADD PRIMARY KEY (`jobseeker_id`);

--
-- Indexes for table `profile`
--
ALTER TABLE `profile`
  ADD PRIMARY KEY (`profile_id`),
  ADD KEY `jobseeker_id` (`jobseeker_id`);

--
-- Indexes for table `resume`
--
ALTER TABLE `resume`
  ADD PRIMARY KEY (`resume_id`),
  ADD KEY `jobseeker_id` (`jobseeker_id`);

--
-- Indexes for table `interview`
--
ALTER TABLE `interview`
  ADD PRIMARY KEY (`interview_num`),
  ADD KEY `job_id` (`job_id`),
  ADD KEY `jobseeker_id` (`jobseeker_id`);

--
-- Indexes for table `apply`
--
ALTER TABLE `apply`
  ADD KEY `jobseeker_id` (`jobseeker_id`),
  ADD KEY `job_id` (`job_id`);

--
-- Indexes for table `result`
--
ALTER TABLE `result`
  ADD PRIMARY KEY (`result_id`),
  ADD KEY `jobseeker_id` (`jobseeker_id`),
  ADD KEY `job_id` (`job_id`);

--
-- Indexes for table `job`
--
ALTER TABLE `job`
  ADD PRIMARY KEY (`job_id`),
  ADD KEY `company_id` (`company_id`);

--
-- Indexes for table `company`
--
ALTER TABLE `company`
  ADD PRIMARY KEY (`company_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `jobseeker`
--
ALTER TABLE `jobseeker`
  MODIFY `jobseeker_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;

--
-- AUTO_INCREMENT for table `profile`
--
ALTER TABLE `profile`
  MODIFY `profile_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;

--
-- AUTO_INCREMENT for table `resume`
--
ALTER TABLE `resume`
  MODIFY `resume_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;

--
-- AUTO_INCREMENT for table `interview`
--
ALTER TABLE `interview`
  MODIFY `interview_num` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;

--
-- AUTO_INCREMENT for table `result`
--
ALTER TABLE `result`
  MODIFY `result_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;

--
-- AUTO_INCREMENT for table `job`
--
ALTER TABLE `job`
  MODIFY `job_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;

--
-- AUTO_INCREMENT for table `company`
--
ALTER TABLE `company`
  MODIFY `company_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;
--
-- Constraints for dumped tables
--

--
-- Constraints for table `profile`
--
ALTER TABLE `profile`
  ADD CONSTRAINT `profile_pf1` FOREIGN KEY (`jobseeker_id`) REFERENCES `jobseeker` (`jobseeker_id`) ON DELETE CASCADE;

--
-- Constraints for table `resume`
--
ALTER TABLE `resume`
  ADD CONSTRAINT `resume_pf1` FOREIGN KEY (`jobseeker_id`) REFERENCES `jobseeker` (`jobseeker_id`) ON DELETE CASCADE;

--
-- Constraints for table `interview`
--
ALTER TABLE `interview`
  ADD CONSTRAINT `interview_pf1` FOREIGN KEY (`job_id`) REFERENCES `job` (`job_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `interview_pf2` FOREIGN KEY (`jobseeker_id`) REFERENCES `jobseeker` (`jobseeker_id`) ON DELETE CASCADE;

--
-- Constraints for table `apply`
--
ALTER TABLE `apply`
  ADD CONSTRAINT `apply_pf1` FOREIGN KEY (`job_id`) REFERENCES `job` (`job_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `apply_pf2` FOREIGN KEY (`jobseeker_id`) REFERENCES `jobseeker` (`jobseeker_id`) ON DELETE CASCADE;

--
-- Constraints for table `result`
--
ALTER TABLE `result`
  ADD CONSTRAINT `result_pf1` FOREIGN KEY (`job_id`) REFERENCES `job` (`job_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `result_pf2` FOREIGN KEY (`jobseeker_id`) REFERENCES `jobseeker` (`jobseeker_id`) ON DELETE CASCADE;

--
-- Constraints for table `job`
--
ALTER TABLE `job`
  ADD CONSTRAINT `job_pf1` FOREIGN KEY (`company_id`) REFERENCES `company` (`company_id`) ON DELETE CASCADE;
 
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
