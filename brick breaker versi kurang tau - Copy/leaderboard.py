from Db import get_connection

def update_score(user_id, score):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET score = MAX(score, ?) WHERE id = ?", (score, user_id))
    conn.commit()
    conn.close()

def get_top_scores(limit=5):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT username, score FROM users ORDER BY score DESC LIMIT ?", (limit,))
    result = c.fetchall()
    conn.close()
    return result
