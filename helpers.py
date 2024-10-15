import sqlite3

def db(query, *args):
    """Execute a query with parameters and return the results."""
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute(query, args)  # Use args to substitute placeholders in the query
    results = c.fetchall()
    conn.commit()
    conn.close()
    return results
