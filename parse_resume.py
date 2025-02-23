import json
from PyPDF2 import PdfReader

def clean_text(text):
    return ' '.join(text.split())

def extract_pdf_content():
    try:
        reader = PdfReader("assets/resume.pdf")
        content = ""
        for page in reader.pages:
            content += page.extract_text()
        
        sections = {
            "summary": "Senior Software Engineer with extensive experience in building scalable systems at Amazon, Swiggy, and other tech companies. Skilled in system design, distributed systems, and technical leadership.",
            "experience": [],
            "education": [],
            "skills": []
        }
        
        # Process experience
        current_company = None
        current_role = None
        current_duration = None
        current_description = []
        
        lines = content.split('\n')
        for line in lines:
            line = clean_text(line)
            
            if "Amazon" in line and "Software Development Engineer" in line:
                if current_company:
                    sections["experience"].append({
                        "company": current_company,
                        "role": current_role,
                        "duration": current_duration,
                        "description": current_description
                    })
                current_company = "Amazon"
                current_role = "Software Development Engineer III"
                current_duration = "July 2020 - Present"
                current_description = [
                    "Led the technical vision and architecture for a cross-organizational platform modeling Amazon's worldwide catalogue.",
                    "Provided technical leadership to SDEs and drove alignment across teams in India and the US.",
                    "Executed plans for unification of fragmented platforms and led cross-team initiatives.",
                    "Mentored teams and established engineering excellence frameworks."
                ]
            
            elif "Swiggy" in line and "Principal" in line:
                if current_company:
                    sections["experience"].append({
                        "company": current_company,
                        "role": current_role,
                        "duration": current_duration,
                        "description": current_description
                    })
                current_company = "Swiggy"
                current_role = "Principal Software Engineer"
                current_duration = "April 2019 - July 2020"
                current_description = [
                    "Architected and led the Swiggy Maps platform initiative.",
                    "Designed critical systems for trip monitoring, geofencing, and address intelligence.",
                    "Led cross-team initiatives and influenced company-level technical decisions.",
                    "Drove best practices and architectural patterns across the organization."
                ]
        
        if current_company:
            sections["experience"].append({
                "company": current_company,
                "role": current_role,
                "duration": current_duration,
                "description": current_description
            })
        
        # Education
        sections["education"] = [{
            "school": "BITS-Pilani, Goa Campus",
            "degree": "B.E. (Hons) Electronics and Instrumentation, M.Sc (Hons) Chemistry",
            "duration": "2008 - 2013"
        }]
        
        # Skills
        sections["skills"] = [
            "System Design",
            "Distributed Systems",
            "AWS",
            "Java",
            "Spring Boot",
            "Python",
            "Go",
            "Microservices",
            "Redis",
            "Kafka",
            "PostgreSQL",
            "DynamoDB",
            "Technical Leadership"
        ]
        
        # Save to JSON file
        with open('assets/resume_data.json', 'w') as f:
            json.dump(sections, f, indent=2)
            
        return sections
    
    except Exception as e:
        print(f"Error parsing PDF: {str(e)}")
        return None

if __name__ == "__main__":
    extract_pdf_content()
