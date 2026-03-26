from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import pandas as pd
import tempfile
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from app.core.tasks import tasks

router = APIRouter()


def format_results(results):
    """统一结果格式"""
    formatted = []

    for item in results:
        formatted.append({
            "目标": item.get("target", ""),
            "协议": item.get("protocol", ""),
            "用户名": item.get("username", ""),
            "密码": item.get("password", ""),
            "状态": item.get("status", "")
        })

    return formatted


@router.get("/export/{task_id}/pdf")
async def export_pdf(task_id: str):
    """导出PDF报告"""

    task = tasks.get(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="任务尚未完成")

    results = task.get("result", [])

    if not results:
        raise HTTPException(status_code=404, detail="没有扫描结果")

    formatted = format_results(results)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:

        doc = SimpleDocTemplate(tmp.name, pagesize=letter)
        styles = getSampleStyleSheet()

        elements = []

        # 标题
        title = Paragraph("弱口令检测报告", styles["Title"])
        elements.append(title)
        elements.append(Spacer(1, 20))

        # 表格数据
        data = [["目标", "协议", "用户名", "密码", "状态"]]

        for row in formatted:
            data.append([
                row["目标"],
                row["协议"],
                row["用户名"],
                row["密码"],
                row["状态"]
            ])

        table = Table(data)

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),

            ("ALIGN", (0, 0), (-1, -1), "CENTER"),

            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),

            ("GRID", (0, 0), (-1, -1), 1, colors.black)
        ]))

        elements.append(table)

        doc.build(elements)

        return FileResponse(
            tmp.name,
            media_type="application/pdf",
            filename=f"weakpass_report_{task_id}.pdf"
        )


@router.get("/export/{task_id}/excel")
async def export_excel(task_id: str):
    """导出Excel报告"""

    task = tasks.get(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="任务尚未完成")

    results = task.get("result", [])

    if not results:
        raise HTTPException(status_code=404, detail="没有扫描结果")

    formatted = format_results(results)

    df = pd.DataFrame(formatted)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:

        df.to_excel(tmp.name, index=False)

        return FileResponse(
            tmp.name,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=f"weakpass_report_{task_id}.xlsx"
        )