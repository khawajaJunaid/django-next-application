from django.utils import timezone
from rest_framework import generics, response
from rest_framework.permissions import IsAuthenticated
from .models import ExtractedData
from . import serializers
from django.http import JsonResponse
from django import forms
import tempfile 
from django.core.exceptions import ValidationError
from pypdf import PdfReader
from pypdf.errors import PdfReadError
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
from django.contrib.auth.decorators import login_required
import cv2
import re
import PyPDF2
import traceback
from PyPDF2.errors import PdfReadError

class UploadPDFForm(forms.Form):
    pdf_file = forms.FileField(required=True)



def is_pdf(file):
    # Check if the uploaded file is a PDF using the 'magic' library
    
    try:
        print("returning file after validatiom")
        response = PdfReader(file)
        return response
    except PdfReadError as error:
        print("invalid PDF file")
        raise error
    except Exception as error:
        print("error occured while validating pdf",error)
        raise error
    
def extract_employee_details(text):
    # Extract employee's name
    match_name = re.search(r"12\s*\n\n([\w\s]+)\s*\.\s*13", text)
    employee_name = match_name.group(1).strip() if match_name else None
    
    # Extract address
    pattern = r'(?<=employee plan sick pay\n)(.*?)(?=Vv)'
    matches = re.findall(pattern, text, re.DOTALL)
    
    # Joining matches to get the result as a single string
    result = ''.join(matches).strip()
    
    # Remove lines starting explicitly with "14"
    cleaned_result = re.sub(r'^14.*$', '', result, flags=re.MULTILINE).strip()
    
    # Split the cleaned_result into lines, filter out any empty lines, and then join with commas
    employee_address = ', '.join(filter(None, cleaned_result.split('\n')))
    
    # Extract the wages/income based on the "Federal income tax withheld" prompt
    match_income = re.search(r'Federal income tax withheld\s*\n[^ ]+ (\d{2,})', text)
    income = match_income.group(1) if match_income else None

    return {
        "Employee Name": employee_name,
        "Address": employee_address,
        "Wages": income
    }

def extract_text_from_pdf(pdf_file_path):
    try:
        # Convert PDF to images using pdf2image
        pdf_images = convert_from_path(pdf_file_path)
        # Save each extracted image to the directory
        extracted_text = ""
        for i, page_image in enumerate(pdf_images):
            image_path = f'/app/images/page_{i + 1}.jpg'
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            # Apply adaptive thresholding
            img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                cv2.THRESH_BINARY_INV, 11, 2)

            # Denoise
            img = cv2.fastNlMeansDenoising(img, None, 30, 7, 21)
            page_image.save(image_path, 'JPEG')
            print("Saving image for page", i)
            img = Image.open(image_path).convert('L')
            # Save the preprocessed image (optional)
            img.save('preprocessed_image.png')
            
            # Perform OCR with Tesseract
            # custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
            custom_config = r'--oem 3  --psm 4 -c textord_tablefind_recognize_tables=1 -c textord_force_make_prop_words=1'

            # Use pytesseract to extract text with custom Tesseract configuration
            page_text= pytesseract.image_to_string(img, config=custom_config)

            extracted_text += page_text

        return extracted_text
    except Exception as error:
        print("Error raised while extracting text from pdf",error)
        raise error

def rotate_pdf(input_pdf_path, output_pdf_path=None, degrees=90):
    if output_pdf_path is None:
        output_pdf_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name

    with open(input_pdf_path, 'rb') as input_pdf_file, open(output_pdf_path, 'wb') as output_pdf_file:
        pdf_reader = PyPDF2.PdfReader(input_pdf_file)
        pdf_writer = PyPDF2.PdfWriter()
        
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            page.rotate(degrees)
            pdf_writer.add_page(page)

        pdf_writer.write(output_pdf_file)

    return output_pdf_path

def extract_pdf_data(request):
    try:
        if request.method == 'POST':
            form = UploadPDFForm(request.POST, request.FILES)
            if form.is_valid():
                pdf_file = form.cleaned_data['pdf_file']

                # Save the uploaded PDF to a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                    for chunk in pdf_file.chunks():
                        temp_pdf.write(chunk)

                # Get the path to the saved PDF
                pdf_file_path = temp_pdf.name

                # Rotate the PDF to the right (clockwise)
                rotated_pdf_path = rotate_pdf(pdf_file_path, degrees=90)

                # Extract text from the rotated PDF
                extracted_text = extract_text_from_pdf(rotated_pdf_path)
                details = extract_employee_details(extracted_text)

                # Parse the extracted text to extract specific data like name, address, and income
                name = details['Employee Name']  # Replace with actual parsing logic
                address = details['Address']  # Replace with actual parsing logic
                income = details['Wages']  # Replace with actual parsing logic

                # Create a JSON response
                response_data = {
                    'name': name,
                    'address': address,
                    'income': income,
                }

                if not name:
                    raise Exception("Please upload a correct PDF, possible errors: orientation")
                    # return JsonResponse({'errors': "Please upload a correct PDF, possible errors: orientation"}, status=422)

                return response_data
            else:
                # Form is not valid, return an error response
                errors = form.errors.as_json()
                # return JsonResponse({'errors': errors}, status=400)
                raise PdfReadError(errors)
    except Exception as error:
        # return JsonResponse({'error': f'Invalid request with error {error}'}, status=400)
        raise error
class Profile(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.User

    def get_object(self):
        return self.request.user


class Ping(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, *args, **kwargs):
        return response.Response({'now': timezone.now().isoformat()})


class UploadFile(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.FileUploadSerializer

    def post(self, request, *args, **kwargs):
        try:
            extracted_data = extract_pdf_data(request)
            # Create a new instance of ExtractedData and save it to the database
            print("errore here",extracted_data)
            extracted_data = ExtractedData(user=request.user, name=extracted_data["name"], address=extracted_data["address"], income=extracted_data["income"])
            extracted_data.save()
            extracted_data_serializer = serializers.ExtractedDataSerializer(extracted_data)
            return response.Response(extracted_data_serializer.data)
        
        except PdfReadError as error:
            print(traceback.format_exc())
            return response.Response(f"Invalid file format. Please upload a PDF file with {error}",status=422)
        except Exception as error:
            print(traceback.format_exc())
            return response.Response(f"An error occured while uploading file :{error}",status=500)
        

# docker run -v images:/app/images -p 4001:4001 django-app