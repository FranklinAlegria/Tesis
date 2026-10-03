import os
import google.generativeai as genai
from dotenv import load_dotenv
import markdown
from xhtml2pdf import pisa
from extract import get_docx_text

def load_environment():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        raise ValueError("Please set a valid GEMINI_API_KEY in the .env file.")
    genai.configure(api_key=api_key)

def get_review_prompt(charter_text):
    return f"""
Act as a strict and professional Project Management Expert (PMP certified).
Your task is to review the following extracted text from a 'Project Charter' (also known as Project Establishment) document.

Evaluate the document based on the following standard project management criteria:
1. **Información General:** Project Name, Sponsor, and Project Manager clearly identified.
2. **Justificación / Business Case:** The reason for the project is clearly stated.
3. **Objetivos (SMART):** Objectives are Specific, Measurable, Achievable, Relevant, and Time-bound.
4. **Alcance (Scope):** In-scope and out-of-scope boundaries are clearly defined.
5. **Entregables Principales (Deliverables):** A clear list of tangible outcomes.
6. **Hitos y Cronograma (Milestones):** Key dates and high-level milestones established.
7. **Presupuesto y Recursos (Budget/Resources):** Initial estimate of costs or resources.
8. **Riesgos y Supuestos (Risks & Assumptions):** High-level risks and key assumptions identified.
9. **Interesados (Stakeholders):** List of key stakeholders affected by the project.

Please generate a professional Markdown report evaluating the Project Charter. 
Structure your report as follows:
- **Title:** Reporte de Revisión de Project Charter (Use # for title)
- **Resumen Ejecutivo:** A brief 2-3 sentence summary of the charter's overall quality and readiness.
- **Puntuación Global:** Provide a score out of 100 based on completeness and quality.
- **Evaluación por Criterio:** For each of the 9 criteria, state if it 'Cumple' (Pass), 'Necesita Mejora' (Needs Improvement), or 'No Cumple' (Fail). Provide a brief explanation of why, and if it fails or needs improvement, give a specific recommendation.
- **Conclusión y Próximos Pasos:** What the project manager should do next.

Here is the extracted text of the Project Charter:
--------------------------------------------------
{charter_text}
--------------------------------------------------
"""

def generate_pdf(markdown_text, output_path):
    # Convert Markdown to HTML
    html_content = markdown.markdown(markdown_text, extensions=['tables'])
    
    # Wrap in basic HTML structure with CSS for better PDF rendering
    full_html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Helvetica, Arial, sans-serif; font-size: 12px; line-height: 1.5; color: #333; }}
            h1 {{ color: #2C3E50; font-size: 24px; border-bottom: 2px solid #2C3E50; padding-bottom: 5px; }}
            h2 {{ color: #34495E; font-size: 18px; margin-top: 20px; }}
            h3 {{ color: #7F8C8D; font-size: 14px; }}
            p {{ margin-bottom: 10px; }}
            ul, ol {{ margin-bottom: 10px; padding-left: 20px; }}
            li {{ margin-bottom: 5px; }}
            strong {{ color: #2980B9; }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # Generate PDF
    with open(output_path, "wb") as pdf_file:
        pisa_status = pisa.CreatePDF(full_html, dest=pdf_file)
        
    if pisa_status.err:
        raise Exception("Error generating PDF document.")

def generate_review(charter_path="Trabajo Parcial Rev.0 (1).docx", output_path="Project_Charter_Review_Report.pdf"):
    print("Loading environment...")
    load_environment()
    
    print(f"Extracting text from {charter_path}...")
    try:
        charter_text = get_docx_text(charter_path)
    except Exception as e:
        print(f"Error reading document: {e}")
        print("Falling back to reading extracted_text.txt if it exists...")
        try:
            with open("extracted_text.txt", "r", encoding="utf-16le") as f:
                 charter_text = f.read()
        except:
             with open("extracted_text.txt", "r", encoding="utf-8") as f:
                 charter_text = f.read()
                 
    if not charter_text.strip():
        raise ValueError("The extracted text is empty.")

    print("Sending text to Gemini for evaluation...")
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = get_review_prompt(charter_text)
    
    response = model.generate_content(prompt)
    
    print(f"Generating PDF report to {output_path}...")
    generate_pdf(response.text, output_path)
    print("Review complete! Check the generated PDF report.")

if __name__ == "__main__":
    generate_review()
