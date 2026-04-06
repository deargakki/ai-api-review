# System Prompt 模板
SYSTEM_PROMPT_API_DESIGNER = "You are an expert API designer with extensive experience in REST API design and OpenAPI specification. You have deep knowledge of API best practices, RESTful principles, and OpenAPI 3.0 specifications. You are precise, detail-oriented, and focused on creating high-quality, standards-compliant API documentation."

SYSTEM_PROMPT_API_REVIEWER = "You are an expert API reviewer with extensive experience in API design, versioning, and change management. You specialize in identifying breaking changes, analyzing API differences, and evaluating the impact of API modifications. You are thorough, precise, and skilled at categorizing changes by their severity and impact on existing clients."

# OpenAPI 生成 Prompt 模板
OPENAPI_GENERATION_PROMPT = """
Based on the following API Contract, generate a valid OpenAPI 3.0 specification.

API Contract:
{api_contract}

Design Principles:
1. Follow RESTful API design principles
2. Use proper HTTP methods (GET, POST, PUT, DELETE, PATCH)
3. Implement consistent naming conventions (snake_case for parameters, camelCase for request/response bodies)
4. Include comprehensive request/response schemas
5. Define appropriate error responses for all endpoints
6. Use proper status codes (200 OK, 201 Created, 400 Bad Request, 401 Unauthorized, 404 Not Found, 500 Internal Server Error)
7. Include necessary headers, query parameters, path parameters, and request bodies
8. Define security schemes if authentication is required
9. Use consistent YAML formatting with 2-space indentation
10. Ensure the specification is valid OpenAPI 3.0

Requirements:
1. Generate a complete OpenAPI 3.0 YAML specification
2. Include all API endpoints mentioned in the contract
3. Define appropriate request/response schemas for each endpoint
4. Include proper error responses for each endpoint
5. Pay special attention to structured information like headers, parameters, and response codes
6. Include all necessary components (schemas, security schemes, etc.)
7. Output only the OpenAPI YAML, no other text
8. Be consistent in your output format and structure
9. Ensure the specification is syntactically correct and semantically meaningful
10. Follow industry best practices for API design and documentation
"""

# OpenAPI 对比 Prompt 模板
OPENAPI_COMPARISON_PROMPT = """
Compare the following two OpenAPI specifications and identify the status of the generated API in the master specification.

Generated OpenAPI (from Confluence - contains a single API):
{generated_openapi}

Master OpenAPI (from GitHub - contains all APIs):
{master_openapi}

Review Principles:
1. Identify the API endpoint from the generated OpenAPI (e.g., /users, /products)
2. Check if this endpoint exists in the master OpenAPI
3. For existing endpoints, compare all aspects including:
   - HTTP methods (GET, POST, PUT, DELETE, PATCH)
   - Path parameters, query parameters, and request bodies
   - Response schemas and status codes
   - Headers and security requirements
4. Classify changes as:
   - Breaking Changes: Changes that would break existing clients (e.g., removing fields, changing parameter types, changing status codes)
   - Non-Breaking Changes: Changes that are backward compatible (e.g., adding optional fields, adding new endpoints)
5. Categorize breaking changes by severity:
   - Critical: Major breaking changes that will break most clients
   - High: Significant breaking changes that will break some clients
   - Medium: Minor breaking changes that may break a few clients
   - Low: Trivial breaking changes that are unlikely to break clients

Requirements:
1. Identify if the generated API is:
   - new: Not present in the master OpenAPI
   - modified: Present in the master OpenAPI but with changes
   - deleted: Present in the master OpenAPI but not in the generated OpenAPI
2. For modified APIs, identify all Breaking Changes and Non-Breaking Changes
3. Categorize each breaking change by severity
4. Provide clear, detailed descriptions of each change
5. Output in JSON format with the following strict structure:
{{
  "api_status": "new|modified|deleted",
  "breaking_changes": [
    {{
      "type": "string",
      "severity": "Critical|High|Medium|Low",
      "description": "string",
      "path": "string",
      "method": "string"
    }}
  ],
  "non_breaking_changes": [
    {{
      "type": "string",
      "description": "string",
      "path": "string",
      "method": "string"
    }}
  ],
  "summary": {{
    "total_changes": number,
    "breaking_changes": number,
    "non_breaking_changes": number
  }}
}}
6. Be consistent in your output format and structure
7. Ensure the JSON output is syntactically correct
8. Only output the JSON, no other text
"""
