INSERT INTO user_info (user_id, username, password, email, avatar, admin_id, status)
VALUES
(1, 'admin', '123456', 'admin@example.com', NULL, 1001, 'active'),   -- 管理员
(2, 'wj', '123456', 'wj@example.com', NULL, NULL, 'active'),         -- 普通用户 wj
(3, 'abc', '123456', 'abc@example.com', NULL, NULL, 'active');       -- 普通用户 abc

INSERT INTO trip_template (template_id, title, destination, description, plan_content, creator_id)
VALUES
(1, '珠海一日游模版', '珠海', '经典珠海一日游路线', 'day1: 情侣路 → 渔女像 → 拱北口岸', 1),
(2, '南京两日游模版', '南京', '适合第一次到南京的行程', 'day1: 中山陵 → 明孝陵; day2: 夫子庙 → 秦淮河', 1);
INSERT INTO trip (
  trip_id, owner_user_id, template_id, title, destination, start_date, end_date,
  publish_status, is_public, reviewed_by, reviewed_at, review_comment
)
VALUES
-- trip 1 : wj 根据模板1创建并已发布
(1, 2, 1, '我的珠海一日游', '珠海', '2025-01-10', '2025-01-10',
 'published', 1, 1, NOW(), '审核通过'),

-- trip 2 : wj 自己写的行程，正在等待审核
(2, 2, NULL, '周末深圳游', '深圳', '2025-01-20', '2025-01-21',
 'pending', 0, NULL, NULL, NULL),

-- trip 3 : abc 的行程，但审核失败
(3, 3, NULL, '广州欢乐谷一日游', '广州', '2025-02-01', '2025-02-01',
 'rejected', 0, 1, NOW(), '行程内容不完整'),

-- trip 4 : abc 从模板2创建的行程（草稿）
(4, 3, 2, '我的南京两日游计划', '南京', '2025-03-01', '2025-03-02',
 'draft', 0, NULL, NULL, NULL),

-- trip 5 : 管理员公开发布的行程
(5, 1, NULL, '管理员示例行程—澳门三日游', '澳门', '2025-04-01', '2025-04-03',
 'published', 1, 1, NOW(), '审核自动通过');
INSERT INTO trip_favorite (user_id, trip_id, created_at)
VALUES
(2, 5, NOW()),   -- wj 收藏管理员行程
(3, 1, NOW()),   -- abc 收藏 wj 的已发布行程
(2, 3, NOW());   -- wj 收藏 abc 的行程（测试数据）
INSERT INTO notice (notice_id, title, content, created_by)
VALUES
(1, '系统维护公告', '系统将于2025-01-15进行维护，请提前保存数据。', 1),
(2, '春节活动开启', '春节期间将上线行程抽奖活动，欢迎参与！', 1);
INSERT INTO message (message_id, sender_id, receiver_id, title, content, is_read)
VALUES
(1, 1, 2, '行程审核通知', '你的“我的珠海一日游”已经审核通过！', 0),
(2, 1, 3, '行程审核未通过', '你的广州行程审核未通过，请重新修改内容。', 0),
(3, 1, 2, '账户提示', '你最近收藏了新的行程，欢迎查看~', 1);
