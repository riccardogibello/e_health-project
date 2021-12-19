DROP DATABASE `projectdatabase`;
CREATE DATABASE  IF NOT EXISTS `projectdatabase`;
USE `projectdatabase`;

DROP TABLE IF EXISTS `app`;
CREATE TABLE `app` (
  `app_id` varchar(200) UNIQUE NOT NULL,
  `app_name` varchar(200),
  `description` varchar(10000),
  `category_id` varchar(100),
  `score` float DEFAULT 0,
  `rating` integer DEFAULT 0,
  `installs` integer DEFAULT 0,
  `developer_id` varchar(200),
  `last_update` bigint,
  `content_rating` varchar(50),
  `teacher_approved` boolean DEFAULT false,
  PRIMARY KEY (`app_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `selected_app`;
CREATE TABLE `selected_app` (
  `app_id` varchar(200) UNIQUE NOT NULL,
  `app_name` varchar(200),
  `description` varchar(10000),
  `category_id` varchar(100),
  `score` float DEFAULT 0,
  `rating` integer DEFAULT 0,
  `installs` integer DEFAULT 0,
  `developer_id` varchar(200),
  `last_update` bigint,
  `content_rating` varchar(50),
  `teacher_approved` boolean DEFAULT false,
  PRIMARY KEY (`app_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `preliminary`;
CREATE TABLE `preliminary` (
    `app_id` varchar(100) UNIQUE NOT NULL,
    `check` boolean DEFAULT false,
    `from_dataset` boolean DEFAULT false,
    `existing` boolean DEFAULT true,
    PRIMARY KEY (`app_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `developer`;
CREATE TABLE `developer` (
  `id` varchar(200),
  `name` varchar (200),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `developer`;
CREATE TABLE `developer` (
  `id` varchar(100) UNIQUE NOT NULL,
  `name` varchar (200),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `app_paper`;
CREATE TABLE `app_paper` (
  `paper_id` varchar(100),
  `app_id` varchar(200),
  PRIMARY KEY (`paper_id`, `app_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `paper_keywords`;
CREATE TABLE `paper_keywords` (
  `paper_id` varchar(100),
  `keyword_id` varchar(200),
  PRIMARY KEY (`paper_id`, `keyword_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `keyword`;
CREATE TABLE `keyword` (
  `keyword_id` integer UNIQUE NOT NULL AUTO_INCREMENT,
  `keyword` varchar(200),
  `occurrences` int DEFAULT 0,
  PRIMARY KEY (`keyword_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `author_paper`;
CREATE TABLE `author_paper` (
  `author_id` integer,
  `paper_id` integer,
  PRIMARY KEY (`author_id`, `paper_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `author`;
CREATE TABLE `author` (
  `author_id` integer NOT NULL AUTO_INCREMENT,
  `name` varchar(100),
  `surname` varchar(100),
  `quotes` integer,
  `papers` integer,
  PRIMARY KEY (`author_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `paper`;
CREATE TABLE `paper` (
  `paper_id` integer NOT NULL AUTO_INCREMENT,
  `paper_title` varchar(1000),
  `abstract` varchar(10000),
  `type` varchar(100),
  `journal` varchar(1000),
  `nature_type` varchar(1000),
  PRIMARY KEY (`paper_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `test_paper`;
CREATE TABLE `test_paper` (
  `paper_id` integer NOT NULL AUTO_INCREMENT,
  `text` varchar(10000),
  `true_type` integer,
  `predicted_type` integer,
  PRIMARY KEY (`paper_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `labeled_app`;
CREATE TABLE `labeled_app` (
  `app_id` varchar(100) UNIQUE NOT NULL,
  `human_classified` boolean
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


