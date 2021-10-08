
CREATE DATABASE  IF NOT EXISTS `projectdatabase`;

USE `projectdatabase`;



--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;

CREATE TABLE `user` (
  `userid` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `surname` varchar(45) NOT NULL,
  `username` varchar(45) NOT NULL,
  `password` varchar(45) NOT NULL,
  PRIMARY KEY (`userid`)
) ENGINE=InnoDB AUTO_INCREMENT=101 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `app`;

CREATE TABLE `app` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app` varchar(100),
  `category` varchar(45),
  `rating` varchar(10),
  `reviews` varchar(10),
  `size` varchar(10),
  `installs` varchar(15),
  `type` varchar(45),
  `price` varchar(10),
  `content_rating` varchar(45),
  `genres` varchar(45),
  `last_updated` varchar(45),
  `current_ver` varchar(45),
  `android_ver` varchar(45),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=101 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `category`;
CREATE TABLE `category` (
  `id` int NOT NULL AUTO_INCREMENT,
  `category_name` varchar(30) NOT NULL,
  `category_id` varchar(30) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=101 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;