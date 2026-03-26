from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.models.schemas import DetectConfig
from app.core.tasks import create_detect_task, execute_detection, tasks
from app.utils.ip_parser import parse_targets  # 导入修复后的IP解析函数
import logging

# 初始化日志（方便调试和排查问题）
logger = logging.getLogger(__name__)
router = APIRouter() # 补充前缀和标签，规范接口路径


@router.post("/detect")
async def start_detection(config: DetectConfig, background_tasks: BackgroundTasks):
    """启动弱口令检测
    - 解析目标IP（支持单IP/CIDR网段/IP范围）
    - 创建检测任务并后台执行
    """
    try:
        # 1. 核心调用：解析目标IP列表（兼容字符串/列表输入）
        targets = parse_targets(config.targets)
        logger.info(f"解析目标IP完成，共解析出 {len(targets)} 个有效IP")

        # 2. 校验解析结果：无有效IP则返回400错误
        if not targets:
            raise HTTPException(status_code=400, detail="无有效目标IP，请检查输入格式（支持单IP/CIDR/IP范围）")

        # 3. 更新config：将解析后的合法IP写回配置
        config.targets = targets

        # 4. 创建检测任务（获取唯一task_id）
        task_id = await create_detect_task(config)

        # 5. 获取任务对象，记录关键信息（用于前端展示进度）
        task = tasks.get(task_id)
        if not task:  # 增加任务不存在的容错
            raise HTTPException(status_code=500, detail="任务创建失败，未找到任务ID")

        # 6. 记录目标信息到任务对象
        task["targets"] = targets
        task["total_targets"] = len(targets)
        task["progress"] = 0  # 初始化进度为0

        # 7. 后台执行检测任务（非阻塞，接口快速返回）
        background_tasks.add_task(execute_detection, task_id, config)

        # 8. 返回任务信息给前端
        return {
            "task_id": task_id,
            "status": "pending",
            "target_count": len(targets),  # 字段名更语义化（原targets易混淆）
            "message": "检测任务已启动"
        }

    except HTTPException as e:
        # 主动抛出的业务异常（如无有效IP），直接向上抛出
        raise e
    except Exception as e:
        # 捕获其他未知异常，记录日志并返回友好提示
        logger.error(f"启动检测任务失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"服务器内部错误：{str(e)}")


@router.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """获取任务状态（整体信息）"""
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")
    return task


@router.get("/tasks")
async def list_tasks():
    """列出所有任务"""
    # 修复：原代码可能是 tasks.tasks.values()，需确认tasks对象的结构
    # 如果tasks是字典，直接返回values()；如果是自定义对象，按需调整
    return list(tasks.values()) if isinstance(tasks, dict) else list(tasks.tasks.values())


@router.get("/result/{task_id}")
async def get_result(task_id: str):
    """获取检测结果（仅任务完成后返回）"""
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail=f"任务 {task_id} 状态为 {task['status']}，暂无法获取结果")
    return {"task_id": task_id, "result": task["result"]}  # 包装返回，结构更清晰


@router.get("/progress/{task_id}")
async def get_progress(task_id: str):
    """获取扫描进度（实时更新）"""
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")
    
    # 确保返回字段不为None，避免前端报错
    return {
        "status": task.get("status", "unknown"),
        "progress": task.get("percent", 0),
        "current_target": task.get("current_target", ""),
        "current_user": task.get("current_user", ""),
        "current_password": task.get("current_password", "")
    }
#暂停任务
@router.post("/pause/{task_id}")
async def pause_task(task_id: str):

    ok = tasks.pause_task(task_id)

    if not ok:
        raise HTTPException(404, "task not found")

    return {"message": "task paused"}

#继续任务
@router.post("/resume/{task_id}")
async def resume_task(task_id: str):

    ok = tasks.resume_task(task_id)

    if not ok:
        raise HTTPException(404, "task not found")

    return {"message": "task resumed"}

#取消任务
@router.post("/stop/{task_id}")
async def stop_task(task_id: str):

    ok = tasks.stop_task(task_id)

    if not ok:
        raise HTTPException(404, "task not found")

    return {"message": "task stopped"}