from fastapi import FastAPI, HTTPException
import duckdb
import os

app = FastAPI()
db_path = os.environ.get('DUCKDB_DATABASE', '/data/database.db')
conn = duckdb.connect(db_path)

@app.get("/health")
def health_check():
    try:
        conn.execute("SELECT 1").fetchone()
        return {"status": "healthy"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
def execute_query(query: str):
    try:
        result = conn.execute(query).fetchall()
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/tables")
def list_tables():
    try:
        tables = conn.execute("SHOW TABLES").fetchall()
        return {"tables": tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/schemas")
def list_schemas():
    try:
        schemas = conn.execute("SHOW SCHEMAS").fetchall()
        return {"schemas": schemas}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
async def startup():
    # Load Delta Lake extension
    conn.execute("LOAD 'delta';")
    # Configure S3
    conn.execute("""
        SET s3_region='us-east-1';
        SET s3_endpoint='http://minio:9000';
        SET s3_access_key_id='minioadmin';
        SET s3_secret_access_key='minioadmin';
        SET s3_url_style='path';
    """)

@app.on_event("shutdown")
async def shutdown():
    conn.close() 