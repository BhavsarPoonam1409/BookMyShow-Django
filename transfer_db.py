import os
import sqlite3
import psycopg2

SQLITE_DB = "db.sqlite3"
DATABASE_URL = os.environ["DATABASE_URL"]

sqlite_conn = sqlite3.connect(SQLITE_DB)
sqlite_conn.row_factory = sqlite3.Row
sqlite_cur = sqlite_conn.cursor()

pg_conn = psycopg2.connect(DATABASE_URL)
pg_cur = pg_conn.cursor()

sqlite_cur.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type='table'
    AND name NOT LIKE 'sqlite_%'
    AND name != 'django_migrations'
    ORDER BY name
""")

tables = [row["name"] for row in sqlite_cur.fetchall()]

print("Tables found:", len(tables))
print()

# Foreign key dependencies
pg_cur.execute("""
    SELECT
        tc.table_name,
        ccu.table_name AS foreign_table_name
    FROM information_schema.table_constraints AS tc
    JOIN information_schema.constraint_column_usage AS ccu
        ON tc.constraint_name = ccu.constraint_name
        AND tc.table_schema = ccu.table_schema
    WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_schema = 'public'
""")

dependencies = {}

for table, parent in pg_cur.fetchall():
    dependencies.setdefault(table, set()).add(parent)

ordered = []
remaining = set(tables)

while remaining:
    ready = []

    for table in remaining:
        deps = dependencies.get(table, set())
        deps = deps.intersection(remaining)

        if not deps:
            ready.append(table)

    if not ready:
        ordered.extend(sorted(remaining))
        break

    for table in sorted(ready):
        ordered.append(table)
        remaining.remove(table)

print("Starting transfer...")
print()

# Clear Render database
for table in reversed(ordered):
    try:
        pg_cur.execute(f'TRUNCATE TABLE "{table}" CASCADE')
    except Exception:
        pg_conn.rollback()

pg_conn.commit()

# Copy data
for table in ordered:

    sqlite_cur.execute(f'PRAGMA table_info("{table}")')
    sqlite_columns = sqlite_cur.fetchall()

    columns = [row["name"] for row in sqlite_columns]

    if not columns:
        continue

    # Find PostgreSQL boolean columns
    pg_cur.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = %s
        AND data_type = 'boolean'
    """, (table,))

    boolean_columns = {row[0] for row in pg_cur.fetchall()}

    sqlite_cur.execute(f'SELECT * FROM "{table}"')
    rows = sqlite_cur.fetchall()

    if not rows:
        print(f"{table}: 0")
        continue

    column_names = ", ".join(f'"{c}"' for c in columns)
    placeholders = ", ".join(["%s"] * len(columns))

    query = f'''
        INSERT INTO "{table}" ({column_names})
        VALUES ({placeholders})
    '''

    for row in rows:
        values = []

        for column, value in zip(columns, row):

            if column in boolean_columns:
                if value is None:
                    value = None
                else:
                    value = bool(value)

            values.append(value)

        pg_cur.execute(query, tuple(values))

    pg_conn.commit()

    print(f"{table}: {len(rows)}")

# Reset IDs
print()
print("Resetting IDs...")

for table in ordered:
    try:
        pg_cur.execute(f"""
            SELECT setval(
                pg_get_serial_sequence('"public"."{table}"', 'id'),
                COALESCE((SELECT MAX(id) FROM "{table}"), 1),
                true
            )
        """)
        pg_conn.commit()
    except Exception:
        pg_conn.rollback()

print()
print("================================")
print("TRANSFER COMPLETED SUCCESSFULLY")
print("================================")

sqlite_conn.close()
pg_conn.close()