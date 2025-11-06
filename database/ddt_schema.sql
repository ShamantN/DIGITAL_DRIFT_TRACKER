-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: localhost    Database: ddt
-- ------------------------------------------------------
-- Server version	8.0.43

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `activity_event`
--

DROP TABLE IF EXISTS `activity_event`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `activity_event` (
  `event_id` int NOT NULL AUTO_INCREMENT,
  `session_id` int NOT NULL,
  `user_id` int NOT NULL,
  `tab_id` int NOT NULL,
  `event_type` enum('MOUSE_MOVE','CLICK','SCROLL','KEY_PRESS','TAB_FOCUS','TAB_UNFOCUS','URL_CHANGE') NOT NULL,
  `timestamp` timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `url` varchar(2083) DEFAULT NULL,
  `mouse_x` int DEFAULT NULL,
  `mouse_y` int DEFAULT NULL,
  `scroll_y_pixels` int DEFAULT NULL,
  `scroll_y_percent` float DEFAULT NULL,
  `target_element_id` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`event_id`),
  KEY `fk_act_to_user` (`user_id`),
  KEY `fk_act_to_session` (`session_id`),
  KEY `fk_act_to_tab` (`tab_id`),
  CONSTRAINT `fk_act_to_session` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`sid`) ON DELETE CASCADE,
  CONSTRAINT `fk_act_to_tab` FOREIGN KEY (`tab_id`) REFERENCES `tab` (`tid`),
  CONSTRAINT `fk_act_to_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`uid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `domains`
--

DROP TABLE IF EXISTS `domains`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `domains` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `domain_name` varchar(255) NOT NULL,
  `favicon_url` varchar(2083) DEFAULT NULL,
  `category` enum('Productive','Unproductive','Neutral','Social Media','Entertainment') NOT NULL DEFAULT 'Neutral',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_user_domain` (`user_id`,`domain_name`),
  CONSTRAINT `fk_domains_to_users` FOREIGN KEY (`user_id`) REFERENCES `user` (`uid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `drift_event`
--

DROP TABLE IF EXISTS `drift_event`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `drift_event` (
  `drift_id` int NOT NULL AUTO_INCREMENT,
  `session_id` int NOT NULL,
  `event_start` timestamp NOT NULL,
  `event_end` timestamp NOT NULL,
  `duration_seconds` int DEFAULT NULL,
  `drift_type` varchar(60) DEFAULT NULL,
  `description` varchar(150) DEFAULT NULL,
  `severity` enum('NEGLIGIBLE','VERY LOW','LOW','MODERATE','HIGH','VERY HIGH') NOT NULL,
  PRIMARY KEY (`drift_id`),
  KEY `fk_drift_to_session` (`session_id`),
  CONSTRAINT `fk_drift_to_session` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`sid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `drift_involves_tab`
--

DROP TABLE IF EXISTS `drift_involves_tab`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `drift_involves_tab` (
  `tab_id` int NOT NULL,
  `drift_id` int NOT NULL,
  PRIMARY KEY (`tab_id`,`drift_id`),
  KEY `fk_dit_to_drift` (`drift_id`),
  CONSTRAINT `fk_dit_to_drift` FOREIGN KEY (`drift_id`) REFERENCES `drift_event` (`drift_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_dit_to_tab` FOREIGN KEY (`tab_id`) REFERENCES `tab` (`tid`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sessions`
--

DROP TABLE IF EXISTS `sessions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sessions` (
  `sid` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `start_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `end_time` timestamp NULL DEFAULT NULL,
  `browser_name` varchar(50) NOT NULL,
  `browser_version` varchar(50) NOT NULL,
  `platform` varchar(50) NOT NULL COMMENT 'browser_name, browser_version, platform is a comp attr. duration is a derived attr',
  PRIMARY KEY (`sid`),
  KEY `fk_sessions_to_users` (`user_id`),
  CONSTRAINT `fk_sessions_to_users` FOREIGN KEY (`user_id`) REFERENCES `user` (`uid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tab`
--

DROP TABLE IF EXISTS `tab`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tab` (
  `tid` int NOT NULL AUTO_INCREMENT,
  `session_id` int NOT NULL,
  `domain_id` int NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `url` varchar(200) DEFAULT NULL COMMENT 'Domain field can be derived from url',
  `title` varchar(100) DEFAULT NULL,
  `opened_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `closed_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`tid`),
  KEY `fk_tab_to_session` (`session_id`),
  KEY `fk_tab_to_domain` (`domain_id`),
  CONSTRAINT `fk_tab_to_domain` FOREIGN KEY (`domain_id`) REFERENCES `domains` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_tab_to_session` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`sid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `uid` int NOT NULL AUTO_INCREMENT,
  `email` varchar(100) NOT NULL,
  `user_name` varchar(50) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `timezone` varchar(50) NOT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `whitelists`
--

DROP TABLE IF EXISTS `whitelists`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `whitelists` (
  `wid` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `domain_id` int NOT NULL,
  `user_reason` varchar(200) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`wid`),
  UNIQUE KEY `unique_user_whitelist` (`user_id`,`domain_id`),
  KEY `fk_white_to_domain` (`domain_id`),
  CONSTRAINT `fk_white_to_domain` FOREIGN KEY (`domain_id`) REFERENCES `domains` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_white_to_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`uid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;



CREATE TABLE `daily_domain_summary` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `domain_id` INT NOT NULL,
  `summary_date` DATE NOT NULL,
  `total_seconds_focused` INT DEFAULT 0,
  `total_events` INT DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_domain_date` (`user_id`, `domain_id`, `summary_date`),
  FOREIGN KEY (`user_id`) REFERENCES `user` (`uid`) ON DELETE CASCADE,
  FOREIGN KEY (`domain_id`) REFERENCES `domains` (`id`) ON DELETE CASCADE
);

/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-10-24  8:32:52
