# 🌵 Manual de Usuario - Cactus Detection API

## ¿Qué es esta API?

Una API que recibe imágenes y detecta si contienen cactus usando inteligencia artificial.

---

## URL de la API

http://34.30.103.83

Copy

---

## Cómo usar la API

### 1️⃣ Verificar que la API funciona

**Comando:**
```bash
curl http://34.30.103.83/health
Respuesta esperada:

json
Copy
{
  "status": "healthy",
  "timestamp": 1769698622.08,
  "database": "connected"
}
✅ Si ves "database": "connected", todo funciona correctamente.

2️⃣ Hacer una predicción

Comando:

bash
Copy
curl -X POST -F "file=@tu_imagen.jpg" http://34.30.103.83/predict
⚠️ IMPORTANTE: Reemplaza tu_imagen.jpg por el nombre de una imagen que tengas en tu carpeta actual.
Ejemplo: si tienes foto.png en tu carpeta, el comando sería:
bash
Copy
curl -X POST -F "file=@foto.png" http://34.30.103.83/predict
Si recibes el error Failed to open/read local data from file, significa que el archivo no existe en tu carpeta.
Respuesta esperada:

json
Copy
{
  "filename": "tu_imagen.jpg",
  "has_cactus": 1,
  "confidence": 0.95,
  "prediction_raw": 0.95,
  "saved_to_db": true,
  "timestamp": 1769698622.08
}
¿Cómo interpretar el resultado?

Campo	Significado
has_cactus: 1	✅ La imagen SÍ tiene cactus
has_cactus: 0	❌ La imagen NO tiene cactus
confidence	Nivel de confianza (0 a 1, más alto = más seguro)
saved_to_db: true	La predicción se guardó en la base de datos
3️⃣ Ver historial de predicciones

Comando (últimas 10):

bash
Copy
curl http://34.30.103.83/logs
Comando (últimas 5):

bash
Copy
curl http://34.30.103.83/logs?limit=5
Requisitos

Terminal con curl instalado (Mac y Linux lo tienen por defecto)
Una imagen en formato JPG, PNG o similar
Autora

Ana Haique - Trabajo Final Computación en la Nube

