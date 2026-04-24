

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for camerarecords
-- ----------------------------
DROP TABLE IF EXISTS `camerarecords`;
CREATE TABLE `camerarecords`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `weight` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `conf` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `username` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `start_time` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `out_video` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `kind` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 15 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for imgrecords
-- ----------------------------
DROP TABLE IF EXISTS `imgrecords`;
CREATE TABLE `imgrecords`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `input_img` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `out_img` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `confidence` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `all_time` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `conf` decimal(5, 2) NULL DEFAULT NULL,
  `weight` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `username` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `start_time` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `label` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `ai` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `suggestion` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 941 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for user
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `sex` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `email` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `tel` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `role` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `avatar` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `time` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 6 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;
INSERT INTO `user` VALUES (1, 'admin', 'admin', '1', '男', '111111@qq.com', '353252', 'admin', 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif', '2025-03-05 16:00:27');
INSERT INTO `user` VALUES (2, '1111', '111', '111', '111', '11', '11', 'common', 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif', '2025-03-11 20:27:04');
INSERT INTO `user` VALUES (3, '222', '222', '张三', '男', '123@qq.com', '1234567889', 'common', 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif', '2025-04-24 09:45:28');
INSERT INTO `user` VALUES (4, '123', '123', '张三', '男', '123@qq.com', '1234567889', 'common', 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif', '2025-04-24 09:45:36');
INSERT INTO `user` VALUES (5, '333', '333', '张三', '男', '123@qq.com', '1234567889', 'common', 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif', '2025-04-24 09:45:40');
-- ----------------------------
-- Table structure for videorecords
-- ----------------------------
DROP TABLE IF EXISTS `videorecords`;
CREATE TABLE `videorecords`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `input_video` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `out_video` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `username` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `start_time` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `conf` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `weight` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `kind` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 24 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Procedure structure for update_camerarecords_id
-- ----------------------------
DROP PROCEDURE IF EXISTS `update_camerarecords_id`;
delimiter ;;
CREATE PROCEDURE `update_camerarecords_id`()
BEGIN
CREATE TEMPORARY TABLE temp_camerarecords AS
SELECT weight, conf, username, start_time, out_video
FROM camerarecords;
DROP TABLE camerarecords;
CREATE TABLE camerarecords(
id int(11) NOT NULL AUTO_INCREMENT,
weight varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
conf varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
username varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
start_time varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
out_video varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
PRIMARY KEY (id) USING BTREE
);
INSERT INTO camerarecords (weight, conf, username, start_time, out_video)
SELECT weight, conf, username, start_time, out_video
FROM temp_camerarecords;
DROP TEMPORARY TABLE temp_camerarecords;
END
;;
delimiter ;

-- ----------------------------
-- Procedure structure for update_imgrecords_id
-- ----------------------------
DROP PROCEDURE IF EXISTS `update_imgrecords_id`;
delimiter ;;
CREATE PROCEDURE `update_imgrecords_id`()
BEGIN
-- 临时保存表结构和数据
 CREATE TEMPORARY TABLE temp_imgrecords AS
SELECT input_img, out_img, confidence, all_time, conf, weight, username, start_time, label
FROM imgrecords;
-- 删除原表
DROP TABLE imgrecords;
-- 重新创建表
CREATE TABLE imgrecords (
id int(11) NOT NULL AUTO_INCREMENT,
input_img varchar(255) DEFAULT NULL,
out_img varchar(255) DEFAULT NULL,
confidence varchar(255) DEFAULT NULL,
all_time varchar(255) DEFAULT NULL,
conf DECIMAL(5,2) DEFAULT NULL,
weight varchar(255) DEFAULT NULL,
username varchar(255) DEFAULT NULL,
start_time varchar(255) DEFAULT NULL,
label varchar(255) DEFAULT NULL,
PRIMARY KEY (id)
);
-- 将临时表的数据插入新表
INSERT INTO imgrecords (input_img, out_img, confidence, all_time, conf, weight, username, start_time, label)
SELECT input_img, out_img, confidence, all_time, conf, weight, username, start_time, label
FROM temp_imgrecords;
-- 删除临时表
DROP TEMPORARY TABLE temp_imgrecords;
END
;;
delimiter ;

-- ----------------------------
-- Procedure structure for update_videorecords_id
-- ----------------------------
DROP PROCEDURE IF EXISTS `update_videorecords_id`;
delimiter ;;
CREATE PROCEDURE `update_videorecords_id`()
BEGIN
CREATE TEMPORARY TABLE temp_videorecords AS
SELECT input_video, out_video, username, start_time, conf, weight
FROM videorecords;
DROP TABLE videorecords;
CREATE TABLE videorecords(
id int(11) NOT NULL AUTO_INCREMENT,
input_video varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
out_video varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
username varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
start_time varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
conf varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
weight varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
PRIMARY KEY (id) USING BTREE
);
INSERT INTO videorecords (input_video, out_video, username, start_time, conf, weight)
SELECT input_video, out_video, username, start_time, conf, weight
FROM temp_videorecords;
DROP TEMPORARY TABLE temp_videorecords;
END
;;
delimiter ;

SET FOREIGN_KEY_CHECKS = 1;
