# routers/admin.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.dependencies import get_current_admin, get_db
from app.models.user import User
from app.schemas.user import UserRead, UserUpdate, UserCreate
from app.services.auth_service import create_user, get_user_by_id, get_password_hash

router = APIRouter(prefix="/admin", tags=["Administration"])


@router.get("/users", response_model=List[UserRead])
def list_users(
    db: Session = Depends(get_db)
    current_user: User = Depends(get_current_admin),
):
    try:
        users = user_service.list_users(db)
        return users
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")



@router.get("/users/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
    current_user: User = Depends(get_current_admin),
):
    try:
        user = user_service.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
    current_user = Depends(get_current_admin),
):
    try:
        user_dict = user_data.model_dump()
        user = user_service.create_user(db, user_dict)

        logger.info(f"Admin {current_user.id} created user: {user.email} (ID: {user_id})")
        return user
    except ValueError as e:
        error_message = str(e)
        if error_message == "EMAIL_ALREADY_EXISTS":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        elif error_message == "NO_ROLES_SPECIFIED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one role is required"
            )
        logger.error(f"Validation error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bad request"
        )
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/users/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin),
):
    if user_id == current_user.id and user_update.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate yourself"
        )

    try:
        update_data = user_update.model_dump(exclude_unset=True)
        user = user_service.update_user(db, user_id, update_data)
        
        logger.info(f"Admin {current_user.id} updated user: {user.email} (ID: {user.id})")
        return user
        
    except ValueError as e:
        if str(e) == "USER_NOT_FOUND":
            raise HTTPException(status_code=404, detail="User not found")
        logger.error(f"Validation error updating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bad request"
        )
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin),
):
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )
    
    try:
        user_service.delete_user(db, user_id)
        
        logger.info(f"Admin {current_user.id} deleted user ID: {user_id}")
        return None
        
    except ValueError as e:
        if str(e) == "USER_NOT_FOUND":
            raise HTTPException(status_code=404, detail="User not found")
        logger.error(f"Validation error deleting user: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bad request"
        )
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/roles", response_model=List[RoleRead])
def list_roles(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin),
):
    try:
        return user_service.list_roles(db)
    except Exception as e:
        logger.error(f"Error listing roles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )