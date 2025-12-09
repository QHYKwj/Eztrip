CREATE TABLE user_info (
  user_id    INT UNSIGNED NOT NULL AUTO_INCREMENT,
  username   VARCHAR(255) NOT NULL,
  password   VARCHAR(255) NOT NULL,
  email      VARCHAR(255) NOT NULL,
  avatar     VARCHAR(255),
  admin_id   INT,           -- 可以继续保留用来表示管理员编号
  status     VARCHAR(255),  -- 可改成 ENUM('active','banned') 等
  PRIMARY KEY (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE trip_template (
  template_id    INT UNSIGNED NOT NULL AUTO_INCREMENT,
  title          VARCHAR(255) NOT NULL,  -- 模板名称，比如“珠海一日游模板”
  destination    VARCHAR(255) NOT NULL,  -- 目的地
  description    TEXT,                   -- 模板简介
  plan_content   TEXT,                   -- 详细行程（可以先用 TEXT，后面可以JSON）
  creator_id     INT UNSIGNED NOT NULL,  -- 创建人，一般是管理员 user_id
  created_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  is_active      TINYINT(1) NOT NULL DEFAULT 1,  -- 是否启用该模板

  PRIMARY KEY (template_id),
  CONSTRAINT fk_trip_template_creator
    FOREIGN KEY (creator_id) REFERENCES user_info(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE trip (
  trip_id        INT UNSIGNED NOT NULL AUTO_INCREMENT,
  owner_user_id  INT UNSIGNED NOT NULL,         -- 这个行程属于哪个用户
  template_id    INT UNSIGNED DEFAULT NULL,     -- 如来自模板，则记录模板id，否则NULL

  title          VARCHAR(255) NOT NULL,         -- 行程标题，例如“我的珠海一日游”
  destination    VARCHAR(255) NOT NULL,         -- 目的地
  start_date     DATE NOT NULL,
  end_date       DATE NOT NULL,

  created_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  -- 发布状态：草稿 / 待审核 / 已发布 / 未通过
  publish_status ENUM('draft','pending','published','rejected') NOT NULL DEFAULT 'draft',

  -- 审核相关（只有待审核/已发布/未通过时有意义）
  reviewed_by    INT UNSIGNED DEFAULT NULL,     -- 审核管理员 user_id
  reviewed_at    DATETIME DEFAULT NULL,
  review_comment VARCHAR(500) DEFAULT NULL,     -- 审核意见

  -- 是否对外公开（比如已发布但不一定在广场中展示，可控制）
  is_public      TINYINT(1) NOT NULL DEFAULT 1,

  PRIMARY KEY (trip_id),
  CONSTRAINT fk_trip_owner
    FOREIGN KEY (owner_user_id) REFERENCES user_info(user_id),
  CONSTRAINT fk_trip_template
    FOREIGN KEY (template_id) REFERENCES trip_template(template_id),
  CONSTRAINT fk_trip_reviewer
    FOREIGN KEY (reviewed_by) REFERENCES user_info(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE trip_favorite (
  user_id    INT UNSIGNED NOT NULL,        -- 收藏者
  trip_id    INT UNSIGNED NOT NULL,        -- 被收藏的行程
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (user_id, trip_id),
  CONSTRAINT fk_fav_user
    FOREIGN KEY (user_id) REFERENCES user_info(user_id),
  CONSTRAINT fk_fav_trip
    FOREIGN KEY (trip_id) REFERENCES trip(trip_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE notice (
  notice_id    INT UNSIGNED NOT NULL AUTO_INCREMENT,
  title        VARCHAR(255) NOT NULL,
  content      TEXT NOT NULL,
  created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by   INT UNSIGNED NOT NULL,          -- 发布管理员 user_id
  is_active    TINYINT(1) NOT NULL DEFAULT 1,  -- 是否有效（可以软删除）

  PRIMARY KEY (notice_id),
  CONSTRAINT fk_notice_creator
    FOREIGN KEY (created_by) REFERENCES user_info(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE notice (
                        notice_id    INT UNSIGNED NOT NULL AUTO_INCREMENT,
                        title        VARCHAR(255) NOT NULL,
                        content      TEXT NOT NULL,
                        created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        created_by   INT UNSIGNED NOT NULL,          -- 发布管理员 user_id
                        is_active    TINYINT(1) NOT NULL DEFAULT 1,  -- 是否有效（可以软删除）

                        PRIMARY KEY (notice_id),
                        CONSTRAINT fk_notice_creator
                            FOREIGN KEY (created_by) REFERENCES user_info(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE message (
                         message_id   INT UNSIGNED NOT NULL AUTO_INCREMENT,
                         sender_id    INT UNSIGNED NOT NULL,   -- 发送者（通常是管理员，但设计成任意用户也行）
                         receiver_id  INT UNSIGNED NOT NULL,   -- 接收者（具体某个用户）
                         title        VARCHAR(255) DEFAULT NULL, -- 可有可无
                         content      TEXT NOT NULL,
                         created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                         is_read      TINYINT(1) NOT NULL DEFAULT 0,  -- 是否已读
                         read_at      DATETIME DEFAULT NULL,

                         PRIMARY KEY (message_id),
                         CONSTRAINT fk_message_sender
                             FOREIGN KEY (sender_id) REFERENCES user_info(user_id),
                         CONSTRAINT fk_message_receiver
                             FOREIGN KEY (receiver_id) REFERENCES user_info(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
