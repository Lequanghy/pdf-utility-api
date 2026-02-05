# api/index.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import io
import subprocess

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
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are allowed")

    try:
        content = await file.read()
        input_pdf = io.BytesIO(content)
        output_pdf = io.BytesIO()

        cmd = [
            "gs",
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            "-dPDFSETTINGS=/ebook",     # /screen = smallest, /ebook = good balance
            "-dNOPAUSE", "-dQUIET", "-dBATCH",
            "-sOutputFile=-",
            "-f", "-"
        ]

        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        stdout, stderr = process.communicate(input=input_pdf.getvalue())

        if process.returncode != 0:
            raise RuntimeError(f"Ghostscript failed: {stderr.decode()}")

        return StreamingResponse(
            io.BytesIO(stdout),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="compressed_{file.filename}"'
            }
        )

    except Exception as e:
        raise HTTPException(500, f"Compression failed: {str(e)}")

# Vercel serverless handler
handler = Mangum(app)