from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pikpakapi import PikPakApi
import asyncio
import logging
from typing import Optional
import os

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PikPak Download Service", description="接收磁力链接并添加到PikPak下载任务的服务")

# 请求模型
class DownloadRequest(BaseModel):
    magnet_link: str
    name: Optional[str] = None

# 响应模型
class DownloadResponse(BaseModel):
    success: bool
    message: str
    task_id: Optional[str] = None

# PikPak客户端实例
pikpak_client = None
client_lock = asyncio.Lock()
is_client_ready = False

@app.on_event("startup")
async def startup_event():
    """应用启动时检查环境变量并初始化客户端"""
    global pikpak_client, is_client_ready
    
    username = os.getenv("PIKPAK_USERNAME")
    password = os.getenv("PIKPAK_PASSWORD")
    
    if not username or not password or username == "your_username_here" or password == "your_password_here":
        logger.warning("PikPak用户名或密码未正确设置，请配置真实的账户信息")
        logger.warning("服务已启动，但需要正确配置后才能正常工作")
        return
    
    logger.info("PikPak账户配置检查通过")
    
    # 严格按照官方文档流程初始化客户端
    try:
        async with client_lock:
            # 1. 创建客户端实例
            pikpak_client = PikPakApi(
                username=username,
                password=password
            )
            
            # 2. 登录
            await pikpak_client.login()
            logger.info("PikPak客户端登录成功")
            
            # 3. 刷新访问令牌
            await pikpak_client.refresh_access_token()
            logger.info("PikPak访问令牌刷新成功")
            
            is_client_ready = True
            logger.info("PikPak客户端初始化完成，服务已就绪")
            
    except Exception as e:
        logger.error(f"PikPak客户端初始化失败: {e}")
        pikpak_client = None
        is_client_ready = False
        logger.warning("服务已启动，但PikPak功能不可用")

async def get_pikpak_client():
    """获取已初始化的PikPak客户端"""
    global pikpak_client, is_client_ready
    
    if not is_client_ready or pikpak_client is None:
        raise HTTPException(
            status_code=503,
            detail="PikPak服务不可用，请检查配置或稍后重试"
        )
    
    return pikpak_client

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理资源"""
    logger.info("服务正在关闭...")

@app.get("/")
async def root():
    """健康检查接口"""
    return {"message": "PikPak下载服务运行中", "status": "healthy"}

@app.post("/download", response_model=DownloadResponse)
async def add_download_task(request: DownloadRequest):
    """添加下载任务接口"""
    try:
        # 获取已初始化的PikPak客户端
        client = await get_pikpak_client()
        
        # 添加离线下载任务
        task_name = request.name or "磁力链接下载任务"
        result = await client.offline_download(
            request.magnet_link,
            name=task_name
        )
        
        if result and 'task' in result:
            task_id = result['task'].get('id', 'unknown')
            logger.info(f"成功添加下载任务: {task_id}")
            return DownloadResponse(
                success=True,
                message="下载任务添加成功",
                task_id=task_id
            )
        else:
            logger.warning(f"下载任务添加可能失败: {result}")
            return DownloadResponse(
                success=False,
                message="下载任务添加失败，请检查磁力链接"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加下载任务时发生错误: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"添加下载任务失败: {str(e)}"
        )

@app.get("/tasks")
async def get_tasks():
    """获取下载任务列表"""
    try:
        # 获取已初始化的PikPak客户端
        client = await get_pikpak_client()
        
        tasks = await client.offline_list()
        return {"success": True, "tasks": tasks}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取任务列表时发生错误: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取任务列表失败: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    
    # 从环境变量获取主机和端口配置
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", "8000"))
    
    logger.info(f"启动服务: {host}:{port}")
    uvicorn.run(app, host=host, port=port)