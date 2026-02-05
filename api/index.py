# api/index.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import io
import pikepdf

app = FastAPI(title="PDF Compression Service")

# Enable CORS (allow your frontend origin)
app.add_middleware(
    CORSMiddleware,
     allow_origins=[
        "http://localhost:5173",   
        "http://127.0.0.1:5173",
        "https://pdf-utility-api-88dm.onrender.com",
        "https://pdf-utility-9tma.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/compress")
async def compress_pdf(file: UploadFile = File(...)):
    content = await file.read()
    with pikepdf.open(io.BytesIO(content)) as pdf:
        pdf.remove_unreferenced_resources()
        output = io.BytesIO()
        pdf.save(output, compress_streams=True)
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="compressed_{file.filename}"'}
    )

# Vercel serverless handler
handler = Mangum(app)