import io
import os
import time
from datetime import datetime

import numpy as np
from PIL import Image
import tensorflow as tf
from fastapi import FastAPI, File, UploadFile, HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor

# Cargar el modelo
model = tf.keras.models.load_model('modelo_cactus.h5')
print("✅ Modelo cargado. Input shape:", model.input_shape)

app = FastAPI(title="Cactus Detection API", version="2.0")

# ===========================================
# CONFIGURACIÓN DE BASE DE DATOS
# ===========================================
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "cactus"),
    "user": os.getenv("DB_USER", "cactus_user"),
    "password": os.getenv("DB_PASSWORD", "")
}

def get_db_connection():
    """Crea conexión a PostgreSQL via Cloud SQL Proxy."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"❌ Error conectando a BD: {e}")
        return None

def init_db():
    """Crea la tabla si no existe."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS predictions (
                        id SERIAL PRIMARY KEY,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        filename VARCHAR(255),
                        has_cactus INTEGER,
                        confidence FLOAT,
                        prediction_raw FLOAT
                    )
                """)
                conn.commit()
                print("✅ Tabla 'predictions' verificada/creada")
        except Exception as e:
            print(f"⚠️ Error creando tabla: {e}")
        finally:
            conn.close()

@app.on_event("startup")
async def startup_event():
    """Espera a que el proxy esté listo e inicializa la BD."""
    import asyncio
    for i in range(5):
        conn = get_db_connection()
        if conn:
            conn.close()
            init_db()
            print("✅ Conexión a BD establecida")
            return
        print(f"⏳ Esperando Cloud SQL Proxy... intento {i+1}/5")
        await asyncio.sleep(2)
    print("⚠️ No se pudo conectar a BD, continuando sin persistencia")

# ===========================================
# ENDPOINTS
# ===========================================

@app.get("/health")
async def health():
    db_status = "disconnected"
    conn = get_db_connection()
    if conn:
        db_status = "connected"
        conn.close()
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "database": db_status
    }

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen.")

    try:
        contents = await file.read()
        img = Image.open(io.BytesIO(contents)).convert("RGB")
        img = img.resize((32, 32))
        img_array = np.array(img) / 255.0
        img_flat = img_array.flatten().reshape(1, -1)

        prediction = model.predict(img_flat, verbose=0)[0][0]
        has_cactus = 1 if prediction > 0.5 else 0
        confidence = float(prediction) if has_cactus else float(1 - prediction)

        saved_to_db = False
        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO predictions (filename, has_cactus, confidence, prediction_raw)
                        VALUES (%s, %s, %s, %s)
                    """, (file.filename, has_cactus, confidence, float(prediction)))
                    conn.commit()
                    saved_to_db = True
                    print(f"✅ Predicción guardada: {file.filename}")
            except Exception as e:
                print(f"❌ Error guardando en BD: {e}")
            finally:
                conn.close()

        return {
            "filename": file.filename,
            "has_cactus": has_cactus,
            "confidence": round(confidence, 4),
            "prediction_raw": float(prediction),
            "saved_to_db": saved_to_db,
            "timestamp": time.time()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando la imagen: {str(e)}")

@app.get("/logs")
async def logs(limit: int = 10):
    conn = get_db_connection()
    if not conn:
        return {"message": "BD no disponible", "predictions": []}

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id, timestamp, filename, has_cactus, confidence, prediction_raw
                FROM predictions
                ORDER BY timestamp DESC
                LIMIT %s
            """, (limit,))
            predictions = cur.fetchall()
            for p in predictions:
                if p['timestamp']:
                    p['timestamp'] = p['timestamp'].isoformat()
        return {"count": len(predictions), "predictions": predictions}
    except Exception as e:
        return {"message": f"Error: {e}", "predictions": []}
    finally:
        conn.close()

@app.get("/")
async def root():
    return {
        "message": "API de detección de cactus v2.0 (con PostgreSQL)",
        "endpoints": {
            "health": "/health",
            "predict": "/predict (POST con imagen)",
            "logs": "/logs?limit=10"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)