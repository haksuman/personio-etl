import json
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
                            if not val:
                                return default
                            # Personio nested objects often have attributes with id and name/label
                            nested_attrs = val.get("attributes", {}) if isinstance(val, dict) else {}
                            return val.get("label") or val.get("name") or nested_attrs.get("name") or nested_attrs.get("label") or default
                        return val if val is not None else default
                    return attr_obj if attr_obj is not None else default

                # Extract department details for summary
                dept_info = self._extract_nested_info(attrs.get("department", {}).get("value"))
                
                flat_emp = {
                    "employeeID": get_val("id"),
                    "First name": get_val("first_name"),
                    "Last name": get_val("last_name"),
                    "email": get_val("email"),
                    "status": get_val("status"),
                    "Hire date": self._format_date(get_val("hire_date")),
                    "Termination date": self._format_date(get_val("termination_date")),
                    "position": get_val("position"),
                    "department": dept_info["name"],
                    "department_id": dept_info["id"],
                    "team": get_val("team"),
                    "Supervisor name": self._get_supervisor_name(attrs),
                    "location": get_val("office"),
                    "Weekly working hours": get_val("weekly_working_hours"),
                    "Employment type": get_val("employment_type"),
                    "Cost center": self._format_cost_centers(attrs),
                    "Base Salary": self._calculate_base_salary(attrs),
                    "Last modified": get_val("last_modified_at")
                }
                flattened_data.append(flat_emp)
            except Exception as e:
                logger.error(f"Error transforming employee {emp.get('id')}: {e}")
                # We continue with other employees instead of failing the whole job
                
        return flattened_data

    def _calculate_base_salary(self, attrs: Dict[str, Any]) -> float:
        """Calculates a monthly base salary from various salary attributes."""
        # 1. Try fixed salary
        fix_salary_obj = attrs.get("fix_salary", {})
        fix_salary = fix_salary_obj.get("value")
        
        interval_obj = attrs.get("fix_salary_interval", {})
        interval = interval_obj.get("value")
        
        if fix_salary is not None:
            try:
                val = float(fix_salary)
                if val > 0:
                    if interval == "monthly":
                        return val
                    elif interval == "yearly":
                        return val / 12.0
                    return val # Default to value if interval unknown or empty
            except (ValueError, TypeError):
                pass
            
        # 2. Try hourly salary as fallback
        hourly_salary_obj = attrs.get("hourly_salary", {})
        hourly_salary = hourly_salary_obj.get("value")
        
        weekly_hours_obj = attrs.get("weekly_working_hours", {})
        weekly_hours = weekly_hours_obj.get("value")
        
        if hourly_salary is not None:
            try:
                h_val = float(hourly_salary)
                if h_val > 0:
                    # Weekly working hours is often a string or number
                    w_val = float(weekly_hours) if weekly_hours else 40.0
                    # Monthly = hourly * weekly_hours * 4.33 (average weeks in a month)
                    return h_val * w_val * 4.33
            except (ValueError, TypeError):
                pass
            
        return 0.0

    def _format_cost_centers(self, attrs: Dict[str, Any]) -> str:
        """Extracts cost center names and returns them as a JSON array string."""
        cost_centers_obj = attrs.get("cost_centers", {})
        cost_centers_list = cost_centers_obj.get("value", [])
        
        if not isinstance(cost_centers_list, list):
            return "[]"
            
        names = []
        for cc in cost_centers_list:
            if isinstance(cc, dict):
                # Structure: {'type': 'CostCenter', 'attributes': {'id': 1970429, 'name': 'TestCostCenter3', ...}}
                cc_attrs = cc.get("attributes", {})
                name = cc_attrs.get("name")
                if name:
                    names.append(name)
        
        return json.dumps(names)

    def _extract_nested_info(self, val: Any) -> Dict[str, Any]:
        """Extracts ID and Name from nested Personio objects."""
        if not isinstance(val, dict):
            return {"id": "", "name": str(val) if val else ""}
            
        # Structure often looks like: {'type': 'Department', 'attributes': {'id': 123, 'name': 'Sales'}}
        nested_attrs = val.get("attributes", {})
        obj_id = nested_attrs.get("id") or val.get("id") or ""
        obj_name = nested_attrs.get("name") or nested_attrs.get("label") or val.get("name") or val.get("label") or ""
        
        return {"id": obj_id, "name": obj_name}

    def _format_date(self, date_str: Any) -> str:
        if not date_str:
            return ""
        # Personio usually returns ISO 8601 (e.g., 2026-01-24T00:00:00+01:00)
        # We ensure it's YYYY-MM-DD
        try:
            if isinstance(date_str, str):
                # Simple extraction of YYYY-MM-DD from start of string
                if len(date_str) >= 10 and date_str[4] == "-" and date_str[7] == "-":
                    return date_str[:10]
            return str(date_str)
        except Exception:
            return str(date_str)

    def _get_supervisor_name(self, attrs: Dict) -> str:
        supervisor = attrs.get("supervisor", {}).get("value", {})
        if isinstance(supervisor, dict):
            # Personio nested supervisor object has an 'attributes' dictionary
            sup_attrs = supervisor.get("attributes", {})
            if isinstance(sup_attrs, dict):
                # Try preferred_name first, then fallback to first_name + last_name
                preferred = sup_attrs.get("preferred_name", {}).get("value")
                if preferred:
                    return str(preferred).strip()
                
                first = sup_attrs.get("first_name", {}).get("value", "")
                last = sup_attrs.get("last_name", {}).get("value", "")
                return f"{first} {last}".strip()
        return ""
