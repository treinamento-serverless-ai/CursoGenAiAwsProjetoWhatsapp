import json
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TIMEZONE = ZoneInfo("America/Sao_Paulo")

def get_week_range(base_date, offset=0):
    """Retorna segunda e domingo da semana (offset: 0=atual, 1=próxima)"""
    days_since_monday = base_date.weekday()
    monday = base_date - timedelta(days=days_since_monday) + timedelta(weeks=offset)
    sunday = monday + timedelta(days=6)
    return monday.date(), sunday.date()

def get_month_range(base_date, offset=0):
    """Retorna primeiro e último dia do mês (offset: 0=atual, 1=próximo)"""
    month = base_date.month + offset
    year = base_date.year
    while month > 12:
        month -= 12
        year += 1
    first_day = datetime(year, month, 1, tzinfo=TIMEZONE).date()
    if month == 12:
        last_day = datetime(year, 12, 31, tzinfo=TIMEZONE).date()
    else:
        last_day = (datetime(year, month + 1, 1, tzinfo=TIMEZONE) - timedelta(days=1)).date()
    return first_day, last_day

def resolve_reference(reference, now):
    """Resolve referência temporal"""
    ref_upper = reference.upper().strip()
    
    if ref_upper == "TODAY":
        date = now.date()
        return {"type": "single", "date": str(date), "day_of_week": date.strftime("%A")}
    
    if ref_upper == "TOMORROW":
        date = (now + timedelta(days=1)).date()
        return {"type": "single", "date": str(date), "day_of_week": date.strftime("%A")}
    
    if "day" in ref_upper:
        parts = ref_upper.replace("days", "").replace("day", "").strip().split()
        if len(parts) == 1:
            offset = int(parts[0])
            date = (now + timedelta(days=offset)).date()
            return {"type": "single", "date": str(date), "day_of_week": date.strftime("%A")}
    
    if ref_upper == "CURRENT_WEEK":
        start, end = get_week_range(now, 0)
        return {"type": "range", "start_date": str(start), "end_date": str(end)}
    
    if ref_upper == "NEXT_WEEK":
        start, end = get_week_range(now, 1)
        return {"type": "range", "start_date": str(start), "end_date": str(end)}
    
    if "week" in ref_upper:
        parts = ref_upper.replace("weeks", "").replace("week", "").strip().split()
        if len(parts) == 1:
            offset = int(parts[0])
            start, end = get_week_range(now, offset)
            return {"type": "range", "start_date": str(start), "end_date": str(end)}
    
    if ref_upper == "CURRENT_MONTH":
        start, end = get_month_range(now, 0)
        return {"type": "range", "start_date": str(start), "end_date": str(end)}
    
    if ref_upper == "NEXT_MONTH":
        start, end = get_month_range(now, 1)
        return {"type": "range", "start_date": str(start), "end_date": str(end)}
    
    raise ValueError(f"Referência '{reference}' não suportada")

def convert_params_to_dict(params_list):
    """Convert Bedrock Agent parameter list to dictionary."""
    return {param.get("name"): param.get("value") for param in params_list if param.get("name")}

def lambda_handler(event, context):
    action_group = event.get('actionGroup')
    function_name = event.get('function')
    parameters = convert_params_to_dict(event.get('parameters', []))
    
    reference = parameters.get('reference')
    
    if not reference:
        return {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": action_group,
                "function": function_name,
                "functionResponse": {
                    "responseBody": {"TEXT": {"body": "Error: reference parameter is required."}}
                }
            }
        }
    
    try:
        now = datetime.now(TIMEZONE)
        result = resolve_reference(reference, now)
        
        if result["type"] == "single":
            result["start_date"] = None
            result["end_date"] = None
            date_obj = datetime.strptime(result["date"], "%Y-%m-%d")
            result["formatted_date"] = date_obj.strftime("%d/%m/%Y")
        else:
            result["date"] = None
            result["day_of_week"] = None
            start_obj = datetime.strptime(result["start_date"], "%Y-%m-%d")
            end_obj = datetime.strptime(result["end_date"], "%Y-%m-%d")
            result["formatted_range"] = f"{start_obj.strftime('%d/%m/%Y')} a {end_obj.strftime('%d/%m/%Y')}"
        
        result["reference"] = reference
        response_text = json.dumps(result, ensure_ascii=False)
        
        return {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": action_group,
                "function": function_name,
                "functionResponse": {
                    "responseBody": {"TEXT": {"body": response_text}}
                }
            }
        }
        
    except ValueError as e:
        error_msg = f"{str(e)}. Supported: TODAY, TOMORROW, +N days, CURRENT_WEEK, NEXT_WEEK, +N weeks, CURRENT_MONTH, NEXT_MONTH"
        return {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": action_group,
                "function": function_name,
                "functionResponse": {
                    "responseBody": {"TEXT": {"body": error_msg}}
                }
            }
        }
    except Exception as e:
        logger.error(f"Error resolving date reference: {e}")
        return {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": action_group,
                "function": function_name,
                "functionResponse": {
                    "responseBody": {"TEXT": {"body": f"Internal error: {str(e)}"}}
                }
            }
        }
