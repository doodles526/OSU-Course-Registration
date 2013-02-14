delimiter $$

CREATE DATABASE `osu_classes`;

CREATE TABLE `class_times` (
  `class_time_id` int(11) NOT NULL AUTO_INCREMENT,
  `class_id` int(11) NOT NULL,
  `term` varchar(4) NOT NULL,
  `crn` int(11) NOT NULL,
  `section` varchar(3) NOT NULL,
  `instructor` varchar(100) NOT NULL,
  `days` varchar(10) NOT NULL,
  `time_start` varchar(4) NOT NULL,
  `time_end` varchar(4) NOT NULL,
  `campus` varchar(100) NOT NULL,
  `type` varchar(10) NOT NULL,
  `cap` int(11) NOT NULL,
  `current` int(11) NOT NULL,
  `available` int(11) NOT NULL,
  `wl_cap` int(11) NOT NULL,
  `wl_current` int(11) NOT NULL,
  `wl_available` int(11) NOT NULL,
  `fees` varchar(50) NOT NULL,
  `restrictions` varchar(50) NOT NULL,
  `notes` text NOT NULL,
  `midterm_start` datetime NOT NULL,
  `midterm_end` datetime NOT NULL,
  `final_start` datetime NOT NULL,
  `final_end` datetime NOT NULL,
  PRIMARY KEY (`class_time_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1$$

CREATE TABLE `classes` (
  `class_id` int(11) NOT NULL AUTO_INCREMENT,
  `subject` varchar(5) NOT NULL,
  `level` int(3) NOT NULL,
  `level_format` varchar(3) NOT NULL,
  `short_name` varchar(6) NOT NULL,
  `full_name` varchar(150) NOT NULL,
  `description` text NOT NULL,
  PRIMARY KEY (`class_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1$$
