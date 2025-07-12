# n8n中使用PikPak下载服务指南

本指南将详细说明如何在n8n工作流中使用HTTP Request节点调用我们的PikPak下载服务。

## API接口信息

### 服务地址
- **Docker部署**: `http://localhost:8000` (默认)
- **自定义端口**: 修改`docker-compose.yml`中的端口映射
- **远程服务器**: `http://your-server-ip:8000`

**注意**: 如果修改了Docker端口映射，请相应调整URL中的端口号。

### 主要接口

#### 1. 健康检查接口
- **方法**: GET
- **路径**: `/`
- **用途**: 检查服务是否正常运行

#### 2. 添加下载任务接口
- **方法**: POST
- **路径**: `/download`
- **Content-Type**: `application/json`
- **请求体**:
```json
{
    "magnet_link": "magnet:?xt=urn:btih:your_magnet_link_here",
    "name": "可选的任务名称"
}
```
- **响应**:
```json
{
    "success": true,
    "message": "下载任务添加成功",
    "task_id": "任务ID"
}
```

#### 3. 查询任务列表接口
- **方法**: GET
- **路径**: `/tasks`
- **响应**: 返回当前所有下载任务的列表

## n8n配置步骤

### 步骤1: 添加HTTP Request节点

1. 在n8n工作流中添加一个"HTTP Request"节点
2. 配置节点参数如下：

### 步骤2: 配置添加下载任务

**基本配置**:
- **Method**: `POST`
- **URL**: `http://localhost:8000/download`
- **Authentication**: `None`
- **Send Headers**: `Yes`

**Headers配置**:
```
Content-Type: application/json
```

**Body配置**:
- **Body Content Type**: `JSON`
- **JSON**:
```json
{
    "magnet_link": "{{ $json.magnet_link }}",
    "name": "{{ $json.name || 'n8n下载任务' }}"
}
```

### 步骤3: 配置查询任务列表

**基本配置**:
- **Method**: `GET`
- **URL**: `http://localhost:8000/tasks`
- **Authentication**: `None`

## n8n工作流示例

### 示例1: 简单的磁力链接下载

```json
{
  "nodes": [
    {
      "parameters": {
        "method": "POST",
        "url": "http://localhost:8000/download",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {
              "name": "Content-Type",
              "value": "application/json"
            }
          ]
        },
        "sendBody": true,
        "bodyContentType": "json",
        "jsonBody": "{\n  \"magnet_link\": \"{{ $json.magnet_link }}\",\n  \"name\": \"{{ $json.name }}\"\n}"
      },
      "name": "添加PikPak下载任务",
      "type": "n8n-nodes-base.httpRequest"
    }
  ]
}
```

### 示例2: 带错误处理的完整工作流

1. **触发器节点** (Webhook/Manual Trigger)
2. **HTTP Request节点** - 添加下载任务
3. **IF节点** - 检查响应是否成功
4. **成功分支**: 发送成功通知
5. **失败分支**: 发送错误通知和重试逻辑

## 输入数据格式

在n8n中，确保输入数据包含以下字段：

```json
{
  "magnet_link": "magnet:?xt=urn:btih:example123456789abcdef&dn=example_file",
  "name": "我的下载文件"
}
```

## 错误处理

### 常见错误响应

1. **配置错误** (500):
```json
{
  "detail": "PikPak账户未配置，请设置PIKPAK_USERNAME和PIKPAK_PASSWORD环境变量"
}
```

2. **登录失败** (500):
```json
{
  "detail": "PikPak登录失败: Invalid username or password"
}
```

3. **磁力链接无效** (200但success为false):
```json
{
  "success": false,
  "message": "下载任务添加失败，请检查磁力链接"
}
```

### n8n错误处理配置

在HTTP Request节点中启用"Continue on Fail"选项，然后使用IF节点检查响应：

```javascript
// 检查HTTP状态码
{{ $node["HTTP Request"].json.success === true }}

// 或检查响应内容
{{ $json.success === true }}
```

## 高级用法

### 批量处理磁力链接

1. 使用"Split In Batches"节点处理多个磁力链接
2. 为每个链接调用下载API
3. 收集所有结果并生成报告

### 定时任务检查

1. 使用"Cron"节点定时触发
2. 调用`/tasks`接口获取任务状态
3. 根据任务状态发送通知或执行后续操作

### 与其他服务集成

- **Telegram Bot**: 接收磁力链接并自动下载
- **RSS监控**: 监控RSS源并自动下载新内容
- **文件管理**: 下载完成后自动整理文件

## 测试建议

1. **先测试健康检查**: 确保服务正常运行
2. **使用示例磁力链接**: 避免使用真实链接进行测试
3. **检查日志**: 查看服务端日志了解详细错误信息
4. **逐步调试**: 从简单的GET请求开始，再测试POST请求

## 安全注意事项

1. **网络访问**: 确保n8n能够访问PikPak服务
2. **认证信息**: 不要在n8n工作流中硬编码PikPak账户信息
3. **HTTPS**: 生产环境建议使用HTTPS
4. **访问控制**: 限制API访问权限

## 故障排除

### 连接问题
- 检查服务是否运行在正确端口
- 确认防火墙设置
- 验证网络连通性

### 认证问题
- 检查.env文件配置
- 验证PikPak账户信息
- 查看服务端日志

### 数据格式问题
- 确认Content-Type头部设置
- 检查JSON格式是否正确
- 验证磁力链接格式