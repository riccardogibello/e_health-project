CREATE DATABASE  IF NOT EXISTS `projectdatabase`;

USE `projectdatabase`;

DROP TABLE IF EXISTS `paper_app`;
CREATE TABLE `paper_app` (
  `app_id` varchar(100) NOT NULL,
  `paper_id` varchar(100) NOT NULL,
  PRIMARY KEY (`app_id`, `paper_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `paper`;
CREATE TABLE `paper` (
  `paper_id` varchar(100) UNIQUE NOT NULL,
  `title` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;