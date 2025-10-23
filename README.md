# 启动项目

## 安装依赖
```bash
npm install
```
## 运行
```bash
npm run dev
```
### 关于前端的一点提示

前端的目录方面：
layout是布局，这个我先写的差不多，后面有需要在改，所有的页面都是围绕这个框架来的
pages是页面，点击布局中的导航栏实现路由跳转，显示不同的pages
router是路由控制，点开index.js看一看就知道，简单易懂
components是写可以复用的组件，比如搜索栏，模板卡片等等，我一开始嫌麻烦就把应该在layout/component的导航栏也写进去了，，，，
所有的图标都可以在上面找然后用mdi-icon就可以了 ：https://pictogrammers.com/library/mdi/