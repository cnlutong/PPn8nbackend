# 安全指南

本文档提供了使用PikPak下载服务时的安全最佳实践。

## 环境变量安全

### ⚠️ 重要提醒

1. **永远不要将真实的账户信息提交到版本控制系统**
2. **使用 `.env` 文件存储敏感信息时，确保它在 `.gitignore` 中**
3. **定期更换PikPak账户密码**
4. **不要在日志中输出敏感信息**

### 配置方式

#### 本地开发
```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env 文件，填入真实信息
# 注意：.env 文件已在 .gitignore 中，不会被提交
```

#### Docker部署
```bash
# 方式一：修改 docker-compose.yml 中的环境变量
# 注意：不要将包含真实密码的文件提交到公共仓库

# 方式二：使用环境变量文件（推荐）
docker-compose --env-file .env.prod up -d

# 方式三：通过命令行传递
docker run -e PIKPAK_USERNAME=xxx -e PIKPAK_PASSWORD=xxx ...
```

#### 生产环境
```bash
# 使用系统环境变量
export PIKPAK_USERNAME="your_username"
export PIKPAK_PASSWORD="your_password"

# 或使用密钥管理服务
# 如 AWS Secrets Manager, Azure Key Vault 等
```

## 网络安全

### 防火墙配置
```bash
# 只允许必要的端口访问
# 例如：只允许本地访问
sudo ufw allow from 127.0.0.1 to any port 8000

# 或允许特定IP段访问
sudo ufw allow from 192.168.1.0/24 to any port 8000
```

### HTTPS配置
```nginx
# 使用反向代理配置HTTPS
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 访问控制

### API密钥认证（可选实现）
```python
# 在生产环境中，考虑添加API密钥认证
from fastapi import Header, HTTPException

async def verify_api_key(x_api_key: str = Header()):
    if x_api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key
```

### IP白名单
```python
# 限制访问IP
from fastapi import Request
from fastapi.middleware.base import BaseHTTPMiddleware

class IPWhitelistMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, allowed_ips: list):
        super().__init__(app)
        self.allowed_ips = allowed_ips
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        if client_ip not in self.allowed_ips:
            raise HTTPException(status_code=403, detail="Access denied")
        return await call_next(request)
```

## 日志安全

### 敏感信息过滤
```python
# 确保日志中不包含敏感信息
import logging

class SensitiveDataFilter(logging.Filter):
    def filter(self, record):
        # 过滤敏感信息
        if hasattr(record, 'msg'):
            record.msg = str(record.msg).replace(password, '***')
        return True

logger.addFilter(SensitiveDataFilter())
```

## 容器安全

### Dockerfile最佳实践
```dockerfile
# 使用非root用户运行
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# 最小化镜像大小
FROM python:3.11-slim

# 设置安全的文件权限
COPY --chown=appuser:appuser . /app
```

### Docker Compose安全
```yaml
# 限制容器权限
security_opt:
  - no-new-privileges:true
read_only: true
cap_drop:
  - ALL
```

## 监控和审计

### 访问日志
```python
# 记录API访问
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(f"{request.client.host} - {request.method} {request.url} - {response.status_code} - {process_time:.2f}s")
    return response
```

### 异常监控
```python
# 监控异常情况
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

## 定期安全检查

### 检查清单
- [ ] 更新依赖包到最新版本
- [ ] 检查是否有敏感信息泄露
- [ ] 验证访问控制是否正常
- [ ] 检查日志是否包含敏感信息
- [ ] 确认防火墙规则正确
- [ ] 验证HTTPS证书有效性
- [ ] 检查容器安全配置

### 自动化安全扫描
```bash
# 使用安全扫描工具
pip install safety
safety check

# Docker镜像安全扫描
docker scan your-image:tag

# 代码安全扫描
pip install bandit
bandit -r .
```

## 应急响应

### 账户泄露处理
1. 立即更改PikPak账户密码
2. 检查账户异常活动
3. 更新所有部署环境的配置
4. 检查日志文件是否需要清理

### 服务异常处理
1. 立即停止服务
2. 检查日志确定问题原因
3. 修复安全问题
4. 重新部署服务
5. 监控服务状态

---

**记住：安全是一个持续的过程，需要定期检查和更新安全措施。**