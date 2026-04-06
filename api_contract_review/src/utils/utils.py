import json

def parse_json(json_str):
    """解析 JSON 字符串"""
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"JSON 解析错误: {e}")
        return None

def format_response(data, success=True, message=""):
    """格式化响应数据"""
    return {
        "success": success,
        "message": message,
        "data": data
    }

def validate_required_fields(data, required_fields):
    """验证必需字段"""
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return False, f"缺少必需字段: {', '.join(missing_fields)}"
    return True, ""
