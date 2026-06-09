"""User profile routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.router import get_current_user
from backend.db import get_db
from backend.user import service as user_service
from backend.user.models import User
from backend.user.schemas import PrivateUser, PublicUser, UpdateUser

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/{handle}", response_model=PublicUser)
async def get_by_handle(
  handle: str,
  db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
  """Return the public profile for this handle, or 404 if no such user.

  Public (no auth): it backs the creator page at ``/c/{handle}``, which any
  visitor may land on. ``PublicUser`` exposes only viewer-safe fields.
  """
  user = await user_service.get_user_by_handle(db, handle)
  if user is None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
  return user


@router.patch("", response_model=PrivateUser)
async def update_me(
  update: UpdateUser,
  user: Annotated[User, Depends(get_current_user)],
  db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
  """Update the signed-in user's profile (e.g. claim a handle, edit the bio).

  ``handle`` is UNIQUE per the schema, so a clash is reported as 409 rather
  than surfacing as an unhandled server error.
  """
  try:
    return await user_service.update_user(db, user, update)
  except IntegrityError as exc:
    await db.rollback()
    raise HTTPException(
      status_code=status.HTTP_409_CONFLICT,
      detail="That handle is already taken.",
    ) from exc
