import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.core.tasks import create_detect_task, execute_detection, tasks
from app.core.database import task_dao, result_dao  # 导入数据库DAO
from app.models.schemas import DetectConfig
from app.utils.ip_parser import parse_targets

logger = logging.getLogger(__name__)
router = APIRouter()
UNSUPPORTED_PROTOCOLS = {"rdp"}


@router.post("/detect")
async def start_detection(config: DetectConfig, background_tasks: BackgroundTasks):
    try:
        targets = parse_targets(config.targets)
        logger.info("Parsed %s valid targets", len(targets))

        requested_protocols = {
            protocol.value if hasattr(protocol, "value") else str(protocol)
            for protocol in config.protocols
        }
        unsupported = sorted(requested_protocols & UNSUPPORTED_PROTOCOLS)
        if unsupported:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported protocols: {', '.join(unsupported)}",
            )

        if not targets:
            raise HTTPException(status_code=400, detail="No valid targets were provided")

        config.targets = targets
        task_id = await create_detect_task(config)

        task = tasks.get(task_id)
        if not task:
            raise HTTPException(status_code=500, detail="Failed to create detection task")

        task["targets"] = targets
        task["total_targets"] = len(targets)
        task["progress"] = 0

        background_tasks.add_task(execute_detection, task_id, config)

        return {
            "task_id": task_id,
            "status": "pending",
            "target_count": len(targets),
            "message": "Detection task started",
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to start detection task: %s", str(exc), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(exc)}")


@router.get("/task/{task_id}")
async def get_task_status(task_id: str):
    # 优先从数据库获取任务信息
    db_task = task_dao.get_task_by_id(task_id)
    if not db_task:
        # 如果数据库中没有，尝试从内存中获取（兼容性）
        task = tasks.serialize_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        return task
    
    # 从内存中获取实时状态信息
    memory_task = tasks.get(task_id)
    
    # 合并数据库和内存中的任务信息
    task_info = {
        "task_id": db_task["id"],
        "name": db_task["name"],
        "target": db_task["target"],
        "protocol": db_task["protocol"],
        "status": db_task["status"],
        "progress": db_task["progress"],
        "created_at": db_task["created_at"],
        "updated_at": db_task["updated_at"]
    }
    
    # 添加内存中的实时信息
    if memory_task:
        task_info.update({
            "current_target": memory_task.get("current_target"),
            "current_user": memory_task.get("current_user"),
            "current_password": memory_task.get("current_password"),
            "total": memory_task.get("total", 0),
            "percent": memory_task.get("percent", 0),
            "start_time": memory_task.get("start_time"),
            "completed_at": memory_task.get("completed_at"),
            "config": memory_task.get("config", {})
        })
    
    return task_info


@router.get("/tasks")
async def list_tasks():
    # 从数据库获取所有任务
    db_tasks = task_dao.get_all_tasks()
    
    # 转换为前端需要的格式
    task_list = []
    for db_task in db_tasks:
        task_info = {
            "id": db_task["id"],
            "name": db_task["name"],
            "target": db_task["target"],
            "protocol": db_task["protocol"],
            "status": db_task["status"],
            "progress": db_task["progress"],
            "created_at": db_task["created_at"],
            "updated_at": db_task["updated_at"]
        }
        
        # 添加内存中的实时信息
        memory_task = tasks.get(db_task["id"])
        if memory_task:
            task_info.update({
                "percent": memory_task.get("percent", 0),
                "start_time": memory_task.get("start_time"),
                "completed_at": memory_task.get("completed_at")
            })
        
        task_list.append(task_info)
    
    return {"tasks": task_list}


@router.get("/result/{task_id}")
async def get_result(task_id: str):
    # 检查任务是否存在
    db_task = task_dao.get_task_by_id(task_id)
    if not db_task:
        # 兼容性检查：如果数据库中没有，检查内存
        task = tasks.get(task_id)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        if task["status"] != "completed":
            raise HTTPException(
                status_code=400,
                detail=f"Task {task_id} is {task['status']}, result is not ready",
            )
        return {"task_id": task_id, "result": task["result"]}
    
    # 检查任务状态
    if db_task["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Task {task_id} is {db_task['status']}, result is not ready",
        )
    
    # 从数据库获取结果
    results = result_dao.get_results_by_task(task_id)
    
    # 转换为前端需要的格式
    formatted_results = []
    for result in results:
        formatted_results.append({
            "target": result["target"],
            "port": result["port"],
            "protocol": result["protocol"],
            "username": result["username"],
            "password": result["password"],
            "success": bool(result["success"]),
            "status": "weak" if result["success"] else "fail",
            "risk_level": result["risk_level"]
        })
    
    return {"task_id": task_id, "result": formatted_results}


@router.get("/progress/{task_id}")
async def get_progress(task_id: str):
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    return {
        "status": task.get("status", "unknown"),
        "progress": task.get("percent", 0),
        "current_target": task.get("current_target", ""),
        "current_user": task.get("current_user", ""),
        "current_password": task.get("current_password", ""),
    }


@router.post("/pause/{task_id}")
async def pause_task(task_id: str):
    ok = tasks.pause_task(task_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "task paused"}


@router.post("/resume/{task_id}")
async def resume_task(task_id: str):
    ok = tasks.resume_task(task_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "task resumed"}


@router.post("/stop/{task_id}")
async def stop_task(task_id: str):
    ok = tasks.stop_task(task_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "task stopped"}