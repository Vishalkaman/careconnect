from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
def generate_receipt(name, date, paid_to, amount, donation_category, file_name):
    c = canvas.Canvas(file_name, pagesize=letter)
    
    # Set up the font and font size
    c.setFont("Helvetica-Bold", 24)
    
    # Draw border around the receipt
    c.rect(20, 20, 560, 760)
    
    # Write the header
    c.drawCentredString(300, 730, "Receipt")
    c.line(30, 725, 570, 725)
    
    # Write receipt number and date
    c.setFont("Helvetica", 12)
    c.drawRightString(570, 710, f"Date: {date}")
    
    # Write name and paid to
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(300, 670, f"Name: {name}")
    c.drawCentredString(300, 640, f"Paid To: {paid_to}")
    
    # Write donation category and amount
    c.drawCentredString(300, 610, f"Donation Category: {donation_category}")
    c.drawCentredString(300, 580, f"Amount: {amount} Rs")
    
    c.save()

# Example usage
name = "John Doe"
date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
paid_to = "Charity ABC"
donation_category = "Education Fund"
amount = 100  # Example amount
file_name = "receipt.pdf"

generate_receipt(name, date, paid_to, amount, donation_category, file_name)
