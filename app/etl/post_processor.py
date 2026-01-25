from typing import List, Dict, Any
from collections import defaultdict
from app.utils.logger import logger

class PersonioPostProcessor:
    """Generates secondary data products like summaries."""

    def generate_department_summary(self, employee_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calculates department-level statistics."""
        logger.info("Generating department summary...")
        
        dept_stats = defaultdict(lambda: {"count": 0, "total_salary": 0.0})
        
        for emp in employee_data:
            dept = emp.get("department") or "Unknown"
            salary = emp.get("Base Salary")
            
            # Clean salary value (handle strings, None, etc.)
            try:
                salary_val = float(salary) if salary is not None and str(salary).strip() != "" else 0.0
            except (ValueError, TypeError):
                salary_val = 0.0
                
            dept_stats[dept]["count"] += 1
            dept_stats[dept]["total_salary"] += salary_val
            
        summary = []
        for dept, stats in dept_stats.items():
            avg_salary = stats["total_salary"] / stats["count"] if stats["count"] > 0 else 0.0
            summary.append({
                "department": dept,
                "employee_count": stats["count"],
                "average_base_salary": round(avg_salary, 2)
            })
            
        # Sort by department name
        summary.sort(key=lambda x: x["department"])
        return summary
