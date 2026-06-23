"""Identity helpers for demo accounts.

A demo account is an ordinary ``users`` row with no Google identity: its
``google_sub`` is ``None`` and its ``google_email`` is a synthetic address on a
reserved domain that no real Google account can use. That reserved domain is
how a demo account is recognised after the fact (:func:`is_demo`) — there's no
schema flag.
"""

import uuid

from backend.user.models import User

# Synthetic demo emails live on this reserved domain. It isn't a routable mail
# domain, so a real Google sign-in can never produce an address on it — which
# makes the domain a reliable marker that an account is a demo.
DEMO_EMAIL_DOMAIN = "demo.creatorclub.local"

# Shown to the user (greetings, etc.) in place of the Google name a real signup
# would carry; a demo has no Google profile to draw one from.
DEMO_NAME = "Demo User"


def new_demo_email() -> str:
  """A unique synthetic email for a fresh demo account.

  The local part is a random token so concurrent demo logins never collide on
  the ``users.google_email`` unique constraint.
  """
  return f"demo-{uuid.uuid4().hex[:12]}@{DEMO_EMAIL_DOMAIN}"


def is_demo_email(email: str) -> bool:
  """Whether ``email`` is one of our synthetic demo addresses."""
  return email.endswith(f"@{DEMO_EMAIL_DOMAIN}")


def is_demo(user: User) -> bool:
  """Whether ``user`` is a demo account, recognised by its reserved email."""
  return is_demo_email(user.google_email)
