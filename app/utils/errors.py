from datetime import datetime
from typing import Optional, List, Dict, Any


class APIError(Exception):
    """Base API Error class"""

    def __init__(self, code: str, message: str, status_code: int, details: Optional[Any] = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


class ParamsNotValidError(APIError):
    def __init__(self, param: str, value: Any, issue: str, expected_format: str = None):
        details = [{"param": param, "value": str(value), "issue": issue, "expectedFormat": expected_format}]
        super().__init__(
            code="PARAMS_NOT_VALID", message="URL parameter validation failed", status_code=400, details=details
        )


class BodyNotValidError(APIError):
    def __init__(self, validation_errors: List[Dict[str, Any]]):
        super().__init__(
            code="BODY_NOT_VALID", message="Request body validation failed", status_code=400, details=validation_errors
        )


class ResourceNotFoundError(APIError):
    def __init__(self, resource: str, identifier: Any, searched_by: str = "id"):
        details = {"resource": resource, "identifier": str(identifier), "searchedBy": searched_by}
        super().__init__(code="RESOURCE_NOT_FOUND", message=f"{resource} not found", status_code=404, details=details)


class PathNotFoundError(APIError):
    def __init__(self, path: str, available_endpoints: List[str] = None):
        details = {"message": "The requested endpoint does not exist"}
        if available_endpoints:
            details["availableEndpoints"] = available_endpoints

        super().__init__(
            code="PATH_NOT_FOUND", message="The requested endpoint does not exist", status_code=404, details=details
        )


class ServerError(APIError):
    def __init__(self, message: str = "An internal server error occurred", error_id: str = None):
        details = {"message": "Please try again later or contact support if the issue persists"}
        if error_id:
            details["errorId"] = error_id

        super().__init__(code="SERVER_ERROR", message=message, status_code=500, details=details)
