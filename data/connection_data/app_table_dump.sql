CREATE DATABASE  IF NOT EXISTS `projectdatabase`;

USE `projectdatabase`;

DROP TABLE IF EXISTS `app`;
CREATE TABLE `app` (
  `app_id` varchar(100) UNIQUE NOT NULL,
  `app_name` varchar(200),
  `description` varchar(4500),
  `category` varchar(30),
  `score` float,
  `rating` integer,
  `category_id` varchar(60),
  `developer_id` varchar(60),
  `teacher_approved` boolean DEFAULT false,
  PRIMARY KEY (`app_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;