# Eztrip API 接口文档（完整版）

> 本文档覆盖 Eztrip 项目的全部后端 API 接口。

---

## 目录

- [账号管理](#账号管理)
  - [用户登录](#用户登录)
  - [用户注册](#用户注册)
  - [修改密码](#修改密码)
  - [获取用户个人信息](#获取用户个人信息)
  - [修改用户个人信息](#修改用户个人信息)
  - [查找用户](#查找用户)
- [行程管理](#行程管理)
  - [新建行程](#新建行程)
  - [修改行程](#修改行程)
  - [删除行程](#删除行程)
  - [获取行程详情](#获取行程详情)
  - [获取用户行程列表](#获取用户行程列表)
  - [搜索公开行程](#搜索公开行程)
  - [获取高德静态地图](#获取高德静态地图)
- [收藏管理](#收藏管理)
  - [收藏行程](#收藏行程)
  - [取消收藏行程](#取消收藏行程)
  - [获取用户收藏的行程ID列表](#获取用户收藏的行程id列表)
  - [获取行程收藏人数](#获取行程收藏人数)
- [行程计划管理](#行程计划管理)
  - [获取行程计划](#获取行程计划)
  - [添加行程项目](#添加行程项目)
  - [删除行程项目](#删除行程项目)
- [公告管理](#公告管理)
  - [创建公告（草稿）](#创建公告草稿)
  - [发布公告](#发布公告)
  - [取消发布公告](#取消发布公告)
  - [删除公告](#删除公告)
  - [获取所有公告列表](#获取所有公告列表)
- [通知管理](#通知管理)
  - [获取用户通知列表](#获取用户通知列表)
  - [标记单条消息为已读](#标记单条消息为已读)
  - [标记所有消息为已读](#标记所有消息为已读)
- [AI 智能模块](#ai-智能模块)
  - [基础对话](#基础对话)
  - [流式对话](#流式对话)
  - [智能行程规划](#智能行程规划)
- [后台管理](#后台管理)
  - [列出待审核行程](#列出待审核行程)
  - [获取所有待审核行程](#获取所有待审核行程)
  - [审核行程](#审核行程)
  - [旧版审核接口](#旧版审核接口)
  - [发送审核结果消息](#发送审核结果消息)
  - [获取所有用户信息](#获取所有用户信息)
  - [更新用户状态](#更新用户状态)
  - [删除用户](#删除用户)
  - [获取用户总数](#获取用户总数)
  - [获取待审核数量](#获取待审核数量)
  - [获取内容统计](#获取内容统计)

---

## 账号管理

### 用户登录

#### 用户登录-请求URL

`POST /api/user/login`

#### 用户登录-请求参数

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|--------|------|
| username | string | 是 | 用户账号（Form 表单） |
| password | string | 是 | 密码（Form 表单） |

#### 用户登录-返回参数

| 字段名 | 类型 | 说明 |
|-------|------|------|
| message | string | 登录提示信息 |
| username | string | 登录成功时的用户名 |
| user_id | int | 用户ID |
| admin_id | int | 管理员ID（普通用户为 null） |

#### 用户登录-错误响应示例

| 状态码 | 错误信息（detail） | 说明 |
|--------|-------------------|------|
| 400 | Username and password are not null | 用户名或密码为空（含仅空格） |
| 401 | Username or password are wrong | 用户名不存在或密码错误 |
| 500 | Failed to connect database | 数据库连接失败 |
| 500 | 登录失败: [具体异常信息] | 其他服务器错误 |

---

### 用户注册

#### 用户注册-请求URL

`POST /api/user/register`

#### 用户注册-请求参数

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|--------|------|
| username | string | 是 | 用户账号（Form 表单） |
| email | string | 是 | 用户邮箱（Form 表单） |
| password | string | 是 | 密码（Form 表单） |
| confirm_password | string | 是 | 确认密码（Form 表单） |

#### 用户注册-返回参数

| 字段名 | 类型 | 说明 |
|-------|------|------|
| message | string | 注册提示信息 |

#### 用户注册-错误响应示例

| 状态码 | 错误信息（detail） | 说明 |
|--------|-------------------|------|
| 400 | Username,email,password and confirm_password are allowed to be null | 所有必填字段不能为空 |
| 400 | Username already existed | 用户名已存在 |
| 400 | Email is already used | 邮箱已被使用 |
| 400 | The password and confirm_password are different | 两次输入密码不一致 |
| 500 | Failed to connect database | 数据库连接失败 |
| 500 | 注册失败: [具体异常信息] | 其他服务器错误 |

---

### 修改密码

#### 修改密码-请求URL

`POST /api/user/change_password`

#### 修改密码-请求参数

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|--------|------|
| username | string | 是 | 用户账号（Form 表单） |
| email | string | 是 | 用户邮箱（Form 表单） |
| new_password | string | 是 | 新密码（Form 表单） |

#### 修改密码-返回参数

| 字段名 | 类型 | 说明 |
|-------|------|------|
| message | string | 修改密码提示信息 |

#### 修改密码-错误响应示例

| 状态码 | 错误信息（detail） | 说明 |
|--------|-------------------|------|
| 400 | Username,email and new_password are allowed to be null | 所有必填字段不能为空 |
| 404 | Username or email wrong | 用户名或邮箱错误 |
| 400 | Change password unsuccessful | 修改密码失败 |
| 500 | Failed to connect database | 数据库连接失败 |
| 500 | 修改密码失败: [具体异常信息] | 其他服务器错误 |

---

### 获取用户个人信息

#### 获取用户个人信息-请求URL

`GET /api/user/profile/{user_id}`

#### 获取用户个人信息-请求参数

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|--------|------|
| user_id | int | 是 | 用户ID（路径参数） |

#### 获取用户个人信息-返回参数

| 字段名 | 类型 | 说明 |
|-------|------|------|
| user_id | int | 用户ID |
| username | string | 用户名 |
| email | string | 邮箱 |
| avatar | string | 头像URL |
| admin_id | int | 管理员ID |
| phone_num | string | 手机号 |
| birthday | string | 生日（YYYY-MM-DD） |
| stats | object | 行程统计 |
| stats.completed_trips | int | 已完成行程数（end_date < 今天） |
| stats.upcoming_trips | int | 待出发行程数（start_date > 今天） |
| stats.collected_trips | int | 收藏行程数 |

#### 获取用户个人信息-错误响应示例

| 状态码 | 错误信息（detail） | 说明 |
|--------|-------------------|------|
| 404 | User not found | 用户不存在 |
| 500 | Failed to connect database | 数据库连接失败 |
| 500 | 获取个人信息失败: [具体异常信息] | 其他服务器错误 |

---

### 修改用户个人信息

#### 修改用户个人信息-请求URL

`PUT /api/user/profile/{user_id}`

#### 修改用户个人信息-请求参数

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|--------|------|
| user_id | int | 是 | 用户ID（路径参数） |
| phone_num | string | 否 | 手机号（Form 表单） |
| birthday | string | 否 | 生日 YYYY-MM-DD（Form 表单） |
| avatar | string | 否 | 头像URL（Form 表单） |
| email | string | 否 | 邮箱（Form 表单） |

> 至少传一个需要更新的字段，只传的字段才会被更新。

#### 修改用户个人信息-返回参数

| 字段名 | 类型 | 说明 |
|-------|------|------|
| message | string | 更新提示信息 |

#### 修改用户个人信息-错误响应示例

| 状态码 | 错误信息（detail） | 说明 |
|--------|-------------------|------|
| 404 | User not found | 用户不存在 |
| 500 | Failed to connect database | 数据库连接失败 |
| 500 | 更新个人信息失败: [具体异常信息] | 其他服务器错误 |

---

### 查找用户

#### 查找用户-请求URL

`POST /api/finduser`

#### 查找用户-请求参数

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|--------|------|
| username | string | 是 | 用户名（Form 表单） |

#### 查找用户-返回参数

| 字段名 | 类型 | 说明 |
|-------|------|------|
| message | string | 查询结果提示信息 |
| user | object | 用户信息 |
| user.username | string | 用户名 |
| user.avatar | string | 头像URL |
| user.email | string | 邮箱 |

#### 查找用户-错误响应示例

| 状态码 | 错误信息（detail） | 说明 |
|--------|-------------------|------|
| 400 | Username is not null | 用户名为空 |
| 404 | User not found | 用户不存在 |
| 500 | Failed to connect database | 数据库连接失败 |
| 500 | 查询用户失败: [具体异常信息] | 其他服务器错误 |

---

## 行程管理

### 新建行程

#### 新建行程-请求URL

`POST /api/user/trips/create`

#### 新建行程-请求参数

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|--------|------|
| owner_user_id | int | 是 | 行程所有者用户ID |
| title | string | 是 | 行程标题（最短1字符） |
| destination | string | 是 | 目的地（最短1字符） |
| start_date | string | 是 | 开始日期（YYYY-MM-DD） |
| end_date | string | 是 | 结束日期（YYYY-MM-DD） |
| is_public | int | 否 | 是否公开（0-私有，1-公开，默认0） |
| class_type | int | 是 | 行程类型（1-休闲，2-美食，3-商务，4-家庭） |
| remarks | object | 否 | 行程备注 JSON 对象 |

#### 新建行程-返回参数

| 字段名 | 类型 | 说明 |
|-------|------|------|
| message | string | 新建行程提示信息 |
| trip_id | int | 行程ID |

#### 新建行程-错误响应示例

| 状态码 | 错误信息（detail） | 说明 |
|--------|-------------------|------|
| 400 | Invalid class_type | 行程类型不合法 |
| 500 | Failed to connect database | 数据库连接失败 |
| 500 | 创建行程失败: [具体异常信息] | 其他服务器错误 |

---

### 修改行程

#### 修改行程-请求URL

`PUT /api/trip/update`

#### 修改行程-请求参数

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|--------|------|
| user_id | int | 是 | 当前登录用户ID |
| trip_id | int | 是 | 行程ID |
| trip_name | string | 是 | 行程标题 |
| destination | string | 是 | 目的地 |
| start_date | string | 是 | 开始日期（YYYY-MM-DD） |
| end_date | string | 是 | 结束日期（YYYY-MM-DD） |
| is_public | int | 是 | 是否公开（0-私有，1-公开） |
| publish_action | string | 是 | 发布操作（keep-保持当前状态，submit-提交审核，unpublish-取消发布） |
| remarks | object | 否 | 行程备注 JSON 对象 |

#### 修改行程-返回参数

| 字段名 | 类型 | 说明 |
|-------|------|------|
| message | string | 修改行程提示信息 |

#### 修改行程-错误响应示例

| 状态码 | 错误信息（detail） | 说明 |
|--------|-------------------|------|
| 400 | Invalid publish_action | 发布操作不合法 |
| 400 | 日期格式应为 YYYY-MM-DD | 日期格式错误 |
| 400 | 结束日期不能早于开始日期 | 日期范围错误 |
| 404 | Trip not found | 行程不存在 |
| 403 | No permission (favorite trip is read-only) | 无权限（只有创建者可修改） |
| 400 | 当前状态不可提交审核 | 行程状态不允许提交审核（仅 draft/rejected 可提交） |
| 500 | Failed to connect database | 数据库连接失败 |
| 500 | 更新行程失败: [具体异常信息] | 其他服务器错误 |

---

### 删除行程

#### 删除行程-请求URL

`DELETE /api/trip/delete`

#### 删除行程-请求参数

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|--------|------|
| trip_id | int | 是 | 要删除的行程ID |
| user_id | int | 是 | 当前操作的用户ID |

> 权限说明：只有创建者本人或管理员（user_id=1）可删除。删除时级联清理收藏记录及行程计划数据。

#### 删除行程-返回参数

| 字段名 | 类型 | 说明 |
|-------|------|------|
| message | string | 删除结果提示信息 |
| code | int | 状态码 |

#### 删除行程-错误响应示例

| 状态码 | 错误信息（detail） | 说明 |
|--------|-------------------|------|
| 404 | 行程不存在 | 行程未找到 |
| 403 | 无权删除该行程 | 无删除权限 |
| 500 | Failed to connect database | 数据库连接失败 |
| 500 | 删除行程失败: [具体异常信息] | 其他服务器错误 |

---

### 获取行程详情

#### 获取行程详情-请求URL

`GET /api/trip/detail`

#### 获取行程详情-请求参数

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|--------|------|
| user_id | int | 是 | 当前登录用户ID |
| trip_id | int | 是 | 行程ID |

> **可见性规则**：创建者本人可查看、收藏者可见、公开且已发布的行程所有人可见。

#### 获取行程详情-返回参数

| 字段名 | 类型 | 说明 |
|-------|------|------|
| trip_id | int | 行程ID |
| owner_user_id | int | 创建者用户ID |
| trip_name | string | 行程标题 |
| destination | string | 目的地 |
| start_date | string | 开始日期 |
| end_date | string | 结束日期 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| publish_status | string | 发布状态（draft/pending/published/rejected） |
| review_comment | string | 审核意见 |
| is_public | bool | 是否公开 |
| is_collected | bool | 当前用户是否已收藏 |
| is_owner | bool | 当前用户是否是创建者 |
| is_favorited | bool | 是否已被收藏（同 is_collected） |
| class | int | 行程分类（1-休闲,2-美食,3-商务,4-家庭） |
| remarks | object/string | 行程备注（优先JSON解析，失败返回原始字符串） |
| lng | float | 目的地经度（高德地理编码） |
| lat | float | 目的地纬度 |

#### 获取行程详情-错误响应示例

| 状态码 | 错误信息（detail） | 说明 |
|--------|-------------------|------|
| 404 | Trip not found or no permission | 行程不存在或无权限访问 |
| 500 | Failed to connect database | 数据库连接失败 |
| 500 | 获取行程详情失败: [具体异常信息] | 其他服务器错误 |

---

### 获取用户行程列表

#### 获取用户行程列表-请求URL

`GET /api/user/trips/list`

#### 获取用户行程列表-请求参数

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|--------|------|
| user_id | int | 是 | 当前登录用户ID |

> 返回用户创建的行程 + 用户收藏的行程。

#### 获取用户行程列表-返回参数

| 字段名 | 类型 | 说明 |
|-------|------|------|
| trip_id | int | 行程ID |
| trip_name | string | 行程标题 |
| destination | string | 目的地 |
| start_date | string | 开始日期 |
| end_date | string | 结束日期 |
| days | int | 行程天数 |
| owner_user_id | int | 创建者ID |
| is_collected | bool | 当前用户是否已收藏 |
| class | int | 行程分类 |
| class_text | string | 分类中文描述 |

#### 获取用户行程列表-错误响应示例

| 状态码 | 错误信息（detail） | 说明 |
|--------|-------------------|------|
| 500 | Failed to connect database | 数据库连接失败 |
| 500 | 获取行程列表失败: [具体异常信息] | 其他服务器错误 |

---

### 搜索公开行程

#### 搜索公开行程-请求URL

`GET /api/public_trips/search_trips`

#### 搜索公开行程-请求参数

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|--------|------|
| limit | int | 否 | 返回条数（1-200，默认50） |
| offset | int | 否 | 分页偏移（默认0） |
| destination | string | 否 | 目的地关键词（模糊匹配） |
| class_type | int | 否 | 按分类过滤（1-4） |
| days | int | 否 | 按天数过滤（1-365） |

> 只返回 is_public=1 且 publish_status='published' 的公开行程。

#### 搜索公开行程-返回参数

| 字段名 | 类型 | 说明 |
|-------|------|------|
| trip_id | int | 行程ID |
| owner_user_id | int | 创建者ID |
| creator_username | string | 创建者用户名 |
| title | string | 行程标题 |
| destination | string | 目的地 |
| class | int | 分类编号 |
| class_text | string | 分类中文名 |
| days | int | 行程天数 |
| created_at | string | 创建时间 |

#### 搜索公开行程-错误响应示例

| 状态码 | 错误信息（detail） | 说明 |
|--------|-------------------|------|
| 500 | Failed to connect database | 数据库连接失败 |
| 500 | 搜索公开行程失败: [具体异常信息] | 其他服务器错误 |

---

### 获取高德静态地图

#### 获取高德静态地图-请求URL

`GET /api/trip/map/url`

#### 获取高德静态地图-请求参数

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|--------|------|
| lng | float | 是 | 地图中心点经度 |
| lat | float | 是 | 地图中心点纬度 |
| zoom | int | 否 | 缩放等级（1-18，默认14） |
| width | int | 否 | 图片宽度（1-1024，默认600） |
| height | int | 否 | 图片高度（1-1024，默认300） |
| label | string | 否 | 标记点文本（默认"A"） |

#### 获取高德静态地图-返回参数

| 字段名 | 类型 | 说明 |
|-------|------|------|
| url | string | 高德静态地图完整URL，前端直接用 `<img :src="url">` 显示 |

#### 获取高德静态地图-错误响应示例

| 状态码 | 错误信息（detail） | 说明 |
|--------|-------------------|------|
| 500 | 高德 Web 服务 Key 未配置 | AMAP_WEB_KEY 未设置 |

---

## 收藏管理

### 收藏行程

#### 收藏行程-请求URL

`POST /api/collect/favorite/add`

#### 收藏行程-请求参数

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|--------|------|
| user_id | int | 是 | 用户ID |
| trip_id | int | 是 | 行程ID |

#### 收藏行程-返回参数

| 字段名 | 类型 | 说明 |
|-------|------|------|
| code | int | 状态码 |
| message | string | 收藏行程提示信息 |
| data | object | 收藏数据 |
| data.user_id | int | 用户ID |
| data.trip_id | int | 行程ID |

#### 收藏行程-错误响应示例

| 状态码 | 错误信息（detail） | 说明 |
|--------|-------------------|------|
| 403 | 用户ID [用户ID] 不存在 | 用户不存在 |
| 404 | 行程ID [行程ID] 不存在，或未发布/未公开，无法收藏 | 行程不存在或状态不允许 |
| 400 | 已收藏该行程，无需重复操作 | 行程已被收藏 |
| 500 | 数据库连接失败 | 数据库连接失败 |
| 500 | 添加收藏失败：[具体异常信息] | 其他服务器错误 |

---

### 取消收藏行程

#### 取消收藏行程-请求URL

`POST /api/collect/favorite/remove`

#### 取消收藏行程-请求参数

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|--------|------|
| user_id | int | 是 | 用户ID |
| trip_id | int | 是 | 行程ID |

#### 取消收藏行程-返回参数

| 字段名 | 类型 | 说明 |
|-------|------|------|
| code | int | 状态码 |
| message | string | 取消收藏提示信息 |
| data | object | 取消收藏数据 |
| data.user_id | int | 用户ID |
| data.trip_id | int | 行程ID |

#### 取消收藏行程-错误响应示例

| 状态码 | 错误信息（detail） | 说明 |
|--------|-------------------|------|
| 404 | 用户ID [用户ID] 不存在 | 用户不存在 |
| 400 | 未收藏该行程，无需取消 | 行程未被收藏 |
| 500 | 取消收藏失败! | 取消收藏操作失败 |
| 500 | 数据库连接失败 | 数据库连接失败 |
| 500 | 取消收藏失败：[具体异常信息] | 其他服务器错误 |

---

### 获取用户收藏的行程ID列表

#### 获取用户收藏的行程ID列表-请求URL

`POST /api/collect/favorite/list`

#### 获取用户收藏的行程ID列表-请求参数

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|--------|------|
| user_id | int | 是 | 用户ID |

#### 获取用户收藏的行程ID列表-返回参数

| 字段名 | 类型 | 说明 |
|-------|------|------|
| code | int | 状态码 |
| message | string | 获取收藏列表提示信息 |
| data | object | 收藏列表数据 |
| data.user_id | int | 用户ID |
| data.trip_ids | array | 行程ID列表 |
| data.count | int | 收藏数量 |

#### 获取用户收藏的行程ID列表-错误响应示例

| 状态码 | 错误信息（detail） | 说明 |
|--------|-------------------|------|
| 404 | 用户ID [用户ID] 不存在 | 用户不存在 |
| 500 | 数据库连接失败 | 数据库连接失败 |
| 500 | 获取收藏列表失败：[具体异常信息] | 其他服务器错误 |

---

### 获取行程收藏人数

#### 获取行程收藏人数-请求URL

`GET /api/trip/favorite-count`

#### 获取行程收藏人数-请求参数

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|--------|------|
| trip_id | int | 是 | 行程ID |

#### 获取行程收藏人数-返回参数

| 字段名 | 类型 | 说明 |
|-------|------|------|
| trip_id | int | 行程ID |
| count | int | 收藏人数 |

#### 获取行程收藏人数-错误响应示例

| 状态码 | 错误信息（detail） | 说明 |
|--------|-------------------|------|
| 500 | Failed to connect database | 数据库连接失败 |
| 500 | 获取收藏人数失败: [具体异常信息] | 其他服务器错误 |

---

## 行程计划管理

### 获取行程计划

#### 获取行程计划-请求URL

`GET /api/trip_plan/get`

#### 获取行程计划-请求参数

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|--------|------|
| user_id | int | 是 | 用户ID |
| trip_id | int | 是 | 行程ID |

> 会自动根据行程起止日期补齐缺失的天数，确保每天都有计划记录。

#### 获取行程计划-返回参数

| 字段名 | 类型 | 说明 |
|-------|------|------|
| trip_id | int | 行程ID |
| total_days | int | 总天数 |
| days | array | 每日计划数组 |
| days[].day_index | int | 第几天（从1开始） |
| days[].plan_date | string | 对应日期 |
| days[].note | string | 当天备注 |
| days[].items | array | 当天项目列表 |
| days[].items[].id | int | 项目ID |
| days[].items[].title | string | 项目名称 |
| days[].items[].place_type | string | 地点类型（景点/餐厅等） |
| days[].items[].sort_order | int | 排序序号 |

#### 获取行程计划-错误响应示例

| 状态码 | 错误信息（detail） | 说明 |
|--------|-------------------|------|
| 404 | Trip not found | 行程不存在 |
| 400 | Invalid trip dates | 行程日期无效 |
| 500 | 数据库连接失败 | 数据库连接失败 |
| 500 | 获取行程计划失败: [具体异常信息] | 其他服务器错误 |

---

### 添加行程项目

#### 添加行程项目-请求URL

`POST /api/trip_plan/item/add`

#### 添加行程项目-请求参数

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|--------|------|
| user_id | int | 是 | 用户ID（仅创建者可编辑） |
| trip_id | int | 是 | 行程ID |
| day_index | int | 是 | 第几天 |
| title | string | 是 | 项目标题 |
| place_type | string | 否 | 地点类型（如"景点"、"餐厅"） |

#### 添加行程项目-返回参数

| 字段名 | 类型 | 说明 |
|-------|------|------|
| code | int | 状态码 |
| message | string | 操作结果 |
| data | object | 新增项目数据 |
| data.id | int | 项目ID |
| data.day_index | int | 所属天数 |
| data.title | string | 项目名称 |
| data.place_type | string | 地点类型 |
| data.sort_order | int | 排序序号 |

#### 添加行程项目-错误响应示例

| 状态码 | 错误信息（detail） | 说明 |
|--------|-------------------|------|
| 400 | title 不能为空 | 标题为空 |
| 404 | Trip not found | 行程不存在 |
| 403 | 无权限编辑该行程计划 | 非创建者无权限 |
| 404 | Day plan not found | 该天计划不存在 |
| 500 | 数据库连接失败 | 数据库连接失败 |
| 500 | 添加失败: [具体异常信息] | 其他服务器错误 |

---

### 删除行程项目

#### 删除行程项目-请求URL

`POST /api/trip_plan/item/delete`

#### 删除行程项目-请求参数

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|--------|------|
| user_id | int | 是 | 用户ID（仅创建者可编辑） |
| trip_id | int | 是 | 行程ID |
| item_id | int | 是 | 项目ID |

#### 删除行程项目-返回参数

| 字段名 | 类型 | 说明 |
|-------|------|------|
| code | int | 状态码 |
| message | string | 操作结果 |

#### 删除行程项目-错误响应示例

| 状态码 | 错误信息（detail） | 说明 |
|--------|-------------------|------|
| 404 | Trip not found | 行程不存在 |
| 403 | 无权限编辑该行程计划 | 非创建者无权限 |
| 404 | Item not found | 项目不存在 |
| 500 | 数据库连接失败 | 数据库连接失败 |
| 500 | 删除失败: [具体异常信息] | 其他服务器错误 |

---

## 公告管理

### 创建公告（草稿）

#### 创建公告（草稿）-请求URL

`POST /api/notice/create`

#### 创建公告（草稿）-请求参数

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|--------|------|
| title | string | 是 | 公告标题（Form 表单） |
| content | string | 是 | 公告内容（Form 表单） |
| created_by | int | 是 | 管理员ID（Form 表单） |

> 创建时默认为草稿状态（is_active=0），需调用发布接口后用户才能看到。

#### 创建公告（草稿）-返回参数

| 字段名 | 类型 | 说明 |
|-------|------|------|
| success | boolean | 请求是否成功 |
| message | string | 创建公告提示信息 |
| data | object | 公告数据 |
| data.notice_id | int | 新建公告ID |

#### 创建公告（草稿）-错误响应示例

| 状态码 | 错误信息（detail） | 说明 |
|--------|-------------------|------|
| 400 | 标题和内容不能为空 | 标题或内容为空 |
| 400 | 无效的管理员ID | 管理员ID不合法 |
| 400 | 创建公告失败 | 数据库插入失败 |
| 500 | 数据库连接失败 | 数据库连接失败 |
| 500 | 创建公告失败：[具体异常信息] | 其他服务器错误 |

---

### 发布公告

#### 发布公告-请求URL

`POST /api/notice/publish`

#### 发布公告-请求参数

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|--------|------|
| notice_id | int | 是 | 公告ID（Form 表单） |
| admin_id | int | 是 | 管理员ID（Form 表单，用于发送消息） |

> 将公告从草稿（is_active=0）转为已发布（is_active=1），并给所有用户发送系统通知消息。

#### 发布公告-返回参数

| 字段名 | 类型 | 说明 |
|-------|------|------|
| success | boolean | 请求是否成功 |
| message | string | 发布结果提示信息 |

#### 发布公告-错误响应示例

| 状态码 | 错误信息（detail） | 说明 |
|--------|-------------------|------|
| 400 | 无效的公告ID或管理员ID | 参数不合法 |
| 404 | 公告不存在或已发布 | 公告未找到或已发布 |
| 500 | 数据库连接失败 | 数据库连接失败 |
| 500 | 发布公告失败：[具体异常信息] | 其他服务器错误 |

---

### 取消发布公告

#### 取消发布公告-请求URL

`POST /api/notice/unpublish`

#### 取消发布公告-请求参数

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|--------|------|
| notice_id | int | 是 | 公告ID（Form 表单） |

> 将公告从已发布（is_active=1）恢复为草稿（is_active=0）。

#### 取消发布公告-返回参数

| 字段名 | 类型 | 说明 |
|-------|------|------|
| success | boolean | 请求是否成功 |
| message | string | 操作结果提示信息 |

#### 取消发布公告-错误响应示例

| 状态码 | 错误信息（detail） | 说明 |
|--------|-------------------|------|
| 400 | 无效的公告ID | 公告ID不合法 |
| 404 | 公告不存在或未发布 | 公告未找到或不是已发布状态 |
| 500 | 数据库连接失败 | 数据库连接失败 |
| 500 | 取消发布失败：[具体异常信息] | 其他服务器错误 |

---

### 删除公告

#### 删除公告-请求URL

`POST /api/notice/delete`

#### 删除公告-请求参数

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|--------|------|
| notice_id | int | 是 | 公告ID（Form 表单） |

#### 删除公告-返回参数

| 字段名 | 类型 | 说明 |
|-------|------|------|
| success | boolean | 请求是否成功 |
| message | string | 删除结果提示信息 |

#### 删除公告-错误响应示例

| 状态码 | 错误信息（detail） | 说明 |
|--------|-------------------|------|
| 400 | 无效的公告ID | 公告ID不合法 |
| 404 | 公告不存在 | 公告未找到 |
| 500 | 数据库连接失败 | 数据库连接失败 |
| 500 | 删除公告失败：[具体异常信息] | 其他服务器错误 |

---

### 获取所有公告列表

#### 获取所有公告列表-请求URL

`GET /api/notice/list`

#### 获取所有公告列表-请求参数

无

#### 获取所有公告列表-返回参数

| 字段名 | 类型 | 说明 |
|-------|------|------|
| success | boolean | 请求是否成功 |
| data | object | 公告数据 |
| data.notices | array | 公告列表 |
| data.notices[].notice_id | int | 公告ID |
| data.notices[].title | string | 公告标题 |
| data.notices[].created_at | string | 创建时间 |
| data.notices[].is_active | int | 是否已发布（0-草稿，1-已发布） |
| data.notices[].created_by_name | string | 创建者用户名 |
| data.count | int | 公告数量 |

#### 获取所有公告列表-错误响应示例

| 状态码 | 错误信息（detail） | 说明 |
|--------|-------------------|------|
| 500 | 数据库连接失败 | 数据库连接失败 |
| 500 | 获取公告列表失败：[具体异常信息] | 其他服务器错误 |

---

## 通知管理

### 获取用户通知列表

#### 获取用户通知列表-请求URL

`GET /api/notifications`

#### 获取用户通知列表-请求参数

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|--------|------|
| user_id | int | 是 | 用户ID |

#### 获取用户通知列表-返回参数

| 字段名 | 类型 | 说明 |
|-------|------|------|
| id | int | 通知ID |
| kind | string | 通知类型（notice-公告，message-个人消息） |
| sender | string | 发送者 |
| title | string | 通知标题 |
| content | string | 通知内容 |
| created_at | string | 创建时间 |
| unread | boolean | 是否未读 |
| type | string | 消息类型（system-系统，service-客服） |

#### 获取用户通知列表-错误响应示例

| 状态码 | 错误信息（detail） | 说明 |
|--------|-------------------|------|
| 500 | Failed to connect database | 数据库连接失败 |
| 500 | 获取消息失败: [具体异常信息] | 其他服务器错误 |

---

### 标记单条消息为已读

#### 标记单条消息为已读-请求URL

`PUT /api/notifications/messages/{message_id}/read`

#### 标记单条消息为已读-请求参数

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|--------|------|
| message_id | int | 是 | 消息ID（路径参数） |
| user_id | int | 是 | 用户ID |

#### 标记单条消息为已读-返回参数

| 字段名 | 类型 | 说明 |
|-------|------|------|
| message | string | 操作结果提示信息 |

#### 标记单条消息为已读-错误响应示例

| 状态码 | 错误信息（detail） | 说明 |
|--------|-------------------|------|
| 404 | Message not found | 消息不存在 |
| 500 | Failed to connect database | 数据库连接失败 |
| 500 | 标记消息已读失败: [具体异常信息] | 其他服务器错误 |

---

### 标记所有消息为已读

#### 标记所有消息为已读-请求URL

`PUT /api/notifications/messages/read-all`

#### 标记所有消息为已读-请求参数

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|--------|------|
| user_id | int | 是 | 用户ID |

#### 标记所有消息为已读-返回参数

| 字段名 | 类型 | 说明 |
|-------|------|------|
| message | string | 操作结果提示信息 |

#### 标记所有消息为已读-错误响应示例

| 状态码 | 错误信息（detail） | 说明 |
|--------|-------------------|------|
| 500 | Failed to connect database | 数据库连接失败 |
| 500 | 批量标记消息已读失败: [具体异常信息] | 其他服务器错误 |

---

## AI 智能模块

### 基础对话

#### 基础对话-请求URL

`POST /api/model`

#### 基础对话-请求参数

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|--------|------|
| prompt | string | 是 | 提示词 |

> 调用 DeepSeek 大模型（非流式），返回最终回答。

#### 基础对话-返回参数

| 字段名 | 类型 | 说明 |
|-------|------|------|
| response | string | 模型回答内容 |

#### 基础对话-错误响应示例

| 状态码 | 错误信息（detail） | 说明 |
|--------|-------------------|------|
| 400 | 提示词不能为空 | prompt 为空 |
| 500 | 大模型调用失败: [具体异常信息] | 模型调用失败 |

---

### 流式对话

#### 流式对话-请求URL

`POST /api/model/stream`

#### 流式对话-请求参数

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|--------|------|
| prompt | string | 是 | 提示词 |

> 使用 SSE（Server-Sent Events）流式返回模型输出，前端可用 EventSource 接收。

#### 流式对话-返回格式（SSE）

每条数据格式为 `data: {json}\n\n`，包含以下事件类型：

| type 值 | 说明 |
|---------|------|
| start | 开始标志 |
| delta | 增量内容片段（content 字段包含文本） |
| done | 结束标志 |
| error | 错误信息（message 字段包含错误描述） |

#### 流式对话-错误响应示例

| 状态码 | 错误信息（detail） | 说明 |
|--------|-------------------|------|
| 400 | 提示词不能为空 | prompt 为空 |

---

### 智能行程规划

#### 智能行程规划-请求URL

`POST /api/model/agent_plan`

#### 智能行程规划-请求参数

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|--------|------|
| user_id | int | 是 | 用户ID |
| prompt | string | 是 | 自然语言描述的需求 |
| direct_add_plan | bool | 否 | 是否直接写入数据库（默认 false） |

> - `direct_add_plan=false`：仅对话，返回 AI 规划文本
> - `direct_add_plan=true`：AI 自动生成结构化行程，直接写入 trip、trip_day_plan、trip_day_item 表，返回 trip_id

#### 智能行程规划-返回参数（direct_add_plan=false）

| 字段名 | 类型 | 说明 |
|-------|------|------|
| reply | string | AI 回复内容 |
| trip_id | null | 空 |

#### 智能行程规划-返回参数（direct_add_plan=true）

| 字段名 | 类型 | 说明 |
|-------|------|------|
| reply | string | AI 回复内容 |
| trip_id | int | 新建行程ID |
| structured_data | object | 完整的结构化行程数据 |

#### 智能行程规划-错误响应示例

| 状态码 | 错误信息（detail） | 说明 |
|--------|-------------------|------|
| 400 | 提示词不能为空 | prompt 为空 |
| 500 | 大模型调用失败: [具体异常信息] | 模型调用失败 |
| 500 | 数据库写入失败: [具体异常信息] | 数据库写入失败 |

---

## 后台管理

### 列出待审核行程

#### 列出待审核行程-请求URL

`GET /api/admin/trips/pending`

#### 列出待审核行程-请求参数

无

> 返回 publish_status 为 pending（待审核）或 published（已发布）的所有行程。

#### 列出待审核行程-返回参数

返回行程对象数组，每个对象包含：

| 字段名 | 类型 | 说明 |
|-------|------|------|
| trip_id | int | 行程ID |
| title | string | 行程标题 |
| destination | string | 目的地 |
| start_date | string | 开始日期 |
| end_date | string | 结束日期 |
| owner_user_id | int | 创建者ID |
| owner_username | string | 创建者用户名 |
| publish_status | string | 发布状态 |
| is_public | int | 是否公开 |
| created_at | string | 创建时间 |

#### 列出待审核行程-错误响应示例

| 状态码 | 错误信息（detail） | 说明 |
|--------|-------------------|------|
| 500 | Failed to connect database | 数据库连接失败 |
| 500 | 获取审核列表失败: [具体异常信息] | 其他服务器错误 |

---

### 获取所有待审核行程

#### 获取所有待审核行程-请求URL

`GET /api/admin/all_pending_trips`

#### 获取所有待审核行程-请求参数

无

> 返回 publish_status 不为 draft 的所有行程（含 pending、published、rejected），pending 排在最前。

#### 获取所有待审核行程-返回参数

| 字段名 | 类型 | 说明 |
|-------|------|------|
| success | boolean | 请求是否成功 |
| data | object | 数据 |
| data.trips | array | 行程列表（含 trip 表全部字段 + owner_username） |
| data.count | int | 行程数量 |

#### 获取所有待审核行程-错误响应示例

| 状态码 | 错误信息（detail） | 说明 |
|--------|-------------------|------|
| 500 | 数据库连接失败 | 数据库连接失败 |
| 500 | 审核查询失败: [具体异常信息] | 其他服务器错误 |

---

### 审核行程

#### 审核行程-请求URL

`POST /api/admin/trips/review`

#### 审核行程-请求参数

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|--------|------|
| admin_user_id | int | 是 | 审核管理员ID |
| trip_id | int | 是 | 行程ID |
| action | string | 是 | 审核操作（approve-通过，reject-驳回） |
| comment | string | 否 | 审核意见 |

> 审核通过后 publish_status 变为 published，驳回后变为 rejected。同时记录 reviewed_by、reviewed_at 和 review_comment。

#### 审核行程-返回参数

| 字段名 | 类型 | 说明 |
|-------|------|------|
| message | string | 操作结果 |
| publish_status | string | 更新后的发布状态 |

#### 审核行程-错误响应示例

| 状态码 | 错误信息（detail） | 说明 |
|--------|-------------------|------|
| 400 | Invalid action | action 参数不合法 |
| 404 | Trip not found | 行程不存在 |
| 500 | Failed to connect database | 数据库连接失败 |
| 500 | 审核失败: [具体异常信息] | 其他服务器错误 |

---

### 旧版审核接口

#### 旧版审核接口-请求URL

`POST /api/admin/pending`

#### 旧版审核接口-请求参数

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|--------|------|
| trip_id | string | 是 | 行程ID（Form 表单） |
| status | string | 是 | 审核结果（accept-通过，reject-驳回）（Form 表单） |

> 此为旧版审核接口，只更新 publish_status，不记录审核人和审核时间。推荐使用 `/api/admin/trips/review`。

#### 旧版审核接口-返回参数

| 字段名 | 类型 | 说明 |
|-------|------|------|
| message | string | 操作结果 |

#### 旧版审核接口-错误响应示例

| 状态码 | 错误信息（detail） | 说明 |
|--------|-------------------|------|
| 400 | 用户ID必须是数字 | trip_id 不是有效数字 |
| 400 | status参数必须是'accept'或'reject' | status 不合法 |
| 404 | 未找到ID为[trip_id]的行程 | 行程不存在 |
| 500 | 数据库连接失败 | 数据库连接失败 |
| 500 | 处理审核失败: [具体异常信息] | 其他服务器错误 |

---

### 发送审核结果消息

#### 发送审核结果消息-请求URL

`POST /api/admin/send_message`

#### 发送审核结果消息-请求参数

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|--------|------|
| sender_id | string | 是 | 发送者（管理员）ID（Form 表单） |
| trip_id | string | 是 | 行程ID（Form 表单） |
| status | string | 是 | 审核结果（accept-通过，reject-驳回）（Form 表单） |

> 给行程创建者发送审核结果系统消息。accept 时消息内容为"您的行程'XXX'审核已通过！"，reject 时消息内容为"您的行程'XXX'审核未通过，请检查内容后重新提交。"

#### 发送审核结果消息-返回参数

| 字段名 | 类型 | 说明 |
|-------|------|------|
| message | string | 操作结果 |
| details | object | 详情 |
| details.user_id | int | 接收消息的用户ID |
| details.trip_id | string | 行程ID |
| details.message_sent | boolean | 消息是否发送成功 |
| details.reason | string | 发送状态说明 |

#### 发送审核结果消息-错误响应示例

| 状态码 | 错误信息（detail） | 说明 |
|--------|-------------------|------|
| 400 | 行程ID和发送者ID必须是数字 | 参数类型错误 |
| 400 | status参数必须是'accept'或'reject' | status 不合法 |
| 404 | 未找到ID为[trip_id]的行程 | 行程不存在 |
| 500 | 数据库连接失败 | 数据库连接失败 |
| 500 | 处理审核消息失败: [具体异常信息] | 其他服务器错误 |

---

### 获取所有用户信息

#### 获取所有用户信息-请求URL

`GET /api/admin/all_user_info`

#### 获取所有用户信息-请求参数

无

#### 获取所有用户信息-返回参数

| 字段名 | 类型 | 说明 |
|-------|------|------|
| success | boolean | 请求是否成功 |
| data | object | 用户数据 |
| data.users | array | 用户列表 |
| data.users[].user_id | int | 用户ID |
| data.users[].username | string | 用户名 |
| data.users[].email | string | 邮箱 |
| data.users[].avatar | string | 头像 |
| data.users[].admin_id | int | 管理员ID |
| data.users[].status | string | 用户状态 |
| data.count | int | 用户总数 |

#### 获取所有用户信息-错误响应示例

| 状态码 | 错误信息（detail） | 说明 |
|--------|-------------------|------|
| 500 | 数据库连接失败 | 数据库连接失败 |
| 500 | 查询用户失败: [具体异常信息] | 其他服务器错误 |

---

### 更新用户状态

#### 更新用户状态-请求URL

`POST /api/admin/update_user_status`

#### 更新用户状态-请求参数

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|--------|------|
| user_id | string | 是 | 用户ID（Form 表单） |
| status | string | 是 | 新状态（如 active / banned）（Form 表单） |

#### 更新用户状态-返回参数

| 字段名 | 类型 | 说明 |
|-------|------|------|
| success | boolean | 请求是否成功 |
| message | string | 操作结果 |
| data | object | 更新数据 |
| data.user | object | 更新后的用户信息 |
| data.changes | object | 变更记录 |
| data.changes.previous_status | string | 旧状态 |
| data.changes.new_status | string | 新状态 |

#### 更新用户状态-错误响应示例

| 状态码 | 错误信息（detail） | 说明 |
|--------|-------------------|------|
| 400 | 用户ID不能为空 | user_id 为空 |
| 400 | 状态不能为空 | status 为空 |
| 400 | 用户ID必须是数字 | user_id 不是有效数字 |
| 404 | 用户不存在 | 用户未找到 |
| 400 | 用户已经是 [status] 状态，无需修改 | 状态相同无需操作 |
| 500 | 数据库连接失败 | 数据库连接失败 |
| 500 | 更新用户状态失败: [具体异常信息] | 其他服务器错误 |

---

### 删除用户

#### 删除用户-请求URL

`POST /api/admin/delete_user`

#### 删除用户-请求参数

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|--------|------|
| user_id | string | 是 | 要删除的用户ID（Form 表单） |

> **级联删除逻辑**：
> 1. 将该用户审核过的行程的 reviewed_by 置为 NULL
> 2. 删除该用户发送和接收的消息
> 3. 删除其他用户收藏该用户行程的记录
> 4. 删除该用户收藏他人的记录
> 5. 删除该用户创建的所有行程（同时级联删除行程计划和项目）
> 6. 删除用户本身

#### 删除用户-返回参数

| 字段名 | 类型 | 说明 |
|-------|------|------|
| success | boolean | 请求是否成功 |
| message | string | 操作结果 |
| deleted_user_id | int | 被删除的用户ID |
| details | object | 删除详情 |
| details.user_info_deleted | int | 删除用户记录数 |
| details.user_trips_deleted | int | 删除行程数 |
| details.user_favorites_deleted | int | 删除该用户收藏数 |
| details.other_user_favorites_deleted | int | 删除其他用户收藏该用户行程数 |
| details.trips_review_cleared | int | 解除审核关联数 |
| details.sent_messages_deleted | int | 删除发送消息数 |
| details.received_messages_deleted | int | 删除接收消息数 |

#### 删除用户-错误响应示例

| 状态码 | 错误信息（detail） | 说明 |
|--------|-------------------|------|
| 400 | 用户ID不能为空 | user_id 为空 |
| 400 | 用户ID必须是数字 | user_id 不是有效数字 |
| 404 | 用户不存在 | 用户未找到 |
| 500 | 数据库连接失败 | 数据库连接失败 |
| 500 | 删除用户失败: [具体异常信息] | 其他服务器错误 |

---

### 获取用户总数

#### 获取用户总数-请求URL

`GET /api/admin/user_count`

#### 获取用户总数-请求参数

无

#### 获取用户总数-返回参数

| 字段名 | 类型 | 说明 |
|-------|------|------|
| success | boolean | 请求是否成功 |
| data | object | 统计数据 |
| data.user_count | int | 用户总数 |

#### 获取用户总数-错误响应示例

| 状态码 | 错误信息（detail） | 说明 |
|--------|-------------------|------|
| 500 | Failed to connect database | 数据库连接失败 |
| 500 | 获取用户数失败: [具体异常信息] | 其他服务器错误 |

---

### 获取待审核数量

#### 获取待审核数量-请求URL

`GET /api/admin/pending_review_count`

#### 获取待审核数量-请求参数

无

#### 获取待审核数量-返回参数

| 字段名 | 类型 | 说明 |
|-------|------|------|
| success | boolean | 请求是否成功 |
| data | object | 统计数据 |
| data.pending_review_count | int | 待审核行程数量 |

#### 获取待审核数量-错误响应示例

| 状态码 | 错误信息（detail） | 说明 |
|--------|-------------------|------|
| 500 | Failed to connect database | 数据库连接失败 |
| 500 | 获取待审核数失败: [具体异常信息] | 其他服务器错误 |

---

### 获取内容统计

#### 获取内容统计-请求URL

`GET /api/admin/content_count`

#### 获取内容统计-请求参数

无

#### 获取内容统计-返回参数

| 字段名 | 类型 | 说明 |
|-------|------|------|
| success | boolean | 请求是否成功 |
| data | object | 统计数据 |
| data.content_count | int | 行程总数 |
| data.today_new_count | int | 今日新增行程数 |

#### 获取内容统计-错误响应示例

| 状态码 | 错误信息（detail） | 说明 |
|--------|-------------------|------|
| 500 | Failed to connect database | 数据库连接失败 |
| 500 | 获取内容统计失败: [具体异常信息] | 其他服务器错误 |
