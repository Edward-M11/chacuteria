import pypdf

# Try to open and read the PDF
file_path = "c:\\Users\\USER\\Documents\\GitHub\\Chacuteria_FOOD\\Prueba técnica Analista de Planeación énfasis Comercial.pdf"
try:
    reader = pypdf.PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    print(text)
except Exception as e:
    print("pypdf failed:", e)
    try:
        import fitz
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
        print(text)
    except Exception as e2:
        print("fitz failed:", e2)
