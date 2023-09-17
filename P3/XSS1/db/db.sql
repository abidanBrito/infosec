-- MySQL Script generated by MySQL Workbench
-- Tue 17 Oct 2017 15:19:37 CEST
-- Model: New Model    Version: 1.0
-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema INFOSEC_DB
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `INFOSEC_DB` ;

-- -----------------------------------------------------
-- Schema INFOSEC_DB
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `INFOSEC_DB` DEFAULT CHARACTER SET utf8 ;
SHOW WARNINGS;
USE `INFOSEC_DB` ;

-- -----------------------------------------------------
-- Table `INFOSEC_DB`.`user`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `INFOSEC_DB`.`user` ;

SHOW WARNINGS;
CREATE TABLE IF NOT EXISTS `INFOSEC_DB`.`user` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `role` ENUM('admin', 'user') NOT NULL DEFAULT 'user',
  `username` VARCHAR(64) NOT NULL,
  `password_hash` VARCHAR(64) NOT NULL,
  `password_salt` VARCHAR(64) NOT NULL,
  `creation_time` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `username_UNIQUE` (`username` ASC))
ENCRYPTION = 'Y',
ENGINE = InnoDB;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `INFOSEC_DB`.`session`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `INFOSEC_DB`.`session` ;

SHOW WARNINGS;
CREATE TABLE IF NOT EXISTS `INFOSEC_DB`.`session` (
  `id` VARCHAR(64) NOT NULL,
  `user_id` INT NOT NULL,
  `csrf_token` VARCHAR(64) NOT NULL,
  `timestamp` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `fk_session_1_idx` (`user_id` ASC),
  CONSTRAINT `fk_session_1`
    FOREIGN KEY (`user_id`)
    REFERENCES `INFOSEC_DB`.`user` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENCRYPTION = 'Y',
ENGINE = InnoDB;

SHOW WARNINGS;
USE `INFOSEC_DB` ;

-- -----------------------------------------------------
-- Table `INFOSEC_DB`.`post`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `INFOSEC_DB`.`post` ;

SHOW WARNINGS;
CREATE TABLE IF NOT EXISTS `INFOSEC_DB`.`post` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `text` TEXT NULL,
  `timestamp` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `fk_post_1_idx` (`user_id` ASC),
  CONSTRAINT `fk_post_1`
    FOREIGN KEY (`user_id`)
    REFERENCES `INFOSEC_DB`.`user` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENCRYPTION = 'Y',
ENGINE = InnoDB;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `INFOSEC_DB`.`flags`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `INFOSEC_DB`.`flags` ;

SHOW WARNINGS;
CREATE TABLE IF NOT EXISTS `INFOSEC_DB`.`flags` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `flag` VARCHAR(36) NOT NULL,
  PRIMARY KEY (`id`))
ENCRYPTION = 'Y',
ENGINE = InnoDB;

SHOW WARNINGS;

-- -----------------------------------------------------
-- procedure purge_sessions
-- -----------------------------------------------------

USE `INFOSEC_DB`;
DROP procedure IF EXISTS `INFOSEC_DB`.`purge_sessions`;
SHOW WARNINGS;

DELIMITER $$
USE `INFOSEC_DB`$$
CREATE PROCEDURE `purge_sessions` (IN t INT)
BEGIN
	DELETE FROM `session` WHERE `timestamp` < (NOW() - INTERVAL t MINUTE);
END$$

DELIMITER ;
SHOW WARNINGS;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

-- -----------------------------------------------------
-- USER privileges
-- -----------------------------------------------------

DROP USER 'db_user'@'%';
CREATE USER 'db_user'@'%' IDENTIFIED BY 'Super_Secure_INFOSEC21_!?';

GRANT USAGE ON `INFOSEC_DB`.* TO 'db_user'@'%';
GRANT SELECT,INSERT,DELETE,UPDATE ON `INFOSEC_DB`.`user` TO 'db_user'@'%';
GRANT SELECT,INSERT,DELETE,UPDATE ON `INFOSEC_DB`.`post` TO 'db_user'@'%';
GRANT SELECT,INSERT,DELETE,UPDATE ON `INFOSEC_DB`.`session` TO 'db_user'@'%';
GRANT SELECT,INSERT,DELETE,UPDATE ON `INFOSEC_DB`.`flags` TO 'db_user'@'%';
GRANT EXECUTE ON PROCEDURE `INFOSEC_DB`.`purge_sessions` TO 'db_user'@'%';
FLUSH PRIVILEGES;
