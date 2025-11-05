/*
CREATE DATABASE EzTrip;
USE EzTrip;
*/

#DROP TABLE IF EXISTS user_info

CREATE TABLE user_info
(
	user_id INT(11) NOT NULL AUTO_INCREMENT COMMENT'用户唯一编号，主键，系统自增',#
	username VARCHAR(30) NOT NULL COMMENT'用户名，账号',# 字母，数字，下划线
	password VARCHAR(64) NOT NULL COMMENT'登录密码，与账号唯一对应',
	avatar VARCHAR(255) DEFAULT NULL COMMENT'用户头像URL',
	email VARCHAR(50) NOT NULL COMMENT'用户邮箱，验证登录与发送通知', # @xx.com
	admin_id int(11) UNIQUE DEFAULT NULL COMMENT'管理员唯一标识，与user_id对应',
	status TINYINT NOT NULL DEFAULT -1 COMMENT'游客为-1,普通用户为0，管理员为1',
	PRIMARY KEY (user_id),
	UNIQUE KEY idx_username (username),
	UNIQUE KEY idx_email (email),
	CONSTRAINT ck_email_format CHECK (email REGEXP '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'),
  CONSTRAINT ck_username_format CHECK (username REGEXP '^[a-zA-Z0-9_]+$')#保证账号只包含字母，数字，下划线
)ENGINE=INNODB DEFAULT CHARSET=utf8mb4 COMMENT'用户表';


CREATE TABLE trip
(
  trip_id INT(11) NOT NULL AUTO_INCREMENT COMMENT '行程唯一标识，主键',
  trip_name VARCHAR(100) NOT NULL COMMENT '行程名，非空',
  destination VARCHAR(50) NOT NULL COMMENT '行程目的地，非空',
  start_date DATE NOT NULL COMMENT '行程开始时间',
  end_date DATE NOT NULL COMMENT '行程结束时间',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '行程创建时间点，自动生成',
	is_collect TINYINT NOT NULL DEFAULT 0 COMMENT'行程是否被收藏,1表示已收藏',
  ai_plan TEXT COMMENT '系统生成的行程文本，可为空',
  PRIMARY KEY (trip_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='行程信息表';


CREATE TABLE notice
(
	notice_id INT(11) NOT NULL AUTO_INCREMENT COMMENT'公告消息唯一标识，主键自增',
	notice_title VARCHAR(100) NOT NULL COMMENT'公告标题',
	notice_content TEXT NOT NULL COMMENT'公告内容',
	PRIMARY KEY(notice_id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='公告表';


CREATE TABLE message
(
  message_id INT(11) NOT NULL AUTO_INCREMENT COMMENT'消息表唯一标识，主键自增',
	message_content TEXT NOT NULL COMMENT'消息内容',
	user_id INT(11) NOT NULL COMMENT'与用户表关联的外键',
	PRIMARY KEY(message_id),
	#与用户表建立外键约束
	CONSTRAINT fk_message_user FOREIGN KEY(user_id) REFERENCES user_info(user_id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='消息表';


CREATE TABLE template
(
  template_id INT(11) NOT NULL AUTO_INCREMENT COMMENT'行程模版唯一标识，主键自增',
	template_content TEXT NOT NULL COMMENT'模板内容',
	PRIMARY KEY(template_id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='行程模板表';