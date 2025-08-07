import aiosqlite

# --- New Database Schema (No Account Name) ---
async def setup_database(db: aiosqlite.Connection):
    """Sets up the necessary table if it doesn't exist."""
    await db.execute("""
        CREATE TABLE IF NOT EXISTS user_credentials (
            credential_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            email_address TEXT NOT NULL,
            password TEXT NOT NULL,
            UNIQUE(user_id, email_address) -- A user cannot store the same email twice
        )
    """)
    await db.commit()

async def set_user_credential(db: aiosqlite.Connection, user_id: int, email: str, password: str):
    """Inserts or replaces a user's credential based on the email address."""
    # The UNIQUE constraint on user_id and email_address handles the logic
    await db.execute(
        "INSERT OR REPLACE INTO user_credentials (user_id, email_address, password) VALUES (?, ?, ?)",
        (user_id, email, password)
    )
    await db.commit()

async def get_all_user_credentials(db: aiosqlite.Connection, user_id: int) -> list[tuple[str, str]]:
    """
    Retrieves all credentials for a specific user.
    Returns a list of (email, password) tuples.
    """
    # CORRECTED: Select both email_address and password
    async with db.execute(
        "SELECT email_address, password FROM user_credentials WHERE user_id = ?",
        (user_id,)
    ) as cursor:
        # This will now return the data in the correct format: [('email', 'pass'), ...]
        return await cursor.fetchall()
    
async def get_all_user_emails(db: aiosqlite.Connection, user_id: int) -> list:
    """Retrieves all credentials for a specific user."""
    # We only need to select the email address for listing/deleting
    async with db.execute("SELECT email_address FROM user_credentials WHERE user_id = ?", (user_id,)) as cursor:
        return await cursor.fetchall()

async def delete_user_credential(db: aiosqlite.Connection, user_id: int, email_address: str):
    """Deletes a specific user credential based on the email address."""
    await db.execute("DELETE FROM user_credentials WHERE user_id = ? AND email_address = ?", (user_id, email_address))
    await db.commit()