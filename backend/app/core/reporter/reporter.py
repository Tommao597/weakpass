import json
from datetime import datetime
from typing import Dict, List


class ReportGenerator:
    def __init__(self, task_id: str, results: List[Dict]):
        self.task_id = task_id
        self.results = results
        self.time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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
        summary = self.generate_summary()

        return {
            "task_id": self.task_id,
            "scan_time": self.time,
            "summary": summary,
            "results": self.results,
        }

    def save_json(self, path: str):
        report = self.generate_report()

        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4, ensure_ascii=False)

        return path

    def save_txt(self, path: str):
        report = self.generate_report()

        with open(path, "w", encoding="utf-8") as f:
            f.write("Weak Password Scan Report\n")
            f.write("=" * 40 + "\n")
            f.write(f"Task ID: {report['task_id']}\n")
            f.write(f"Scan Time: {report['scan_time']}\n")

            f.write("\nSummary\n")
            f.write("-" * 20 + "\n")

            for key, value in report["summary"].items():
                f.write(f"{key}: {value}\n")

            f.write("\nResults\n")
            f.write("-" * 20 + "\n")

            for result in report["results"]:
                line = (
                    f"{result.get('target', '')}:{result.get('port', '')} "
                    f"{result.get('protocol', '')} "
                    f"{result.get('username', '')}:{result.get('password', '')} "
                    f"{'SUCCESS' if result.get('success') else 'FAILED'}"
                )
                f.write(line + "\n")

        return path
