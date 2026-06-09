"""Tier routes — managing the current user's own ladder.

The owner always comes from the session, so there's no ``creatorId`` in these
paths; reading another creator's ladder happens via the creators routes.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.router import get_current_user
from backend.db import get_db
from backend.tier import service as tier_service
from backend.tier.models import Tier
from backend.tier.schemas import NewTier, PublicTier, UpdateTier
from backend.user import service as user_service
from backend.user.models import User

router = APIRouter(prefix="/tiers", tags=["tiers"])


async def get_owned_tier(
  tier_id: uuid.UUID,
  user: Annotated[User, Depends(get_current_user)],
  db: Annotated[AsyncSession, Depends(get_db)],
) -> Tier:
  """Resolve the tier and verify the session user owns it.

  404 if no such tier; 403 if it belongs to someone else. The shared guard for
  every ``/tiers/{tier_id}`` route, since they are all owner-only.
  """
  tier = await tier_service.get_tier_by_id(db, tier_id)
  if tier is None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
  if tier.user_id != user.id:
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
  return tier


@router.get("", response_model=list[PublicTier])
async def list_tiers(
  handle: str,
  db: Annotated[AsyncSession, Depends(get_db)],
) -> list[Tier]:
  """List a creator's tiers by handle, ordered by ``rank`` ascending.

  404 if no user has this handle. Public (no auth) for the same reason as
  ``GET /user/{handle}``: it backs the creator page any visitor may land on,
  and the ladder itself is viewer-safe.
  """
  user = await user_service.get_user_by_handle(db, handle)
  if user is None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
  return await tier_service.list_tiers_by_user(db, user.id)


@router.post("", response_model=PublicTier, status_code=status.HTTP_201_CREATED)
async def create_tier(
  new_tier: NewTier,
  user: Annotated[User, Depends(get_current_user)],
  db: Annotated[AsyncSession, Depends(get_db)],
) -> Tier:
  """Add a tier to the signed-in user's own ladder.

  ``name`` and ``rank`` are UNIQUE per owner, so a clash is reported as 409
  rather than surfacing as an unhandled server error.
  """
  try:
    return await tier_service.create_tier(db, user.id, new_tier)
  except IntegrityError as exc:
    await db.rollback()
    raise HTTPException(
      status_code=status.HTTP_409_CONFLICT,
      detail="You already have a tier with that name or rank.",
    ) from exc


@router.patch("/{tier_id}", response_model=PublicTier)
async def update_tier(
  update: UpdateTier,
  tier: Annotated[Tier, Depends(get_owned_tier)],
  db: Annotated[AsyncSession, Depends(get_db)],
) -> Tier:
  """Edit a tier (name, rank, price, description). Owner only."""
  try:
    return await tier_service.update_tier(db, tier, update)
  except IntegrityError as exc:
    await db.rollback()
    raise HTTPException(
      status_code=status.HTTP_409_CONFLICT,
      detail="You already have a tier with that name or rank.",
    ) from exc


@router.delete("/{tier_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tier(
  tier: Annotated[Tier, Depends(get_owned_tier)],
  db: Annotated[AsyncSession, Depends(get_db)],
) -> Response:
  """Remove a tier. Owner only.

  409 if memberships or posts still reference it (their foreign keys block the
  delete once those tables exist).
  """
  try:
    await tier_service.delete_tier(db, tier)
  except IntegrityError as exc:
    await db.rollback()
    raise HTTPException(
      status_code=status.HTTP_409_CONFLICT,
      detail="That tier is still referenced by memberships or posts.",
    ) from exc
  return Response(status_code=status.HTTP_204_NO_CONTENT)
