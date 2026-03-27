import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.core.tasks import create_detect_task, execute_detection, tasks
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
    task = tasks.serialize_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task


@router.get("/tasks")
async def list_tasks():
    return tasks.list_serialized_tasks()


@router.get("/result/{task_id}")
async def get_result(task_id: str):
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    if task["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Task {task_id} is {task['status']}, result is not ready",
        )
    return {"task_id": task_id, "result": task["result"]}


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
