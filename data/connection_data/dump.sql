CREATE DATABASE  IF NOT EXISTS `projectdatabase`;

USE `projectdatabase`;

DROP TABLE IF EXISTS `app_word_occurrences`;
CREATE TABLE `app_word_occurrences` (
  `app_id` varchar(100) NOT NULL,
  `app_name` varchar(200),
  `word` varchar(200),
  `occurrences` int,
  PRIMARY KEY (`app_id`, `word`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*DROP TABLE IF EXISTS `labeled_app`;
CREATE TABLE `labeled_app` (
  `app_id` varchar(100) UNIQUE NOT NULL,
  `machine_classified` boolean,
  `human_classified` boolean
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;*/

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
  `category_id` varchar(30),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*DROP TABLE IF EXISTS `review`;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;*/