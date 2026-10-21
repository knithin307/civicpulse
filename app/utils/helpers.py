from datetime import datetime, timezone

def get_utc_now():
    """
    Returns current UTC datetime as a naive datetime object
    compatible with SQLite and SQLAlchemy.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)
