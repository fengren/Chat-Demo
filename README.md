# AI Chat Demo

一个基于 LangChain/LangGraph 的 AI 对话演示项目，支持会话管理、记忆管理和流式响应。

## ✨ 功能特性

- 🤖 **智能对话**：基于 LangChain 和 LangGraph 构建的对话流程
- 💬 **会话管理**：支持多会话管理，每个会话独立存储消息历史
- 🧠 **记忆管理**：使用 mem0 进行智能记忆提取和管理
- 📡 **流式响应**：支持 Server-Sent Events (SSE) 流式输出
- 🎨 **现代化 UI**：基于 Vue3 + TypeScript 的 ChatGPT 风格界面
- 📊 **会话摘要**：自动生成会话标题（基于首次对话摘要）
- 🔍 **记忆检索**：根据对话内容智能检索相关记忆

## 🛠 技术栈

### 后端
- **框架**：FastAPI
- **AI 框架**：LangChain、LangGraph
- **LLM**：OpenAI 兼容 API
- **记忆管理**：mem0 (基于 Qdrant)
- **数据库**：PostgreSQL
- **ORM**：SQLAlchemy
- **数据库迁移**：Alembic
- **日志**：Python logging（支持文件日志和日志轮转）

### 前端
- **框架**：Vue 3 + TypeScript
- **构建工具**：Vite
- **路由**：Vue Router
- **状态管理**：Pinia
- **HTTP 客户端**：Fetch API

### 基础设施
- **容器化**：Docker Compose（PostgreSQL）

## 📁 项目结构

```
.
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── lang/           # LangChain/LangGraph 相关
│   │   │   ├── graph.py    # 对话图编排
│   │   │   ├── chains.py   # 提示链
│   │   │   ├── intent.py   # 意图识别
│   │   │   └── safety.py   # 内容安全
│   │   ├── routes/         # API 路由
│   │   │   ├── chat.py     # 聊天接口（流式/非流式）
│   │   │   ├── session.py  # 会话管理
│   │   │   └── memory.py   # 记忆管理
│   │   ├── services/       # 业务逻辑层
│   │   │   ├── session.py  # 会话服务
│   │   │   ├── message.py  # 消息服务
│   │   │   ├── memory.py   # 记忆服务
│   │   │   └── summary.py   # 摘要生成
│   │   ├── models/         # 数据模型
│   │   ├── config.py       # 配置管理
│   │   ├── main.py         # 应用入口
│   │   └── logging_config.py # 日志配置
│   ├── migrations/         # Alembic 数据库迁移
│   └── requirements.txt    # Python 依赖
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── components/    # Vue 组件
│   │   │   └── ChatWindow.vue
│   │   ├── stores/        # Pinia 状态管理
│   │   │   └── session.ts
│   │   ├── router.ts      # 路由配置
│   │   ├── App.vue        # 根组件
│   │   └── main.ts        # 入口文件
│   └── package.json
├── scripts/                # 脚本工具
│   └── dev.sh             # 开发启动脚本
└── README.md

```

## 🚀 快速开始

### 前置要求

- Python 3.12+
- Node.js 18+（推荐使用 pnpm）
- Docker & Docker Compose
- PostgreSQL（通过 Docker 运行）

### 1. 克隆项目

```bash
git clone <repository-url>
cd craft
```

### 2. 配置环境变量

在项目根目录创建 `.env` 文件：

```bash
# 后端服务配置
BACKEND_PORT=8000
CORS_ORIGINS=http://localhost:5173

# LLM 配置（OpenAI 兼容 API）
LLM_API_BASE=https://api.openai.com/v1
LLM_API_KEY=your-api-key
LLM_MODEL_CHAT=gpt-4o-mini

# 向量大模型配置（用于嵌入向量生成，可选）
# 如果不配置，将使用 LLM 配置作为备选
EMBEDDING_API_BASE=https://api.openai.com/v1
EMBEDDING_API_KEY=your-embedding-api-key
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIM=1536

# 数据库配置
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_chat

# Mem0 配置（可选，用于记忆管理）
MEM0_API_KEY=
MEM0_BASE_URL=
```

### 3. 启动 PostgreSQL

```bash
cd infra
docker compose up -d
```

### 4. 初始化数据库

```bash
cd backend
# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行数据库迁移
alembic upgrade head
```

### 5. 启动后端服务

```bash
# 在 backend 目录下
uvicorn app.main:app --reload --port 8000
```

后端服务将在 `http://localhost:8000` 启动。

### 6. 启动前端服务

```bash
cd frontend

# 安装依赖（使用 pnpm）
pnpm install

# 启动开发服务器
pnpm dev
```

前端服务将在 `http://localhost:5173` 启动。

### 使用开发脚本（推荐）

项目提供了便捷的开发脚本：

```bash
# 确保脚本有执行权限
chmod +x scripts/dev.sh

# 运行脚本（会自动启动后端）
./scripts/dev.sh
```

## 📖 API 文档

启动后端服务后，访问以下地址查看 API 文档：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 主要 API 端点

#### 聊天接口

- `POST /api/chat` - 非流式聊天
- `GET /api/chat/stream?q={query}&session_id={session_id}` - 流式聊天（SSE）

#### 会话管理

- `POST /api/sessions` - 创建新会话
- `GET /api/sessions` - 列出所有会话
- `GET /api/sessions/{session_id}` - 获取会话详情
- `GET /api/sessions/{session_id}/messages` - 获取会话消息历史
- `PUT /api/sessions/{session_id}/title` - 更新会话标题
- `DELETE /api/sessions/{session_id}` - 删除会话

#### 记忆管理

- `GET /api/memory/{session_id}` - 获取会话的所有记忆
- `GET /api/memory/{session_id}/search?q={query}` - 搜索相关记忆
- `DELETE /api/memory/{session_id}/{memory_id}` - 删除指定记忆

## 🔧 配置说明

### LLM 配置

项目支持任何 OpenAI 兼容的 API，包括：

- OpenAI API
- 本地部署的 OpenAI 兼容服务（如 LM Studio、vLLM 等）

配置方式：

```env
LLM_API_BASE=https://api.openai.com/v1  # API 基础 URL
LLM_API_KEY=sk-xxx                      # API 密钥
LLM_MODEL_CHAT=gpt-4o-mini              # 使用的模型名称
```

### 记忆管理配置

项目使用 mem0 进行记忆管理，mem0 使用 Qdrant 作为向量存储：

- **本地模式**：mem0 会自动在 `./mem0_data/qdrant` 目录创建本地 Qdrant 数据库
- **API 模式**：如需使用 mem0 云服务，配置 `MEM0_API_KEY` 和 `MEM0_BASE_URL`

### 数据库配置

确保 PostgreSQL 已启动，并配置正确的连接字符串：

```env
DATABASE_URL=postgresql://用户名:密码@主机:端口/数据库名
```

## 🧪 开发说明

### 数据库迁移

使用 Alembic 管理数据库迁移：

```bash
# 创建新迁移
alembic revision --autogenerate -m "描述信息"

# 应用迁移
alembic upgrade head

# 回退迁移
alembic downgrade -1
```

### 日志查看

日志文件位置：`backend/logs/app.log`

日志级别可在 `backend/app/logging_config.py` 中配置。

### 前端开发

前端使用 Vite 作为构建工具，支持热重载：

```bash
cd frontend
pnpm dev
```

## 🐛 常见问题

### 1. mem0 初始化失败

**问题**：`Unsupported vector store provider: chroma`

**解决**：mem0 当前版本只支持 `qdrant` 作为向量存储，配置已自动使用 Qdrant。

### 2. 数据库连接失败

**问题**：`sqlalchemy.exc.OperationalError`

**解决**：
- 确保 PostgreSQL 容器已启动：`docker compose ps`
- 检查 `DATABASE_URL` 配置是否正确
- 确认数据库已创建

### 3. 前端无法连接后端

**问题**：CORS 错误或网络请求失败

**解决**：
- 检查 `CORS_ORIGINS` 配置是否包含前端地址
- 确认后端服务已启动
- 检查 `vite.config.ts` 中的代理配置

### 4. 记忆未生成

**问题**：对话后记忆未添加到 mem0

**解决**：
- 检查日志文件 `backend/logs/app.log` 查看详细错误
- 确认 LLM_API_KEY 配置正确（记忆提取需要调用 LLM）
- 查看后端控制台输出的调试信息

## 📝 开发计划

- [ ] 支持用户认证和授权
- [ ] 集成外部 RAG 系统
- [ ] 支持多种向量数据库
- [ ] 添加对话导出功能
- [ ] 优化记忆提取算法
- [ ] 支持多模态输入（图片、文件等）

## 📄 许可证

[MIT License](LICENSE)

