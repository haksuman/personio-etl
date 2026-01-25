from typing import List, Dict, Any
from app.utils.logger import logger
from app.utils.errors import TransformationError

class PersonioTransformer:
    """Transforms nested Personio JSON data into flat structures for CSV."""

    def transform_employees(self, raw_employees: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Flattens employee data according to the specified schema."""
        flattened_data = []
        
        for emp in raw_employees:
            try:
                # The Personio API returns employee attributes in a 'attributes' dictionary
                # where each key is an attribute name and value is an object with 'value' key.
                attrs = emp.get("attributes", {})
                
                # Helper to extract value safely
                def get_val(key: str, default: Any = "") -> Any:
                    attr_obj = attrs.get(key, {})
                    if isinstance(attr_obj, dict):
                        val = attr_obj.get("value")
                        # Handle nested objects like department/position which might have 'label' or 'name'
                        if isinstance(val, dict):
                            return val.get("label") or val.get("name") or str(val)
                        return val if val is not None else default
                    return attr_obj if attr_obj is not None else default

                flat_emp = {
                    "employeeID": get_val("id"),
                    "First name": get_val("first_name"),
                    "Last name": get_val("last_name"),
                    "email": get_val("email"),
                    "status": get_val("status"),
                    "Hire date": self._format_date(get_val("hire_date")),
                    "Termination date": self._format_date(get_val("termination_date")),
                    "position": get_val("position"),
                    "department": get_val("department"),
                    "team": get_val("team"),
                    "Supervisor name": self._get_supervisor_name(attrs),
                    "location": get_val("office"),
                    "Weekly working hours": get_val("weekly_working_hours"),
                    "Employment type": get_val("employment_type"),
                    "Cost center": get_val("cost_centers"), # This might be a list in API
                    "Base Salary": get_val("fixed_salary"), # Usually needs extraction from compensation endpoint or attrs
                    "Last modified": get_val("last_modified_at")
                }
                flattened_data.append(flat_emp)
            except Exception as e:
                logger.error(f"Error transforming employee {emp.get('id')}: {e}")
                # We continue with other employees instead of failing the whole job
                
        return flattened_data

    def _format_date(self, date_str: Any) -> str:
        if not date_str:
            return ""
        # Personio usually returns ISO or YYYY-MM-DD
        # We ensure it's YYYY-MM-DD
        try:
            if isinstance(date_str, str) and "T" in date_str:
                return date_str.split("T")[0]
            return str(date_str)
        except Exception:
            return str(date_str)

    def _get_supervisor_name(self, attrs: Dict) -> str:
        supervisor = attrs.get("supervisor", {}).get("value", {})
        if isinstance(supervisor, dict):
            first = supervisor.get("first_name", "")
            last = supervisor.get("last_name", "")
            return f"{first} {last}".strip()
        return ""
