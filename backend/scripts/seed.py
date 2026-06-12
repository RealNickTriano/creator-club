"""Seed the local dev database with test data.

Five creators with handles and bios, each with a small tier ladder and a feed
of posts (public, free-members-only, and paid, in varying lengths, plus the
odd draft), plus memberships: the seed users support each other, and every
real (non-seed) account is subscribed to a few creators so the home grid has
content when you sign in.

Idempotent: existing users (by ``google_sub``) are skipped, a creator who
already has tiers or posts keeps them untouched, and memberships go through
the service's upsert. Rerunning is safe.

Memberships are seeded directly through the service layer, so paid tiers skip
the simulated billing delay in :mod:`backend.billing`.

Run from ``backend/`` with the database up (``docker compose up -d``):

    uv run python scripts/seed.py
"""

import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db import SessionLocal
from backend.membership import service as membership_service
from backend.post import service as post_service
from backend.post.models import Post
from backend.post.schemas import NewPost, UpdatePost
from backend.tier import service as tier_service
from backend.tier.schemas import NewTier
from backend.user import service as user_service
from backend.user.models import User
from backend.user.schemas import NewUser, UpdateUser

# (creation data, profile) per user — the seed- prefix on google_sub marks
# these rows as test data and keys the rerun check.
SEED_USERS: list[tuple[NewUser, UpdateUser]] = [
  (
    NewUser(
      google_sub="seed-mayamakes",
      google_email="maya@example.com",
      google_name="Maya Lin",
    ),
    UpdateUser(
      handle="mayamakes",
      bio="Ceramics, slow process videos, and the occasional kiln disaster.",
    ),
  ),
  (
    NewUser(
      google_sub="seed-longgame",
      google_email="longgame@example.com",
      google_name="The Long Game",
    ),
    UpdateUser(
      handle="longgame",
      bio="A weekly essay on strategy, careers, and compounding decisions.",
    ),
  ),
  (
    NewUser(
      google_sub="seed-devdiaries",
      google_email="devdiaries@example.com",
      google_name="Dev Diaries",
    ),
    UpdateUser(
      handle="devdiaries",
      bio="Building in public: devlogs, postmortems, and code walkthroughs.",
    ),
  ),
  (
    NewUser(
      google_sub="seed-quietstudio",
      google_email="quietstudio@example.com",
      google_name="Quiet Studio",
    ),
    UpdateUser(
      handle="quietstudio",
      bio="Ambient music and field recordings, released a few tracks at a time.",
    ),
  ),
  (
    NewUser(
      google_sub="seed-pixelpoet",
      google_email="iris@example.com",
      google_name="Iris Vale",
    ),
    UpdateUser(
      handle="pixelpoet",
      bio="Pixel art studies and tiny interactive poems for the web.",
    ),
  ),
]

# Each creator's ladder, bottom rung first (rank = list index).
SEED_TIERS: dict[str, list[NewTier]] = {
  "mayamakes": [
    NewTier(name="Free", rank=0, price_cents=0, description="Public posts and studio updates."),
    NewTier(name="Supporter", rank=1, price_cents=500, description="Process videos and glaze notes."),
    NewTier(name="Insider", rank=2, price_cents=1200, description="Monthly live throwing sessions."),
  ],
  "longgame": [
    NewTier(name="Free", rank=0, price_cents=0, description="The occasional public essay."),
    NewTier(name="Member", rank=1, price_cents=800, description="Every weekly essay, plus the archive."),
    NewTier(name="All-Access", rank=2, price_cents=2000, description="Essays plus the monthly Q&A thread."),
  ],
  "devdiaries": [
    NewTier(name="Free", rank=0, price_cents=0, description="Devlog highlights."),
    NewTier(name="Supporter", rank=1, price_cents=400, description="Full postmortems and code walkthroughs."),
  ],
  "quietstudio": [
    NewTier(name="Free", rank=0, price_cents=0, description="A track each month."),
    NewTier(name="Supporter", rank=1, price_cents=300, description="Full releases and field-recording packs."),
    NewTier(name="Patron", rank=2, price_cents=1000, description="Stems, early mixes, and requests."),
  ],
  "pixelpoet": [
    NewTier(name="Free", rank=0, price_cents=0, description="Weekly pixel studies."),
    NewTier(name="Collector", rank=1, price_cents=600, description="Source files and interactive builds."),
  ],
}

@dataclass(frozen=True)
class SeedPost:
  """One post fixture; tier access is by rank so ids resolve at seed time."""

  title: str
  teaser: str
  body: str
  tier_rank: int | None = None  # None = public; else minimum rank to unlock
  days_ago: int | None = None  # publish offset from now; None leaves a draft


# Each creator's feed, mixing public, free-member, and paid posts, short and
# long bodies, staggered publish dates, and the odd unpublished draft.
SEED_POSTS: dict[str, list[SeedPost]] = {
  "mayamakes": [
    SeedPost(
      title="Studio tour: the new wheel",
      teaser="Finally rearranged the studio around the new kick wheel.",
      body=(
        "The new wheel landed last week and the whole studio shifted around"
        " it. The throwing corner now gets morning light, which sounds"
        " romantic until you realize it also means I can finally see how"
        " uneven my walls are.\n\nPhotos of the new layout below. The wedging"
        " table moved under the window and the glaze shelves are out of the"
        " splash zone for the first time ever."
      ),
      days_ago=12,
    ),
    SeedPost(
      title="Glaze test batch #14",
      teaser="Quick results from this week's test tiles.",
      body=(
        "Fourteen tiles in, the shino is still doing whatever it wants."
        " Tiles 3 and 7 came out beautifully; the rest crawled. Full recipe"
        " notes next week once I rerun the outliers."
      ),
      tier_rank=0,
      days_ago=10,
    ),
    SeedPost(
      title="Process video: trimming a teapot lid",
      teaser="Twenty minutes of real-time trimming, mistakes included.",
      body=(
        "This month's process video is up: trimming a teapot lid to fit a"
        " gallery I threw last week.\n\nI left in the part where I trimmed"
        " through the knob, because that is the actual lesson — how to read"
        " the sound of the tool just before it happens, and what to do with"
        " the lid afterwards instead of throwing it across the room."
      ),
      tier_rank=1,
      days_ago=8,
    ),
    SeedPost(
      title="Kiln disaster report: the bloated shelf",
      teaser="Cone 10 went fine. The kiln shelf did not.",
      body=(
        "I promised kiln disasters in the bio, so here is a proper one.\n\n"
        "Saturday's cone 10 firing looked textbook on the controller. When I"
        " opened the lid, the top shelf had bloated and sagged a full"
        " centimeter, taking four mugs and a vase with it. The culprit: a"
        " hairline crack I noticed two firings ago and decided to 'keep an"
        " eye on'.\n\nLessons, in order: a cracked shelf is a dead shelf;"
        " shelf wash hides cracks exactly as well as it hides everything"
        " else; and the vase, weirdly, survived with a lean I kind of love."
        "\n\nReplacement shelves arrive Thursday. The leaning vase is staying"
        " on my desk as a monument to procrastination."
      ),
      days_ago=6,
    ),
    SeedPost(
      title="Live throwing session: recap and next date",
      teaser="Recording from Tuesday's session, plus July's date.",
      body=(
        "Tuesday's live session recording is up — we threw matching bowls"
        " for an hour and only two of them are actually matching. July's"
        " session is on the 14th; bring questions about handles."
      ),
      tier_rank=2,
      days_ago=4,
    ),
    SeedPost(
      title="Glaze notes: copper red troubleshooting",
      teaser="Why your copper red fires grey, and the fixes that worked here.",
      body=(
        "Copper red is the glaze that taught me humility, so this month's"
        " notes are all about it.\n\nIf yours fires grey or liver-colored,"
        " the usual suspects in rough order: reduction starting too late,"
        " too much copper (more is not redder), and cooling too slowly"
        " through the 900s. My kiln wanted reduction from cone 010 and a"
        " copper carbonate cut from 0.5% to 0.3%.\n\nFull recipe, firing"
        " schedule, and tile photos attached. As always, your kiln will"
        " disagree with mine somewhere — log everything."
      ),
      tier_rank=1,
      days_ago=2,
    ),
    SeedPost(
      title="Spring sale planning",
      teaser="Dates and inventory plans for the spring studio sale.",
      body=(
        "Draft notes: aiming for the last weekend of the month, mugs and"
        " bowls mostly, seconds table for the kiln-disaster survivors."
      ),
      tier_rank=0,
    ),
  ],
  "longgame": [
    SeedPost(
      title="Why career bets compound",
      teaser="The math of small, repeated advantages over a decade.",
      body=(
        "A reader asked why I keep using the word 'compounding' for careers"
        " when careers pay no interest. Fair. Here is the long answer.\n\n"
        "A career bet compounds when its payoff makes the next bet cheaper:"
        " a skill that earns you harder projects, a reputation that earns"
        " you trust before you have proven anything, a network that surfaces"
        " opportunities you would never have found searching. None of these"
        " pay out linearly, and all of them decay if unused.\n\nThe"
        " practical version: prefer work that leaves a residue. Two jobs"
        " with identical salaries can differ enormously in what they leave"
        " behind in skills, reputation, and relationships.\n\nThis one is"
        " public because it is the thesis of the whole newsletter. The"
        " weekly essays work out the details."
      ),
      days_ago=21,
    ),
    SeedPost(
      title="The meeting you should stop attending",
      teaser="A simple audit for recurring meetings, and what to do after.",
      body=(
        "Every recurring meeting on your calendar is a bet that"
        " synchronizing is worth more than the work it displaces. Most of"
        " those bets were placed by someone else, years ago, for reasons"
        " nobody remembers.\n\nThe audit takes one week: for each recurring"
        " meeting, write one sentence after it ends about what changed"
        " because you were there. If the sentence is the same three weeks"
        " running — or you cannot write one — you have your answer.\n\nHow"
        " to actually leave gracefully is the second half of this essay."
      ),
      tier_rank=1,
      days_ago=14,
    ),
    SeedPost(
      title="Optionality is overrated",
      teaser="Keeping your options open has a price; mostly you pay it in focus.",
      body=(
        "The advice to 'keep your options open' is the most expensive free"
        " advice in careers.\n\nOptionality has carrying costs. Every option"
        " you keep open takes maintenance: the side credential, the network"
        " you ping quarterly, the plan B you rehearse. Each is cheap alone."
        " Together they are a tax on the focus that compounding requires"
        " — see the public essay on compounding if you missed it.\n\nThe"
        " uncomfortable claim: past a baseline of insurance, options trade"
        " against outcomes. The people with the most interesting careers I"
        " know closed doors early and deliberately.\n\nWhen optionality IS"
        " worth paying for — early career, volatile industries, bad"
        " managers — is the second half, plus a worksheet for pricing your"
        " own options honestly."
      ),
      tier_rank=1,
      days_ago=7,
    ),
    SeedPost(
      title="Reading list: Q2",
      teaser="Five books and three papers behind this quarter's essays.",
      body=(
        "The sources behind this quarter's essays, with a line on why each"
        " earned its place. No affiliate links, as always."
      ),
      tier_rank=0,
      days_ago=5,
    ),
    SeedPost(
      title="June Q&A thread",
      teaser="The monthly thread is open — careers, strategy, anything.",
      body=(
        "Ask anything below. I answer everything in the first 48 hours;"
        " last month's thread on negotiating a title change is linked at"
        " the top if you want the format."
      ),
      tier_rank=2,
      days_ago=3,
    ),
    SeedPost(
      title="Slow promotions, fast learning",
      teaser="When staying 'too long' at a level is the better trade.",
      body=(
        "Promotion velocity is the most legible career metric, which is"
        " exactly why it is over-optimized.\n\nThe argument this week: at"
        " certain levels, an extra year spent widening your base — shipping"
        " a second kind of project, failing at something recoverable — buys"
        " more than the year of title you gave up. The trick is telling"
        " strategic patience apart from comfortable drift, and there is a"
        " test for that inside."
      ),
      tier_rank=1,
      days_ago=1,
    ),
  ],
  "devdiaries": [
    SeedPost(
      title="Devlog week 1: the world is a grid again",
      teaser="Scrapped the polygon map. Back to tiles, and it feels great.",
      body=(
        "Week one of the rewrite. I scrapped the polygon-based map after"
        " two months of fighting it — pathfinding, serialization, and the"
        " editor were all harder than they needed to be.\n\nBack on a tile"
        " grid, I rebuilt in five days what took five weeks before. The"
        " lesson about choosing boring tech is one I apparently need to"
        " relearn every project."
      ),
      days_ago=30,
    ),
    SeedPost(
      title="Postmortem: the physics rewrite that ate March",
      teaser="A full accounting of the six-week detour, with numbers.",
      body=(
        "This is the long, honest version of what happened in March.\n\n"
        "The plan was a two-week swap of the physics engine. It took six."
        " The proximate cause was the collision layer assuming axis-aligned"
        " boxes in about forty places I had to find one at a time. The real"
        " cause was that I had no integration tests around physics at all,"
        " so every fix was verified by playing the game for ten minutes."
        "\n\nNumbers: 4,100 lines changed, 31 bugs filed against myself, 6"
        " weeks elapsed, 2 of which were the test harness I should have"
        " built first.\n\nWhat I would do differently, in order: write the"
        " harness first, swap subsystems behind a flag, and stop estimating"
        " rewrites by the size of the new code instead of the blast radius"
        " of the old.\n\nFull diff walkthrough and the harness code are"
        " below the fold."
      ),
      tier_rank=1,
      days_ago=25,
    ),
    SeedPost(
      title="Devlog week 2: doors",
      teaser="Doors are never just doors.",
      body=(
        "Spent the week on doors. Doors touch pathfinding, save state,"
        " sound, and the lighting system, because of course they do. They"
        " work now. Short update; the postmortem above explains where the"
        " time went."
      ),
      days_ago=23,
    ),
    SeedPost(
      title="Behind the scenes: my tooling setup",
      teaser="The build scripts, the level editor, and the one-key playtest loop.",
      body=(
        "Free members asked for a tooling tour, so here it is.\n\nThe core"
        " of it: one key rebuilds the changed module, hot-reloads assets,"
        " and drops me into the last room I was testing with the same seed."
        " Iteration time went from ninety seconds to four, and honestly the"
        " game got better the same week.\n\nThe level editor is an in-game"
        " mode, not a separate app — screenshots and the keybinding cheat"
        " sheet are attached."
      ),
      tier_rank=0,
      days_ago=18,
    ),
    SeedPost(
      title="Code walkthrough: the collision system",
      teaser="Swept AABB, spatial hashing, and the bugs between them — with code.",
      body=(
        "The promised collision walkthrough, start to finish.\n\nWe go"
        " through the broadphase first: a spatial hash with 64-pixel cells,"
        " chosen over a quadtree because the world is flat and entities are"
        " evenly sized. Then swept AABB for the narrow phase, and the"
        " corner-clipping bug that swept resolution famously invites — I"
        " hit it on day two and the fix is three lines you will want to"
        " understand rather than copy.\n\nAll code is in the companion"
        " repo, tagged by section. Timestamps in the video description if"
        " you only care about the tunneling fix."
      ),
      tier_rank=1,
      days_ago=12,
    ),
    SeedPost(
      title="Devlog week 3: enemies that flee",
      teaser="Flee behavior shipped, and it made combat 30% more interesting.",
      body=(
        "Enemies now flee when outmatched, which sounds minor and changed"
        " everything — fights have a second act now. Clip below. Next week:"
        " making them regroup instead of cowering in corners."
      ),
      days_ago=9,
    ),
    SeedPost(
      title="Postmortem: the save-file corruption bug",
      teaser="Three players lost saves. Here is the bug, the fix, and the apology.",
      body=(
        "The worst bug report a solo dev can get arrived Tuesday: 'my save"
        " is gone.' Three players were affected. This is the full account."
        "\n\nThe bug: saves are written atomically — write to a temp file,"
        " then rename. Except the temp file was on a different filesystem"
        " for players who moved their save directory, and rename across"
        " filesystems is a copy that can be interrupted. An update that"
        " shipped Monday made startup slower, widening the window, and a"
        " crash during it left a zero-byte save.\n\nThe fix is boring and"
        " correct: temp file beside the target, fsync before rename, and a"
        " rolling backup of the last three saves so this class of bug can"
        " never be total again.\n\nIf you were affected, check your email —"
        " I reconstructed what I could from the telemetry. I am sorry."
      ),
      tier_rank=1,
      days_ago=4,
    ),
    SeedPost(
      title="Devlog week 4: sound pass",
      teaser="Footsteps, room tone, and why silence was the hard part.",
      body=(
        "Draft — waiting on the new footstep recordings before this goes"
        " out. Notes so far on room tone and ducking the music in combat."
      ),
    ),
  ],
  "quietstudio": [
    SeedPost(
      title="New track: Overcast",
      teaser="Six minutes of tape loops and a broken chorus pedal.",
      body=(
        "This month's free track is up. Overcast came out of a tape loop"
        " that degraded in exactly the right way, plus a chorus pedal that"
        " only works when it rains. Stream link below."
      ),
      days_ago=16,
    ),
    SeedPost(
      title="Field notes: the harbor at dawn",
      teaser="Where the recordings on the next EP come from.",
      body=(
        "Spent three mornings at the harbor with the hydrophone and a"
        " thermos. The dawn ferry makes a chord I could not have written —"
        " hull resonance against the dock, low E against an almost-B.\n\n"
        "These recordings anchor the next EP. Notes on gear, placement, and"
        " the one take a gull ruined (kept it) are below for members."
      ),
      tier_rank=0,
      days_ago=11,
    ),
    SeedPost(
      title="Full release: Tide Tables EP",
      teaser="Four tracks built from the harbor sessions, out now for supporters.",
      body=(
        "Tide Tables is out — four tracks, twenty-six minutes, built almost"
        " entirely from the harbor recordings posted earlier.\n\nTrack notes:"
        " the ferry chord opens and closes the record; everything between is"
        " variations pulled from it by resampling and a lot of patience."
        " Lossless downloads and the field-recording pack are attached."
      ),
      tier_rank=1,
      days_ago=8,
    ),
    SeedPost(
      title="Stems and early mix: Overcast",
      teaser="All eight stems, plus the rejected first mix for comparison.",
      body=(
        "Patron post: all eight stems from Overcast, and the first mix I"
        " rejected — listening to them side by side is the whole lesson."
        " Requests thread for next month is open below."
      ),
      tier_rank=2,
      days_ago=5,
    ),
    SeedPost(
      title="Recording pack: rain on canvas",
      teaser="Forty minutes of rain on a canvas awning, in three intensities.",
      body=(
        "New field-recording pack: rain on the studio's canvas awning,"
        " light to heavy, forty minutes total, 24-bit. Licensed for your"
        " own work as usual."
      ),
      tier_rank=1,
      days_ago=2,
    ),
  ],
  "pixelpoet": [
    SeedPost(
      title="Weekly study: streetlight in fog",
      teaser="32x32, four colors, mostly about what to leave out.",
      body=(
        "This week's study: a streetlight in fog, 32x32, four colors. Fog"
        " is an exercise in restraint — the halo is two colors doing the"
        " work of twenty. Process gif below."
      ),
      days_ago=13,
    ),
    SeedPost(
      title="Sketchbook dump: May",
      teaser="Twenty unfinished things, some of which might become finished things.",
      body=(
        "Monthly sketchbook dump for members: twenty fragments from May."
        " The little rotating lighthouse near the end is the one I keep"
        " coming back to — it may turn into next month's interactive."
      ),
      tier_rank=0,
      days_ago=9,
    ),
    SeedPost(
      title="Tiny poem: 'refresh'",
      teaser="An interactive poem that changes every time you reload it.",
      body=(
        "New interactive: 'refresh' is a four-line poem where one word per"
        " line is redrawn from a small word bank on every page load. Some"
        " versions are better than the one I wrote. Play it at the link."
      ),
      days_ago=6,
    ),
    SeedPost(
      title="Source files: 'Lighthouse'",
      teaser="The .aseprite files and palette for the lighthouse piece.",
      body=(
        "Collector post: full source for 'Lighthouse' — layered .aseprite"
        " file, the palette, and the rejected color studies.\n\nThe layer"
        " stack is the interesting part: the rotation is four frames of the"
        " beam redrawn by hand, not a transform, and the file shows why"
        " that choice matters at this resolution."
      ),
      tier_rank=1,
      days_ago=5,
    ),
    SeedPost(
      title="Build notes: dithering in four colors",
      teaser="How the fog pieces get depth out of a four-color palette.",
      body=(
        "The long-promised dithering writeup.\n\nEverything in the fog"
        " series uses ordered dithering with hand-edited Bayer matrices —"
        " ordered rather than error-diffusion because at 32x32 every pixel"
        " is a decision, and diffusion makes decisions for you.\n\nThe"
        " walkthrough covers the three matrices I actually use, when to"
        " break the pattern deliberately (edges, light sources), and a"
        " side-by-side of the streetlight study with and without the"
        " hand-edits. Palette files attached.\n\nNext month: the same"
        " techniques at 16x16, where it all gets harder and better."
      ),
      tier_rank=1,
      days_ago=3,
    ),
    SeedPost(
      title="Weekly study: vending machine at night",
      teaser="The glow study everyone asked for after the streetlight.",
      body=(
        "By request after the streetlight piece: a vending machine at"
        " night, same four-color constraint. The hum is implied. Process"
        " gif and palette below for members."
      ),
      tier_rank=0,
      days_ago=1,
    ),
  ],
}

# (member handle, creator handle, tier rank) — the seed users support each
# other so creator pages and member lists aren't empty.
SEED_MEMBERSHIPS: list[tuple[str, str, int]] = [
  ("pixelpoet", "mayamakes", 0),
  ("mayamakes", "quietstudio", 1),
  ("devdiaries", "longgame", 1),
  ("quietstudio", "pixelpoet", 1),
  ("longgame", "devdiaries", 0),
]

# (creator handle, tier rank) given to every real (non-seed) account, so the
# signed-in dev sees a populated home grid.
DEV_MEMBERSHIPS: list[tuple[str, int]] = [
  ("mayamakes", 2),
  ("longgame", 2),
  ("devdiaries", 0),
  ("quietstudio", 1),
]


async def _seed_users(session: AsyncSession) -> dict[str, User]:
  """Create the seed users (skipping existing) and return them by handle."""
  users: dict[str, User] = {}
  for new_user, profile in SEED_USERS:
    assert profile.handle is not None
    user = await user_service.get_user_by_google_sub(session, new_user.google_sub)
    if user is None:
      user = await user_service.create_user(session, new_user)
      user = await user_service.update_user(session, user, profile)
      print(f"created @{profile.handle} ({new_user.google_name})")
    else:
      print(f"skipped @{profile.handle} (already seeded)")
    users[profile.handle] = user
  return users


async def _seed_tiers(session: AsyncSession, users: dict[str, User]) -> None:
  """Give each creator their ladder, leaving any existing ladder untouched."""
  for handle, ladder in SEED_TIERS.items():
    creator = users[handle]
    existing = await tier_service.list_tiers_by_user(session, creator.id)
    if existing:
      print(f"skipped tiers for @{handle} (already has {len(existing)})")
      continue
    for new_tier in ladder:
      await tier_service.create_tier(session, creator.id, new_tier)
    print(f"created {len(ladder)} tiers for @{handle}")


async def _seed_posts(session: AsyncSession, users: dict[str, User]) -> None:
  """Give each creator their feed, skipping creators who already have posts.

  Posts are created through the service (so they start as drafts) and then
  published by patching ``published_at``, mirroring the real authoring flow.
  """
  now = datetime.now(UTC)
  for handle, feed in SEED_POSTS.items():
    creator = users[handle]
    existing = await session.scalar(
      select(func.count()).select_from(Post).where(Post.user_id == creator.id)
    )
    if existing:
      print(f"skipped posts for @{handle} (already has {existing})")
      continue
    tiers = await tier_service.list_tiers_by_user(session, creator.id)
    tier_by_rank = {tier.rank: tier for tier in tiers}
    drafts = 0
    for seed_post in feed:
      post = await post_service.create_post(
        session,
        creator.id,
        NewPost(
          title=seed_post.title,
          teaser=seed_post.teaser,
          body=seed_post.body,
          required_tier_id=(
            tier_by_rank[seed_post.tier_rank].id
            if seed_post.tier_rank is not None
            else None
          ),
        ),
      )
      if seed_post.days_ago is None:
        drafts += 1
        continue
      await post_service.update_post(
        session,
        post,
        UpdatePost(published_at=now - timedelta(days=seed_post.days_ago)),
      )
    published = len(feed) - drafts
    suffix = f" + {drafts} draft{'s' if drafts != 1 else ''}" if drafts else ""
    print(f"created {published} posts{suffix} for @{handle}")


async def _join(
  session: AsyncSession, member: User, creator: User, rank: int
) -> None:
  """Upsert ``member``'s membership onto the creator's tier at ``rank``."""
  tiers = await tier_service.list_tiers_by_user(session, creator.id)
  tier = next(t for t in tiers if t.rank == rank)
  _, created = await membership_service.set_membership(
    session, member.id, creator.id, tier.id
  )
  verb = "joined" if created else "kept"
  member_name = f"@{member.handle}" if member.handle else member.google_email
  print(f"{member_name} {verb} @{creator.handle} ({tier.name})")


async def _seed_memberships(
  session: AsyncSession, users: dict[str, User]
) -> None:
  """Cross-subscribe the seed users, then subscribe every real account."""
  for member_handle, creator_handle, rank in SEED_MEMBERSHIPS:
    await _join(session, users[member_handle], users[creator_handle], rank)

  dev_users = (
    await session.scalars(select(User).where(~User.google_sub.like("seed-%")))
  ).all()
  for dev_user in dev_users:
    for creator_handle, rank in DEV_MEMBERSHIPS:
      await _join(session, dev_user, users[creator_handle], rank)


async def main() -> None:
  async with SessionLocal() as session:
    users = await _seed_users(session)
    await _seed_tiers(session, users)
    await _seed_posts(session, users)
    await _seed_memberships(session, users)


if __name__ == "__main__":
  asyncio.run(main())
