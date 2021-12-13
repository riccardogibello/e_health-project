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
  `machine_classified` boolean,
  PRIMARY KEY (`app_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `selected_app`;
CREATE TABLE `selected_app` (
  `app_id` varchar(100) UNIQUE NOT NULL,
  `app_name` varchar(200),
  `description` varchar(10000),
  `category_id` varchar(60),
  `score` float DEFAULT 0,
  `rating` integer DEFAULT 0,
  `installs` integer DEFAULT 0,
  `developer_id` varchar(70),
  `last_update` bigint,
  `content_rating` varchar(100),
  `teacher_approved` boolean DEFAULT false,
  PRIMARY KEY (`app_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;