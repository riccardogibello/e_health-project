CREATE DATABASE  IF NOT EXISTS `projectdatabase`;

USE `projectdatabase`;

DROP TABLE IF EXISTS `app_features`;
CREATE TABLE `app_features` (
  `app_id` varchar(100) UNIQUE NOT NULL,
  `serious_words_count` int DEFAULT 0,
  `teacher_approved` boolean DEFAULT false,
  `score` float,
  `rating` integer,
  `category_id` integer,
  `human_classified` boolean,
  `machine_classified` boolean
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;