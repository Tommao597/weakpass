import os
import tempfile

import pandas as pd
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from starlette.background import BackgroundTask

from app.core.tasks import tasks

router = APIRouter()


def format_results(results):
    formatted = []

    for item in results:
        formatted.append(
            {
                "Target": item.get("target", ""),
                "Protocol": item.get("protocol", ""),
                "Username": item.get("username", ""),
                "Password": item.get("password", ""),
                "Status": item.get("status", ""),
            }
        )

    return formatted


@router.get("/export/{task_id}/pdf")
async def export_pdf(task_id: str):
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
        elements.append(Paragraph("Weak Password Report", styles["Title"]))
        elements.append(Spacer(1, 20))

        data = [["Target", "Protocol", "Username", "Password", "Status"]]
        for row in formatted:
            data.append(
                [
                    row["Target"],
                    row["Protocol"],
                    row["Username"],
                    row["Password"],
                    row["Status"],
                ]
            )

        table = Table(data)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )

        elements.append(table)
        doc.build(elements)

        return FileResponse(
            tmp.name,
            media_type="application/pdf",
            filename=f"weakpass_report_{task_id}.pdf",
            background=BackgroundTask(os.unlink, tmp.name),
        )


@router.get("/export/{task_id}/excel")
async def export_excel(task_id: str):
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
            filename=f"weakpass_report_{task_id}.xlsx",
            background=BackgroundTask(os.unlink, tmp.name),
        )
