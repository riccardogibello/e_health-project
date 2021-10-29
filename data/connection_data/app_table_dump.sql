CREATE DATABASE  IF NOT EXISTS `projectdatabase`;

USE `projectdatabase`;

DROP TABLE IF EXISTS `app`;
CREATE TABLE `app` (
  `app_id` varchar(100) UNIQUE NOT NULL,
  `app_name` varchar(200),
  `description` varchar(4500),
  `category_id` varchar(60),
  `score` float DEFAULT 0,
  `rating` integer DEFAULT 0,
  `developer_id` varchar(60),
  `last_update` bigint,
  `content_rating` varchar(50),
  `content_rating_description` varchar(50),
  `teacher_approved` boolean DEFAULT false,
  PRIMARY KEY (`app_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `preliminary`;
CREATE TABLE `preliminary` (
    `app_id` varchar(100) UNIQUE NOT NULL,
    `check` boolean DEFAULT false,
    `from_dataset` boolean DEFAULT false,
    PRIMARY KEY (`app_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `selected_app`;
CREATE TABLE `selected_app` (
    `app_id` varchar(100) UNIQUE NOT NULL,
    `app_name` varchar(200),
    `category_id` varchar(60),
    `score` float DEFAULT 0,
    `rating` integer DEFAULT 0,
    `developer_id` varchar(60),
    `last_update` bigint,
    `content_rating` varchar(50),
    `content_rating_description` varchar(50),
    `teacher_approved` boolean DEFAULT false,
    PRIMARY KEY (`app_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;