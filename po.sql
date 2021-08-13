/*
SQLyog Ultimate v12.09 (64 bit)
MySQL - 5.5.40 : Database - po_evolution_platform
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`po_evolution_platform` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `po_evolution_platform`;

/*Table structure for table `datas` */

DROP TABLE IF EXISTS `datas`;

CREATE TABLE `datas` (
  `dataname` varchar(100) NOT NULL,
  `user` varchar(100) NOT NULL,
  `data_path` varchar(200) NOT NULL,
  `role_id` int(11) NOT NULL DEFAULT '1',
  PRIMARY KEY (`dataname`,`user`),
  KEY `datas_users_fk` (`user`),
  KEY `datas_roles_fk` (`role_id`),
  CONSTRAINT `datas_roles_fk` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`),
  CONSTRAINT `datas_users_fk` FOREIGN KEY (`user`) REFERENCES `users` (`USER`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Data for the table `datas` */

insert  into `datas`(`dataname`,`user`,`data_path`,`role_id`) values ('Wiki','supreme','F:Gitinfdiffusionstaticdataupload2020_12_01_10_43_34_535905.txt',1),('Wiki1','supreme','F:Gitinfdiffusionstaticdataupload2020_12_01_11_25_56_122544.txt',1),('新建文本文档','supreme','F:Gitinfdiffusionstaticdataupload2020_12_01_11_16_47_175149.txt',1);

/*Table structure for table `roles` */

DROP TABLE IF EXISTS `roles`;

CREATE TABLE `roles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `NAME` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `NAME` (`NAME`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

/*Data for the table `roles` */

insert  into `roles`(`id`,`NAME`) values (2,'admin'),(1,'common');

/*Table structure for table `users` */

DROP TABLE IF EXISTS `users`;

CREATE TABLE `users` (
  `USER` varchar(100) NOT NULL,
  `PASSWORD` varchar(100) NOT NULL,
  `number` varchar(20) DEFAULT NULL,
  `mail` varchar(50) NOT NULL,
  `unit` varchar(50) DEFAULT NULL,
  `role_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`USER`),
  UNIQUE KEY `USER` (`USER`),
  KEY `roles_users_fk` (`role_id`),
  CONSTRAINT `roles_users_fk` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Data for the table `users` */

insert  into `users`(`USER`,`PASSWORD`,`number`,`mail`,`unit`,`role_id`) values ('supreme','e10adc3949ba59abbe56e057f20f883e','','1830601430@qq.com','',1),('supreme1','e10adc3949ba59abbe56e057f20f883e','','1830601430@qq.com','',1),('supreme5','1c1cd8203eb2dc2a34bbfafd7919133b','','1830601430@qq.com','',1);

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
