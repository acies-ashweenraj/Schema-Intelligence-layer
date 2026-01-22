import psycopg2

DB_HOST = "localhost"
DB_PORT = 5432
DB_USER = "postgres"
DB_PASSWORD = "ashween29"

TARGET_DB = "ehs_client"


def create_database_if_not_exists(dbname: str):
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname="postgres"
    )
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (dbname,))
    exists = cur.fetchone()

    if not exists:
        cur.execute(f"CREATE DATABASE {dbname};")
        print(f"✅ Database created: {dbname}")
    else:
        print(f"ℹ️ Database already exists: {dbname}")

    cur.close()
    conn.close()


def run():
    create_database_if_not_exists(TARGET_DB)

    # now connect to ehs_client
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=TARGET_DB
    )
    conn.autocommit = True
    cur = conn.cursor()

    # Drop tables in reverse FK order
    cur.execute("""
    DROP TABLE IF EXISTS learning_records CASCADE;
    DROP TABLE IF EXISTS audit_checks CASCADE;
    DROP TABLE IF EXISTS event_log CASCADE;
    DROP TABLE IF EXISTS staff CASCADE;
    DROP TABLE IF EXISTS org_units CASCADE;
    DROP TABLE IF EXISTS site_master CASCADE;
    """)

    # Create tables (different names vs source)
    cur.execute("""
    CREATE TABLE site_master (
        site_pk SERIAL PRIMARY KEY,
        site_title VARCHAR(100) NOT NULL,
        nation VARCHAR(50),
        region VARCHAR(50),
        created_on TIMESTAMP DEFAULT NOW()
    );

    CREATE TABLE org_units (
        unit_pk SERIAL PRIMARY KEY,
        unit_title VARCHAR(100) NOT NULL,
        site_fk INT REFERENCES site_master(site_pk),
        unit_head VARCHAR(100),
        created_on TIMESTAMP DEFAULT NOW()
    );

    CREATE TABLE staff (
        staff_pk SERIAL PRIMARY KEY,
        staff_fullname VARCHAR(100) NOT NULL,
        unit_fk INT REFERENCES org_units(unit_pk),
        role_name VARCHAR(100),
        joining_date DATE
    );

    CREATE TABLE event_log (
        event_pk SERIAL PRIMARY KEY,
        staff_fk INT REFERENCES staff(staff_pk),
        event_dt DATE NOT NULL,
        event_category VARCHAR(50),
        risk_level INT
    );

    CREATE TABLE audit_checks (
        audit_pk SERIAL PRIMARY KEY,
        site_fk INT REFERENCES site_master(site_pk),
        audit_dt DATE NOT NULL,
        auditor VARCHAR(100),
        audit_score INT
    );

    CREATE TABLE learning_records (
        learning_pk SERIAL PRIMARY KEY,
        staff_fk INT REFERENCES staff(staff_pk),
        course_name VARCHAR(100),
        course_dt DATE,
        completion_status VARCHAR(20)
    );
    """)

    # Insert 1000 rows into each table
    cur.execute("""
    INSERT INTO site_master (site_title, nation, region, created_on)
    SELECT
      'Site_' || gs,
      'USA',
      'Region_' || (gs % 50),
      NOW() - (gs || ' days')::interval
    FROM generate_series(1,1000) gs;
    """)

    cur.execute("""
    INSERT INTO org_units (unit_title, site_fk, unit_head, created_on)
    SELECT
      'Unit_' || gs,
      (gs % 1000) + 1,
      'Head_' || gs,
      NOW() - (gs || ' days')::interval
    FROM generate_series(1,1000) gs;
    """)

    cur.execute("""
    INSERT INTO staff (staff_fullname, unit_fk, role_name, joining_date)
    SELECT
      'Staff_' || gs,
      (gs % 1000) + 1,
      'Role_' || (gs % 20),
      CURRENT_DATE - (gs % 3650)
    FROM generate_series(1,1000) gs;
    """)

    cur.execute("""
    INSERT INTO event_log (staff_fk, event_dt, event_category, risk_level)
    SELECT
      (gs % 1000) + 1,
      CURRENT_DATE - (gs % 365),
      'Category_' || (gs % 10),
      (gs % 5) + 1
    FROM generate_series(1,1000) gs;
    """)

    cur.execute("""
    INSERT INTO audit_checks (site_fk, audit_dt, auditor, audit_score)
    SELECT
      (gs % 1000) + 1,
      CURRENT_DATE - (gs % 365),
      'Auditor_' || (gs % 50),
      (gs % 100) + 1
    FROM generate_series(1,1000) gs;
    """)

    cur.execute("""
    INSERT INTO learning_records (staff_fk, course_name, course_dt, completion_status)
    SELECT
      (gs % 1000) + 1,
      'Course_' || (gs % 30),
      CURRENT_DATE - (gs % 365),
      CASE WHEN gs % 2 = 0 THEN 'DONE' ELSE 'OPEN' END
    FROM generate_series(1,1000) gs;
    """)

    # Validate counts
    cur.execute("""
    SELECT 'site_master' AS table_name, COUNT(*) FROM site_master
    UNION ALL SELECT 'org_units', COUNT(*) FROM org_units
    UNION ALL SELECT 'staff', COUNT(*) FROM staff
    UNION ALL SELECT 'event_log', COUNT(*) FROM event_log
    UNION ALL SELECT 'audit_checks', COUNT(*) FROM audit_checks
    UNION ALL SELECT 'learning_records', COUNT(*) FROM learning_records;
    """)
    results = cur.fetchall()

    print("\n✅ ehs_client loaded successfully:")
    for row in results:
        print(row)

    cur.close()
    conn.close()


if __name__ == "__main__":
    run()
