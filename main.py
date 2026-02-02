# main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import subprocess
import io
import os

app = FastAPI(title="PDF Compression Service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   
        "http://127.0.0.1:5173",
        "https://pdf-utility-9tma.onrender.com/",
    ],
    allow_credentials=True,
    allow_methods=["*"],           # allow POST, GET, etc.
    allow_headers=["*"],           # allow all headers
)
@app.post("/compress")
async def compress_pdf(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are allowed")

    try:
        # Read uploaded file
        content = await file.read()

        # Use Ghostscript (best quality/size trade-off)
        input_pdf = io.BytesIO(content)
        output_pdf = io.BytesIO()

        cmd = [
            "gs",
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            "-dPDFSETTINGS=/ebook",      # /screen = smallest, /ebook = good balance, /printer = higher quality
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            "-sOutputFile=-",             # output to stdout
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

        compressed_content = stdout

        return StreamingResponse(
            io.BytesIO(compressed_content),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="compressed_{file.filename}"'
            }
        )

    except Exception as e:
        raise HTTPException(500, f"Compression failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)