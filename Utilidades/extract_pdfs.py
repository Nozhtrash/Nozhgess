# -*- coding: utf-8 -*-
"""
Extractor OCR real para PDFs escaneados usando PyMuPDF + Tesseract
"""
import fitz  # PyMuPDF
import os
import pytesseract
from PIL import Image
import io

# Configurar Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

pdf_dir = r"c:\Users\knoth\OneDrive\Documentos\Extras\Apps\Proyectos\Nozhgess original\Z_Z_Z\Info"
output_dir = r"c:\Users\knoth\OneDrive\Documentos\Extras\Apps\Proyectos\Nozhgess original\Nozhgess v.4\pdf_extracts"

os.makedirs(output_dir, exist_ok=True)

# Process both PDFs that need OCR
pdf_files = [
    ("NORMA TECNICA DECRETO EXENTO N 57 SSP 2025.pdf", 20),  # First 20 pages for sample
]

for pdf_name, max_pages in pdf_files:
    pdf_path = os.path.join(pdf_dir, pdf_name)
    output_file = os.path.join(output_dir, pdf_name.replace(".pdf", "_OCR.txt"))
    
    print(f"\n{'='*80}")
    print(f"OCR: {pdf_name}")
    print(f"{'='*80}")
    
    try:
        doc = fitz.open(pdf_path)
        num_pages = min(len(doc), max_pages)
        print(f"Procesando {num_pages} páginas (de {len(doc)} total)...")
        
        all_text = []
        
        for page_num in range(num_pages):
            print(f"  Página {page_num + 1}/{num_pages}...", end=" ", flush=True)
            page = doc[page_num]
            
            # Render page to image at 200 DPI (faster than 300)
            mat = fitz.Matrix(200/72, 200/72)
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PIL Image
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            
            # Apply OCR with English (default, works for Spanish too)
            text = pytesseract.image_to_string(img, lang='eng')
            
            all_text.append(f"\n\n{'='*40}\nPÁGINA {page_num + 1}\n{'='*40}\n")
            all_text.append(text)
            print(f"OK ({len(text)} chars)")
        
        doc.close()
        
        # Save to file
        full_text = "".join(all_text)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(full_text)
        
        print(f"\nGuardado en: {output_file}")
        print(f"\n--- PREVIEW (primeros 6000 chars) ---")
        print(full_text[:6000])
            
    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()
