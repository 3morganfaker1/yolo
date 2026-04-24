# 基于 YOLOv13 的学生课堂行为智能检测系统

学生课堂行为智能监测项目，采用前后端分离与推理服务解耦架构：

- `Detection_vue`：前端可视化与交互（Vue3 + Vite + Element Plus）
- `Detection_springboot`：业务 API、用户与记录管理、文件上传（Spring Boot + MyBatis Plus）
- `Detection_flask`：YOLO 推理服务（图片/视频/摄像头检测、实时进度与消息推送）

---

## 1. 项目结构

```text
.
├── ClassDetection
│   ├── Detection_vue/          # 前端
│   ├── Detection_springboot/   # Java 后端
│   ├── Detection_flask/        # Python 推理服务
│   ├── yoloai.sql              # 数据库初始化脚本
│   └── 部署文档.pdf
├── SCB-Dataset/                # 数据集（已在 .gitignore 中忽略）
├── CONTRIBUTING.md             # 协作规范
└── .gitignore
```

---

## 2. 主要功能

- 图片检测（单图）
- 图片批量检测
- 视频检测（上传视频并返回处理结果）
- 摄像头检测（录制 -> 提交检测 -> 返回结果）
- 五态引导体验（空状态/已上传/处理中/成功/失败）
- 同页展示检测结果与 AI 建议
- 异常行为实时预警（Socket 消息）
- 历史记录查询与详情可视化

---

## 3. 环境要求

建议环境：

- Node.js >= 16
- npm >= 7
- JDK 8/11（推荐 8）
- Maven 3.8+
- Python 3.8+
- MySQL 8.x
- FFmpeg（系统可执行 `ffmpeg` 命令）

---

## 4. 数据库初始化

1. 创建数据库：`yolo`
2. 执行脚本：`ClassDetection/yoloai.sql`
3. 按需修改后端配置：
   - 文件：`ClassDetection/Detection_springboot/src/main/resources/application.properties`
   - 关键配置：
     - `spring.datasource.url`
     - `spring.datasource.username`
     - `spring.datasource.password`

> 默认后端端口：`9999`

---

## 5. 本地启动（推荐顺序）

### 5.1 启动 Spring Boot（业务后端）

```bash
cd ClassDetection/Detection_springboot
mvn spring-boot:run
```

启动后地址：`http://localhost:9999`

### 5.2 启动 Flask（YOLO 推理）

```bash
cd ClassDetection/Detection_flask
# 如果你已有本项目虚拟环境，可直接使用：
.venv/bin/python main.py
```

启动后地址：`http://127.0.0.1:5000`

### 5.3 启动 Vue 前端

```bash
cd ClassDetection/Detection_vue
npm install
npm run dev
```

默认访问：`http://localhost:8888`

---

## 6. 常用开发命令

### 前端

```bash
cd ClassDetection/Detection_vue
npm run dev
npm run build
```

### 后端

```bash
cd ClassDetection/Detection_springboot
mvn spring-boot:run
```

### 推理服务

```bash
cd ClassDetection/Detection_flask
.venv/bin/python main.py
```

---

## 7. Git 协作建议（多人开发）

请遵循仓库中的 `CONTRIBUTING.md`，核心约定：

- `main` 仅存放稳定代码
- 功能开发使用 `feature/*` 分支
- 小步提交，PR 合并到 `main`
- 不直接向 `main` 推送

建议工作流：

```bash
git checkout main
git pull origin main
git checkout -b feature/your-feature
# coding...
git add .
git commit -m "feat: your change"
git push -u origin feature/your-feature
```

---

## 8. 常见问题

- **Q: 摄像头/视频检测提交后没有结果？**  
  A: 确认 `SpringBoot(9999)` 与 `Flask(5000)` 同时运行，且数据库可用。

- **Q: 页面一直处理中？**  
  A: 检查 Flask 控制台是否报错，确认本机 `ffmpeg` 可执行、模型权重存在于 `Detection_flask/weights/`。

- **Q: 前端能打开但接口报错？**  
  A: 检查 `application.properties` 的数据库连接和后端端口配置。

---

## 9. 项目仓库

GitHub 仓库：<https://github.com/3morganfaker1/yolo>

