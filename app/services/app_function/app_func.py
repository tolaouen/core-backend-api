from sqlalchemy.orm import Session
from typing import Optional, List, Union
from fastapi import HTTPException, status
from collections import defaultdict

from app.models.app_function.app_func import AppFunction
from app.models.users.app_user import Apps
from app.schemas.app_function.app_func import AppFuncCreate, AppFuncUpdate, AppFunctionParentResponse, AppFuncResponse
from app.schemas.Responses.pagination import PaginatedResponse
from app.constants.constant import Is_ParentType
from app.utils.paginations import paginate
from app.utils.query_builder import build_query

class AppFuncService:
    def __init__(self, db: Session):
        self.db = db

    def get_app_function(
            self,
            page: int = 1,
            page_size: int = 10, 
            name: Optional[str] = None,
            code: Optional[str] = None,
            path: Optional[str] = None,
            app_id: Optional[int] = None,
            app_code: Optional[str] = None,
            status: Optional[str] = None
        ) -> PaginatedResponse[AppFunction]:

        query = self.db.query(AppFunction)

        filters = {}

        if name:
            filters[AppFunction.name] = name
        if code: 
            filters[AppFunction.code] = code
        if path:
            filters[AppFunction.path] = path
        if app_id:
            filters[AppFunction.app_id] = app_id
        if app_code:
            filters[AppFunction.app_code] = app_code
        if status:
            filters[AppFunction.status] = status

        query = build_query(query=query, filters=filters)

        return paginate(query, page=page, page_size=page_size)
        
    
    def get_app_function_by_id(self, function_id: int) -> Optional[AppFunction]:
        app_function = self.db.query(AppFunction).filter(AppFunction.id == function_id).first()

        if not app_function:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"App Function By ID {function_id} Not Found"
            )
        return app_function

    def get_apps_by_function_id(self, app_id: int) -> List[AppFunction]:
        apps = self.db.query(AppFunction).filter(AppFunction.app_id == app_id).all()

        if not apps:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No App Function Found."
            )

        return apps
    
    def create_app_function(self, data: AppFuncCreate) -> Optional[AppFunction]:
        item_data = data.model_dump()

        if data.app_id is not None:
            app = self.db.query(Apps).filter(Apps.id == data.app_id).first()
            if not app:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"App With ID {data.app_id} Not Found"
                )
            item_data["app_code"] = app.app_code

        item = AppFunction(**item_data)

        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)

        return item

    def update_app_function(self, function_id: int, data: AppFuncUpdate) -> Optional[AppFunction]:
        item = self.get_app_function_by_id(function_id)

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"App Function Update By ID {function_id} Not Found"
            )
        update_data = data.model_dump(exclude_unset=True)

        if data.app_id is not None:
            app = self.db.query(Apps).filter(Apps.id == data.app_id).first()
            if not app:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"App With ID {data.app_id} Not Found"
                )
            update_data["app_code"] = app.app_code


        for fields, value in update_data.items():
            setattr(item, fields, value)

        self.db.commit()
        self.db.refresh(item)

        return item
    
    def delete_app_function(self, function_id: int) -> Optional[AppFunction]:
        item = self.get_app_function_by_id(function_id)

        if not item:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND, 
                detail="App Function Not Found"
            )

        self.db.delete(item)
        self.db.commit()

        return item

    def get_app_function_response(
        self,
        app_code: str,
    ) -> List[Union[AppFunctionParentResponse, AppFuncResponse]]:
        app_functions = (
            self.db.query(AppFunction)
            .filter(AppFunction.app_code == app_code)
            .order_by(AppFunction.id)
            .all()
        )

        if not app_functions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="App Functions Not Found",
            )

        def key(function: AppFunction):
            return (function.parent_id, function.app_id, function.app_code)

        children_by_key = defaultdict(list)
        for function in app_functions:
            if function.is_parent == Is_ParentType.Child:
                children_by_key[key(function)].append(function)

        result: List[Union[AppFunctionParentResponse, AppFuncResponse]] = []
        parent_keys = set()

        for function in app_functions:
            if function.is_parent == Is_ParentType.Parent:
                parent_keys.add(key(function))
                result.append(
                    AppFunctionParentResponse(
                        **AppFuncResponse.model_validate(function).model_dump(),
                        subtitle=[
                            AppFuncResponse.model_validate(child)
                            for child in children_by_key.get(key(function), [])
                        ],
                    )
                )

        for function in app_functions:
            if (
                function.is_parent == Is_ParentType.Child
                and key(function) not in parent_keys
            ):
                result.append(AppFuncResponse.model_validate(function))

        return result