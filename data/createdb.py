import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from faker import Faker
import random
from datetime import timedelta

fake = Faker()

POSTGRES_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "ashween29",
}

MASTER_DB = "master"
CLIENT_DB = "client"
ROW_COUNT = 1000


# --------------------------------------------------
# DB UTILITIES
# --------------------------------------------------
def create_database(db_name):
    conn = psycopg2.connect(**POSTGRES_CONFIG, dbname="postgres")
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    cur.execute(f"SELECT 1 FROM pg_database WHERE datname='{db_name}'")
    exists = cur.fetchone()

    if not exists:
        cur.execute(f"CREATE DATABASE {db_name}")
        print(f"Created database: {db_name}")
    else:
        print(f"Database already exists: {db_name}")

    cur.close()
    conn.close()


def get_connection(db_name):
    return psycopg2.connect(**POSTGRES_CONFIG, dbname=db_name)


# --------------------------------------------------
# MASTER DATABASE (CANONICAL EHS)
# --------------------------------------------------
def setup_master():
    conn = get_connection(MASTER_DB)
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS action_tracker, trainings, risk_register, incidents, employees CASCADE")

    cur.execute("""
        CREATE TABLE employees (
            employee_id SERIAL PRIMARY KEY,
            full_name VARCHAR(150),
            department VARCHAR(120),
            job_title VARCHAR(120),
            email VARCHAR(150)
        )
    """)

    cur.execute("""
        CREATE TABLE incidents (
            incident_id SERIAL PRIMARY KEY,
            incident_date DATE,
            incident_category VARCHAR(100),
            site_location VARCHAR(200),
            severity VARCHAR(50),
            description TEXT,
            reported_by INT REFERENCES employees(employee_id)
        )
    """)

    cur.execute("""
        CREATE TABLE trainings (
            training_id SERIAL PRIMARY KEY,
            employee_id INT REFERENCES employees(employee_id),
            training_title VARCHAR(150),
            completion_date DATE,
            status VARCHAR(50)
        )
    """)

    cur.execute("""
        CREATE TABLE risk_register (
            risk_id SERIAL PRIMARY KEY,
            assessment_date DATE,
            hazard_type VARCHAR(120),
            hazard_description TEXT,
            risk_rating INT
        )
    """)

    cur.execute("""
        CREATE TABLE action_tracker (
            action_id SERIAL PRIMARY KEY,
            incident_id INT REFERENCES incidents(incident_id),
            action_item TEXT,
            owner VARCHAR(150),
            due_date DATE,
            action_status VARCHAR(50)
        )
    """)

    # ---------------- INSERT DATA ----------------
    for i in range(ROW_COUNT):
        cur.execute("""
            INSERT INTO employees (full_name, department, job_title, email)
            VALUES (%s, %s, %s, %s)
        """, (
            fake.name(),
            fake.job(),
            fake.job(),
            fake.email()
        ))

    for i in range(ROW_COUNT):
        cur.execute("""
            INSERT INTO incidents
            (incident_date, incident_category, site_location, severity, description, reported_by)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            fake.date_between("-2y", "today"),
            random.choice(["Injury", "Fire", "Spill", "Near Miss"]),
            fake.city(),
            random.choice(["Low", "Medium", "High", "Critical"]),
            fake.text(200),
            random.randint(1, ROW_COUNT)
        ))

    for i in range(ROW_COUNT):
        cur.execute("""
            INSERT INTO trainings
            (employee_id, training_title, completion_date, status)
            VALUES (%s, %s, %s, %s)
        """, (
            random.randint(1, ROW_COUNT),
            random.choice(["Fire Safety", "First Aid", "Hazard Awareness"]),
            fake.date_between("-1y", "today"),
            random.choice(["Completed", "Pending"])
        ))

    for i in range(ROW_COUNT):
        cur.execute("""
            INSERT INTO risk_register
            (assessment_date, hazard_type, hazard_description, risk_rating)
            VALUES (%s, %s, %s, %s)
        """, (
            fake.date_between("-2y", "today"),
            random.choice(["Chemical", "Electrical", "Mechanical"]),
            fake.text(150),
            random.randint(1, 10)
        ))

    for i in range(ROW_COUNT):
        cur.execute("""
            INSERT INTO action_tracker
            (incident_id, action_item, owner, due_date, action_status)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            random.randint(1, ROW_COUNT),
            fake.sentence(),
            fake.name(),
            fake.date_between("today", "+90d"),
            random.choice(["Open", "Closed", "In Progress"])
        ))

    conn.commit()
    cur.close()
    conn.close()
    print("Master database populated with 1000 rows per table")


# --------------------------------------------------
# CLIENT DATABASE (CUSTOMER SCHEMA)
# --------------------------------------------------
def setup_client():
    conn = get_connection(CLIENT_DB)
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS corrective_actions, safety_courses, hazard_assessment, incident_master, employee_info CASCADE")

    cur.execute("""
        CREATE TABLE employee_info (
            emp_code SERIAL PRIMARY KEY,
            emp_name VARCHAR(150),
            dept VARCHAR(120),
            designation VARCHAR(120),
            email_address VARCHAR(150)
        )
    """)

    cur.execute("""
        CREATE TABLE incident_master (
            inc_id SERIAL PRIMARY KEY,
            inc_date DATE,
            inc_type VARCHAR(100),
            plant_location VARCHAR(200),
            risk_level VARCHAR(50),
            inc_details TEXT,
            created_by INT REFERENCES employee_info(emp_code)
        )
    """)

    cur.execute("""
        CREATE TABLE safety_courses (
            course_id SERIAL PRIMARY KEY,
            emp_code INT REFERENCES employee_info(emp_code),
            course_name VARCHAR(150),
            course_date DATE,
            completion_flag VARCHAR(50)
        )
    """)

    cur.execute("""
        CREATE TABLE hazard_assessment (
            hazard_id SERIAL PRIMARY KEY,
            eval_date DATE,
            hazard_category VARCHAR(120),
            hazard_desc TEXT,
            score INT
        )
    """)

    cur.execute("""
        CREATE TABLE corrective_actions (
            action_ref SERIAL PRIMARY KEY,
            inc_id INT REFERENCES incident_master(inc_id),
            corrective_step TEXT,
            responsible_person VARCHAR(150),
            target_date DATE,
            status VARCHAR(50)
        )
    """)

    # ---------------- INSERT DATA ----------------
    for i in range(ROW_COUNT):
        cur.execute("""
            INSERT INTO employee_info (emp_name, dept, designation, email_address)
            VALUES (%s, %s, %s, %s)
        """, (
            fake.name(),
            fake.job(),
            fake.job(),
            fake.email()
        ))

    for i in range(ROW_COUNT):
        cur.execute("""
            INSERT INTO incident_master
            (inc_date, inc_type, plant_location, risk_level, inc_details, created_by)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            fake.date_between("-2y", "today"),
            random.choice(["Injury", "Fire", "Spill"]),
            fake.city(),
            random.choice(["Low", "Medium", "High"]),
            fake.text(200),
            random.randint(1, ROW_COUNT)
        ))

    for i in range(ROW_COUNT):
        cur.execute("""
            INSERT INTO safety_courses
            (emp_code, course_name, course_date, completion_flag)
            VALUES (%s, %s, %s, %s)
        """, (
            random.randint(1, ROW_COUNT),
            random.choice(["Fire Safety", "First Aid"]),
            fake.date_between("-1y", "today"),
            random.choice(["Y", "N"])
        ))

    for i in range(ROW_COUNT):
        cur.execute("""
            INSERT INTO hazard_assessment
            (eval_date, hazard_category, hazard_desc, score)
            VALUES (%s, %s, %s, %s)
        """, (
            fake.date_between("-2y", "today"),
            random.choice(["Chemical", "Mechanical"]),
            fake.text(150),
            random.randint(1, 10)
        ))

    for i in range(ROW_COUNT):
        cur.execute("""
            INSERT INTO corrective_actions
            (inc_id, corrective_step, responsible_person, target_date, status)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            random.randint(1, ROW_COUNT),
            fake.sentence(),
            fake.name(),
            fake.date_between("today", "+90d"),
            random.choice(["Open", "Closed"])
        ))

    conn.commit()
    cur.close()
    conn.close()
    print("Client database populated with 1000 rows per table")


# --------------------------------------------------
# MAIN
# --------------------------------------------------
if __name__ == "__main__":
    create_database(MASTER_DB)
    create_database(CLIENT_DB)

    setup_master()
    setup_client()

    print("Setup complete.")
