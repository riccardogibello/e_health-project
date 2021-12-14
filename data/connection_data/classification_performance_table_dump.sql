CREATE DATABASE  IF NOT EXISTS `projectdatabase`;

USE `projectdatabase`;

DROP TABLE IF EXISTS `classification_performance`;
CREATE TABLE `classification_performance` (
  `model_id` integer,
  `iteration` integer,
  `recall` float,
  `accuracy` float,
  `precision` float,
  `f1_score` float,
  `true_positive` integer,
  `true_negative` integer,
  `false_positive` integer,
  `false_negative` integer,
  PRIMARY KEY (`model_id`, `iteration`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;