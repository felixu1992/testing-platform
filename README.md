# testing platform
自动化测试平台，基于原有的`Python`自动化测试系统升级优化，为解决以前添加用例不方便的痛点
## 技术栈
- Django
- MySQL
- Vue
- Redis
## 目录介绍
### backend
使用`Django`搭建的后端工程
### frontend

使用`Vue`构建的前端工程
### testing_platform
`Django`创建项目产生的目录，包含配置，模型，路径映射等等内容
## 功能规划

- [ ] 登录注册

  - [x] 登录功能
  - [ ] 注册功能

- [ ] 项目管理

  - [x] 项目分组

    分组的增加、删除、新增

  - [ ] 项目管理

    项目的增、删、改、查(删的时候连带删除报告)、复制项目、测试
    - [x] CRUD
    - [ ] 复制
    - [x] 执行测试

  - [ ] 接口管理

    接口的增、删、改、查、复制接口、测试、导入`Excel`
    - [x] CRUD
    - [ ] 复制
    - [x] 测试
    - [ ] 导入

- [x] 测试报告

  - [x] 报告管理

    查看、下载、删除

- [x] 文件管理

  - [x] 分组管理

    即增删改查功能

  - [x] 文件管理

    文件的上传、下载、列表查询、删除

- [x] 通讯录

  - [x] 分组管理

    分组的增删改查功能

  - [x] 通讯人员管理

    人员的增、删、改、查(被使用的无法删除、修改)

### 接口新增说明

#### 添加依赖字段
   - 可以选择以及添加过的行**看看能不能用 json 组件来做**
   - 自定义(`Excel`中的格式)
   - **数据结构**
     - 依赖字段：二维数组`[["aaa", "bbb"]]`
     - 注入值：
     ```json
     [
       {
         "depend": 1,
         "step": [
           "data",
           "total"
         ]
       }
     ]
     ```
#### 添加预期
   - 预期字段，固定输入
   - 预期值，可自定义(`Excel`中的格式)
   - 可选择某个接口的返回值，同样可以依赖`Json`
   - **预期字段和预期值数量必须相同**
   - **数据结构**
     - 预期字段：`["code", "total"]`
     - 预期值：
     ```json
     [
       {
         "steps": [
           "code"
         ],
         "value": "0"
       },
       {
         "depend": 1,
         "step": [
           "data",
           "total"
         ]
       }
     ]
     ```

#### 添加参数

   - 增加字段，新增字段，添加值

     - 字段固定，直接添加

     - 值添加，需要选择类型

       文件(从库里选)、数字(输入)、字符(输入)、数组(可组件添加输入)、结构体(继续跟之前一样添加字段，值重复)

## 表规划

1. 用户表
2. 操作记录(暂缓)
3. 项目表
4. 接口表
5. 通讯录分组
6. 通讯录人员
7. 文件分组
8. 文件
9. 测试报告

所有表都需要有拥有者，用`JWT`来做数据权限

## 部分设计

1. 关于登录，自行获取相关信息，添加到项目的`headers`或者`cookies`中，执行测试会进行注入，所以如果需要测试，且接口需要登录，请自行填充相关信息
2. 统一异常拦截
3. 统一返回，与`2`均使用`backend.middleware`中间件实现
4. 连接`Redis`做刷新`token`的事情，大可不必，就想连接一下`Redis`，啦啦啦啦啦      
5. 关于通知，如果项目开启通知，给拥有者发送完整测试报告，同时给开启接口通知的接口开发者，发送接口结果，如果项目关闭通知，则只通知开启的开发者，如果禁用通知，则完全不通知

## Note
- 用例支持延时执行     
- 用例依赖，直接用数组     
- 权限拦截加回来

## 运行
- `pip freeze > install.txt` 导出所有依赖     
- `pip install -r install.txt` 安装所有依赖
- 创建数据库`python manage.py makemigrations`
- `python manage.py migrate`
- `python manage.py runserver 0.0.0.0:port`
## 需要调整的点
- 排序规则      
- 新增用例时，算出最大排序 + 1 作为新的排序      
- 更新排序没实现     
- 对用例新增和修改时，参数格式的校验

- [ ] 用例名称、备注的梳理(优化)
- [ ] 项目、项目分组、分组筛选梳理(优化)
- [ ] 依赖参数依赖的接口变化是，显示有 bug(优化)
- [x] 新增、编辑用例后返回原位置(优化)
- [ ] 用例增加预期值时，缺少固定值嵌套校验(迭代)
- [x] 用例复制时，生成名称规则为原名称+随机串(优化)
- [ ] 没有增加校验参数时，应该默认通过，当前报错(bug)
- [ ] 单条用例执行，允许依赖，依赖时取执行依赖项(迭代)
- [ ] 编辑和新增用例时，参数和预期，显示依赖的接口名称