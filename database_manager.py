import psycopg2
import os
from dotenv import load_dotenv

# Carica le variabili d'ambiente dal file .env
load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

def save_aru_to_db(original_aru, revised_aru, aru_summary, ufp_results, supervisor_report, metadata):
    conn = get_db_connection()
    cursor = conn.cursor()
    insert_query = """
    INSERT INTO arus (original_aru, revised_aru, aru_summary, ufp_results, supervisor_report, metadata)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, (
        original_aru,
        revised_aru,
        aru_summary,
        ufp_results,
        supervisor_report,
        json.dumps(metadata)
    ))
    conn.commit()
    cursor.close()
    conn.close()

def get_all_arus():
    conn = get_db_connection()
    cursor = conn.cursor()
    select_query = "SELECT id, original_aru, revised_aru, aru_summary, ufp_results, supervisor_report, metadata FROM arus"
    cursor.execute(select_query)
    rows = cursor.fetchall()
    arus = []
    for row in rows:
        aru = {
            'id': row[0],
            'original_aru': row[1],
            'revised_aru': row[2],
            'aru_summary': row[3],
            'ufp_results': row[4],
            'supervisor_report': row[5],
            'metadata': json.loads(row[6])
        }
        arus.append(aru)
    cursor.close()
    conn.close()
    return arus
