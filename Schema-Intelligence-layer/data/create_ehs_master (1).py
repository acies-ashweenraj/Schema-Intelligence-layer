import psycopg2

DB_HOST = "localhost"
DB_PORT = 5433
DB_USER = "postgres"
DB_PASSWORD = "Admin"

SOURCE_DB = "ashween_master"


def create_database_if_not_exists(dbname: str):
    # connect to default postgres database first
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
    create_database_if_not_exists(SOURCE_DB)

    # now connect to ehs_master
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=SOURCE_DB
    )
    conn.autocommit = True
    cur = conn.cursor()

    # Drop tables
    cur.execute("""
    DROP TABLE IF EXISTS trainings CASCADE;
    DROP TABLE IF EXISTS inspections CASCADE;
    DROP TABLE IF EXISTS incidents CASCADE;
    DROP TABLE IF EXISTS employees CASCADE;
    DROP TABLE IF EXISTS departments CASCADE;
    DROP TABLE IF EXISTS locations CASCADE;
    """)

    # Create tables
    cur.execute("""
    CREATE TABLE locations (
        location_id SERIAL PRIMARY KEY,
        location_name VARCHAR(100) NOT NULL,
        country VARCHAR(50),
        state VARCHAR(50),
        created_at TIMESTAMP DEFAULT NOW()
    );

    CREATE TABLE departments (
        dept_id SERIAL PRIMARY KEY,
        dept_name VARCHAR(100) NOT NULL,
        location_id INT REFERENCES locations(location_id),
        manager_name VARCHAR(100),
        created_at TIMESTAMP DEFAULT NOW()
    );

    CREATE TABLE employees (
        emp_id SERIAL PRIMARY KEY,
        emp_name VARCHAR(100) NOT NULL,
        dept_id INT REFERENCES departments(dept_id),
        job_title VARCHAR(100),
        hire_date DATE
    );

    CREATE TABLE incidents (
        incident_id SERIAL PRIMARY KEY,
        emp_id INT REFERENCES employees(emp_id),
        incident_date DATE NOT NULL,
        incident_type VARCHAR(50),
        severity INT
    );

    CREATE TABLE inspections (
        inspection_id SERIAL PRIMARY KEY,
        location_id INT REFERENCES locations(location_id),
        inspection_date DATE NOT NULL,
        inspector_name VARCHAR(100),
        score INT
    );

    CREATE TABLE trainings (
        training_id SERIAL PRIMARY KEY,
        emp_id INT REFERENCES employees(emp_id),
        training_name VARCHAR(100),
        training_date DATE,
        status VARCHAR(20)
    );
    """)

    # Insert 1000 rows
    cur.execute("""
    INSERT INTO locations (location_name, country, state, created_at)
    SELECT
      'Location_' || gs,
      'USA',
      'State_' || (gs % 50),
      NOW() - (gs || ' days')::interval
    FROM generate_series(1,1000) gs;
    """)

    cur.execute("""
    INSERT INTO departments (dept_name, location_id, manager_name, created_at)
    SELECT
      'Dept_' || gs,
      (gs % 1000) + 1,
      'Manager_' || gs,
      NOW() - (gs || ' days')::interval
    FROM generate_series(1,1000) gs;
    """)

    cur.execute("""
    INSERT INTO employees (emp_name, dept_id, job_title, hire_date)
    SELECT
      'Employee_' || gs,
      (gs % 1000) + 1,
      'Job_' || (gs % 20),
      CURRENT_DATE - (gs % 3650)
    FROM generate_series(1,1000) gs;
    """)

    cur.execute("""
    INSERT INTO incidents (emp_id, incident_date, incident_type, severity)
    SELECT
      (gs % 1000) + 1,
      CURRENT_DATE - (gs % 365),
      'Type_' || (gs % 10),
      (gs % 5) + 1
    FROM generate_series(1,1000) gs;
    """)

    cur.execute("""
    INSERT INTO inspections (location_id, inspection_date, inspector_name, score)
    SELECT
      (gs % 1000) + 1,
      CURRENT_DATE - (gs % 365),
      'Inspector_' || (gs % 50),
      (gs % 100) + 1
    FROM generate_series(1,1000) gs;
    """)

    cur.execute("""
    INSERT INTO trainings (emp_id, training_name, training_date, status)
    SELECT
      (gs % 1000) + 1,
      'Training_' || (gs % 30),
      CURRENT_DATE - (gs % 365),
      CASE WHEN gs % 2 = 0 THEN 'COMPLETED' ELSE 'PENDING' END
    FROM generate_series(1,1000) gs;
    """)

    # Validate counts
    cur.execute("""
    SELECT 'locations' AS table_name, COUNT(*) FROM locations
    UNION ALL SELECT 'departments', COUNT(*) FROM departments
    UNION ALL SELECT 'employees', COUNT(*) FROM employees
    UNION ALL SELECT 'incidents', COUNT(*) FROM incidents
    UNION ALL SELECT 'inspections', COUNT(*) FROM inspections
    UNION ALL SELECT 'trainings', COUNT(*) FROM trainings;
    """)
    results = cur.fetchall()

    print("\n✅ ehs_master loaded successfully:")
    for row in results:
        print(row)

    cur.close()
    conn.close()


if __name__ == "__main__":
    run()
