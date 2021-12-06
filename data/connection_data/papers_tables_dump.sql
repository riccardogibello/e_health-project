CREATE DATABASE  IF NOT EXISTS `projectdatabase`;

USE `projectdatabase`;

DROP TABLE IF EXISTS `developer`;
CREATE TABLE `developer` (
  `id` varchar(100) UNIQUE NOT NULL,
  `name` varchar (200),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `developer_paper`;
CREATE TABLE `developer_paper` (
  `developer_id` varchar(100),
  `paper_id` varchar(200),
  PRIMARY KEY (`developer_id`, `paper_id`)
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
  `keyword` varchar(200),
  PRIMARY KEY (`paper_id`, `keyword`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `author_paper`;
CREATE TABLE `author_paper` (
  `author_name` varchar(100),
  `author_surname` varchar(100),
  `paper_id` varchar(200),
  PRIMARY KEY (`author_name`, `author_surname`, `paper_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `author`;
CREATE TABLE `author` (
  `name` varchar(100),
  `surname` varchar(100),
  `quotes` integer,
  `papers` integer,
  PRIMARY KEY (`name`, `surname`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `paper`;
CREATE TABLE `paper` (
  `paper_id` integer NOT NULL AUTO_INCREMENT,
  `paper_title` varchar(1000),
  `abstract` varchar(10000),
  `type` varchar(100),
  `pubmed_id` integer,
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

