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

DROP TABLE IF EXISTS `app_features`;
CREATE TABLE `app_features` (
  `app_id` varchar(100) UNIQUE NOT NULL,
  `serious_words_count` int DEFAULT 0,
  `teacher_approved` boolean DEFAULT false,
  `score` float,
  `rating` integer,
  `is_serious_game` boolean DEFAULT false,
  `machine_classification` boolean DEFAULT false
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `app_word_occurrences`;
CREATE TABLE `app_word_occurrences` (
  `app_id` varchar(100) NOT NULL,
  `app_name` varchar(200),
  `word` varchar(200),
  `occurrences` int,
  PRIMARY KEY (`app_id`, `word`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `labeled_app`;
CREATE TABLE `labeled_app` (
  `app_id` varchar(100) UNIQUE NOT NULL,
  `machine_classified` boolean,
  `human_classified` boolean
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `preliminary`;
CREATE TABLE `preliminary` (
    `app_id` varchar(100) UNIQUE NOT NULL,
    `check` boolean DEFAULT false,
    `from_dataset` boolean DEFAULT false,
    PRIMARY KEY (`app_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `category`;
CREATE TABLE `category` (
  `id` int NOT NULL AUTO_INCREMENT,
  `category_name` varchar(30),
  `category_id` varchar(30),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `review`;
CREATE TABLE `review` (
  `app_id` varchar(100) NOT NULL,
  `review` varchar(1000),
  PRIMARY KEY (`app_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `discarded_app`;
CREATE TABLE `discarded_app` (
  `app_id` varchar(100) UNIQUE NOT NULL,
  `description` varchar(4500),
  PRIMARY KEY (`app_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;