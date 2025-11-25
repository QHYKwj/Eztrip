# API接口文档

## 目录

- [账号管理](#账号管理)
  - [用户登录](#用户登录)
  - [用户注册](#用户注册)
  - [修改密码](#修改密码)
- [行程管理](#行程管理)
  - [新建行程](#新建行程)
  - [修改行程](#修改行程)
  - [删除行程](#删除行程) 
  - [收藏行程](#收藏行程)

## 账号管理

### 用户登录

#### 用户登录-请求URL

POST /api/login

#### 用户登录-请求参数

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|--------|-------|
| username | string | 是 | 用户账号 |
| password | string | 是 | 密码 |

#### 用户登录-返回参数

| 字段名 | 类型 | 说明 |
|-------|------|------|
| message | string | 登录提示信息 |
| username | string | 登录成功时的用户名 |

#### 用户登录-错误响应示例

| 状态码 | 错误信息（detail）                                  | 说明                                   |
|--------|-----------------------------------------------------|----------------------------------------|
| 400    | Username and password are not null                   | 用户名或密码为空（含仅空格）           |
| 401    | Username or password are wrong                       | 用户名不存在或密码错误                 |
| 500    | Failed to connect database                          | 数据库连接失败                         |
| 500    | 登录失败: [具体异常信息]                            | 其他服务器错误（如SQL执行失败等）       |

### 用户注册

#### 用户注册-请求URL

POST /api/register

#### 用户注册-请求参数

| 参数名           | 类型   | 是否必填 | 说明                 |
|------------------|--------|----------|--------------------|
| username         | string | 是       | 用户名               |
| email            | string | 是       | 电子邮箱             |
| password         | string | 是       | 密码                 |
| confirm_password | string | 是       | 确认密码（二次输入） |

#### 用户注册-返回参数

| 字段名   | 类型   | 说明               |
| message  | string | 注册结果提示信息   |

#### 用户注册-错误响应示例

| 状态码 | 错误信息（detail）                                  | 说明                                   |
|--------|-----------------------------------------------------|----------------------------------------|
| 400    | Username,email,password and confirm_password are allowed to be null | 任意参数为空（含仅空格）               |
| 400    | Username already existed                            | 用户名已被注册                         |
| 400    | Email is already used                               | 邮箱已被使用                           |
| 400    | The password and confirm_password are different     | 两次输入的密码不一致                   |
| 500    | Failed to connect database                          | 数据库连接失败                         |
| 500    | 注册失败: [具体异常信息]                            | 其他服务器错误（如SQL执行失败等）       |

### 修改密码

#### 修改密码-请求URL

POST /api/change_password

#### 修改密码-请求参数

| 参数名        | 类型   | 是否必填 | 说明       |
|---------------|--------|----------|------------|
| username      | string | 是       | 用户名     |
| email         | string | 是       | 电子邮箱   |
| new_password  | string | 是       | 新密码     |

#### 修改密码-返回参数

| 字段名   | 类型   | 说明                 |
|----------|--------|----------------------|
| message  | string | 修改密码结果提示信息 |

#### 修改密码-错误响应示例

| 状态码 | 错误信息（detail）                                  | 说明                                   |
|--------|-----------------------------------------------------|----------------------------------------|
| 400    | Username,email and new_password are allowed to be null | 用户名、邮箱或新密码为空（含仅空格）   |
| 404    | Username or email wrong                             | 用户名或邮箱不匹配（验证失败）         |
| 400    | Change password unsuccessful                        | 密码更新操作未生效（无匹配用户）       |
| 500    | Failed to connect database                          | 数据库连接失败                         |
| 500    | 修改密码失败: [具体异常信息]                        | 其他服务器错误（如SQL执行失败等）       |

## 行程管理

### 收藏行程

#### 收藏行程-请求URL

POST /api/collect_trip

#### 收藏行程-请求参数

| 参数名   | 类型 | 是否必填 | 说明               |
|----------|------|----------|--------------------|
| user_id  | int  | 是       | 用户ID（整数类型） |
| trip_id  | int  | 是       | 行程ID（整数类型） |

#### 收藏行程-返回参数

| 字段名   | 类型   | 说明                 |
|----------|-------|----------------------|
| message  | string | 收藏行程结果提示信息 |

#### 收藏行程-错误响应示例

| 状态码 | 错误信息（detail）                                  | 说明                                   |
|--------|-----------------------------------------------------|----------------------------------------|
| 400    | User_id and trip_id are not allowed to be null       | user_id 或 trip_id 为空（未传值）      |
| 404    | user_id or trip_id not found                         | 未查询到匹配的用户ID或行程ID           |
| 400    | Collect trip unsuccessful                            | 收藏状态更新失败（无匹配数据可修改）   |
| 500    | Failed to connect database                          | 数据库连接失败                         |
| 500    | 收藏行程失败: [具体异常信息]                        | 其他服务器错误（如SQL执行失败等）       |

<br>
函数设计:
登录：Login()<br>

注册：Register()<br>
输入账号密码
,再次输入密码
,账号、密码是否符合格式（不为空）
,账号是否已存在
,注册成功

修改密码：ChangePassword()<br>
查找用户：FindUser()<br>
根据用户名查找，模糊查找<br>
返回匹配的用户名，头像url，邮箱<br>
删除用户：DeleteUser()<br>
只有管理员可以删除用户

发送信息：SendMessage()<br>

创建行程：CreateRoute()<br>

删除行程：DeleteRoute()<br>

修改行程：ChangeRoute()<br>

复制行程：CopyRoute()<br>

创建并发布公告：CreateNotice()<br>

删除公告：DeleteNotice()<br>

修改公告：ChangeNotice()<br>

创建并发布模板：CreateModel()<br>

删除模板：DeleteModel()<br>

修改模版：ChangeModel()<br>

