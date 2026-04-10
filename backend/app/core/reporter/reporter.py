import json
import os
from datetime import datetime
from typing import Dict, List

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from openpyxl import Workbook


class ReportGenerator:
    def __init__(self, task_id: str, results: List[Dict]):
        self.task_id = task_id
        self.results = results
        self.time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # ⭐ 报告目录
        self.base_dir = "reports"
        os.makedirs(self.base_dir, exist_ok=True)

    # ================= 基础数据 =================
    def generate_summary(self):
        total = len(self.results)
        success = sum(1 for r in self.results if r.get("success"))
        failed = total - success

        return {
            "total_targets": total,
            "weak_password_found": success,
            "failed": failed,
        }

    def generate_report(self):
        return {
            "task_id": self.task_id,
            "scan_time": self.time,
            "summary": self.generate_summary(),
            "results": self.results,
        }

    # ================= JSON =================
    def save_json(self):
        path = os.path.join(self.base_dir, f"{self.task_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.generate_report(), f, indent=4, ensure_ascii=False)
        return path

    # ================= TXT =================
    def save_txt(self):
        path = os.path.join(self.base_dir, f"{self.task_id}.txt")
        report = self.generate_report()

        with open(path, "w", encoding="utf-8") as f:
            f.write("Weak Password Scan Report\n")
            f.write("=" * 40 + "\n")
            f.write(f"Task ID: {report['task_id']}\n")
            f.write(f"Scan Time: {report['scan_time']}\n\n")

            f.write("Summary\n")
            f.write("-" * 20 + "\n")
            for k, v in report["summary"].items():
                f.write(f"{k}: {v}\n")

            f.write("\nResults\n")
            f.write("-" * 20 + "\n")
            for r in report["results"]:
                line = (
                    f"{r.get('target')}:{r.get('port')} "
                    f"{r.get('protocol')} "
                    f"{r.get('username')}:{r.get('password')} "
                    f"{'SUCCESS' if r.get('success') else 'FAILED'}"
                )
                f.write(line + "\n")

        return path

    # ================= PDF =================
    def save_pdf(self):
        path = os.path.join(self.base_dir, f"{self.task_id}.pdf")
        report = self.generate_report()

        doc = SimpleDocTemplate(path)
        styles = getSampleStyleSheet()
        content = []

        content.append(Paragraph("Weak Password Scan Report", styles["Title"]))
        content.append(Spacer(1, 10))

        content.append(Paragraph(f"Task ID: {report['task_id']}", styles["Normal"]))
        content.append(Paragraph(f"Scan Time: {report['scan_time']}", styles["Normal"]))
        content.append(Spacer(1, 10))

        content.append(Paragraph("Summary", styles["Heading2"]))
        for k, v in report["summary"].items():
            content.append(Paragraph(f"{k}: {v}", styles["Normal"]))

        content.append(Spacer(1, 10))
        content.append(Paragraph("Results", styles["Heading2"]))

        for r in report["results"]:
            line = (
                f"{r.get('target')}:{r.get('port')} "
                f"{r.get('protocol')} "
                f"{r.get('username')}:{r.get('password')} "
                f"{'SUCCESS' if r.get('success') else 'FAILED'}"
            )
            content.append(Paragraph(line, styles["Normal"]))

        doc.build(content)
        return path

    # ================= Excel =================
    def save_excel(self):
        path = os.path.join(self.base_dir, f"{self.task_id}.xlsx")
        report = self.generate_report()

        wb = Workbook()
        ws = wb.active
        ws.title = "Report"

        # 表头
        ws.append(["Target", "Port", "Protocol", "Username", "Password", "Status"])

        for r in report["results"]:
            ws.append([
                r.get("target"),
                r.get("port"),
                r.get("protocol"),
                r.get("username"),
                r.get("password"),
                "SUCCESS" if r.get("success") else "FAILED"
            ])

        wb.save(path)
        return path

    # ================= 一键生成 =================
    def generate_all(self):
        self.save_json()
        self.save_txt()
        self.save_pdf()
        self.save_excel()