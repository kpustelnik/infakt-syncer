from io import BytesIO
from pypdf import PdfReader, PdfWriter

def merge_pdfs(pdf_bytes_list: list[bytes]) -> bytes:
  writer = PdfWriter()

  for pdf_bytes in pdf_bytes_list:
    reader = PdfReader(BytesIO(pdf_bytes))
    for page in reader.pages:
      writer.add_page(page)

  output_stream = BytesIO()
  writer.write(output_stream)
  return output_stream.getvalue()