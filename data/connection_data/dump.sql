
CREATE DATABASE  IF NOT EXISTS `projectdatabase`;

USE `projectdatabase`;

DROP TABLE IF EXISTS `app`;
CREATE TABLE `app` (
  `app_id` varchar(100) UNIQUE NOT NULL,
  `app_name` varchar(200),
  `description` varchar(4500),
  `category` varchar(45),
  `score` varchar(45),
  `rating` varchar(45),
  `reviews` varchar(45),
  `content_rating` varchar(45),
  `genres` varchar(45),
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