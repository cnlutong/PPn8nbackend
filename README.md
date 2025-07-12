# PikPak下载服务

一个基于FastAPI的HTTP服务，用于接收磁力链接请求并通过PikPak API添加下载任务。

## 功能特性

- 接收HTTP请求中的磁力链接
- 自动添加到PikPak网盘下载任务
- 24小时持续运行
- RESTful API接口
- 任务状态查询
- Docker容器化部署

## 快速开始（Docker部署）

### 1. 使用docker-compose（推荐）

1. 修改 `docker-compose.yml` 中的PikPak账户信息：

```yaml
environment:
  # 修改为你的真实账户信息
  - PIKPAK_USERNAME=your_actual_username
  - PIKPAK_PASSWORD=your_actual_password
  # 服务配置
  - SERVER_HOST=0.0.0.0
  - SERVER_PORT=8000
```

2. 启动服务：

```bash
docker-compose up -d
```

### 2. 直接使用Docker

```bash
docker build -t pikpak-service .
docker run -d -p 8000:8000 \
  -e PIKPAK_USERNAME=your_username \
  -e PIKPAK_PASSWORD=your_password \
  -e SERVER_HOST=0.0.0.0 \
  -e SERVER_PORT=8000 \
  pikpak-service
```

## API接口

### 1. 健康检查

```
GET /
```

返回服务状态信息。

### 2. 添加下载任务

```
POST /download
Content-Type: application/json

{
    "magnet_link": "magnet:?xt=urn:btih:...",
    "name": "可选的任务名称"
}
```

响应：

```json
{
    "success": true,
    "message": "下载任务添加成功",
    "task_id": "任务ID"
}
```

### 3. 查询任务列表

```
GET /tasks
```

返回当前的下载任务列表。

## 使用示例

### 使用curl添加下载任务

```bash
# 使用默认端口8000
curl -X POST "http://localhost:8000/download" \
     -H "Content-Type: application/json" \
     -d '{
       "magnet_link": "magnet:?xt=urn:btih:example",
       "name": "我的下载任务"
     }'

# 如果修改了SERVER_PORT，请相应调整端口号
```

### 使用Python requests

```python
import requests

url = "http://localhost:8000/download"
data = {
    "magnet_link": "magnet:?xt=urn:btih:example",
    "name": "我的下载任务"
}

response = requests.post(url, json=data)
print(response.json())
```

## 服务管理

### 查看服务状态

```bash
# 查看容器状态
docker-compose ps

# 查看服务日志
docker-compose logs -f
```

### 停止和重启服务

```bash
# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 重新构建并启动
docker-compose up -d --build
```

## 注意事项

1. 确保PikPak账户信息正确
2. 服务需要稳定的网络连接
3. 建议定期检查服务运行状态
4. 磁力链接格式需要正确

## 故障排除

- 检查日志输出获取详细错误信息
- 确认PikPak账户未被限制
- 验证网络连接正常
- 检查环境变量配置