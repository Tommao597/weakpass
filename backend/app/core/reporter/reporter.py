import json
from datetime import datetime
from typing import List, Dict


class ReportGenerator:
    """
    扫描报告生成器
    """

    def __init__(self, task_id: str, results: List[Dict]):
        self.task_id = task_id
        self.results = results
        self.time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def generate_summary(self):
        """
        统计结果
        """
        total = len(self.results)
        success = sum(1 for r in self.results if r.get("success"))
        failed = total - success

        return {
            "total_targets": total,
            "weak_password_found": success,
            "failed": failed
        }

    def generate_report(self):
        """
        生成完整报告
        """

        summary = self.generate_summary()

        report = {
            "task_id": self.task_id,
            "scan_time": self.time,
            "summary": summary,
            "results": self.results
        }

        return report

    def save_json(self, path: str):
        """
        保存JSON报告
        """

        report = self.generate_report()

        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4, ensure_ascii=False)

        return path

    def save_txt(self, path: str):
        """
        保存TXT报告
        """

        report = self.generate_report()

        with open(path, "w", encoding="utf-8") as f:

            f.write("Weak Password Scan Report\n")
            f.write("=" * 40 + "\n")
            f.write(f"Task ID: {report['task_id']}\n")
            f.write(f"Scan Time: {report['scan_time']}\n")

            f.write("\nSummary\n")
            f.write("-" * 20 + "\n")

            for k, v in report["summary"].items():
                f.write(f"{k}: {v}\n")

            f.write("\nResults\n")
            f.write("-" * 20 + "\n")

            for r in report["results"]:
                line = f"{r['host']}:{r['port']} {r['protocol']} "
                line += f"{r['username']}:{r['password']} "
                line += f"{'SUCCESS' if r['success'] else 'FAILED'}"
                f.write(line + "\n")

        return path