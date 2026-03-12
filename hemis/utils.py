import requests
import logging
from django.conf import settings
from .models import HemisStatistic

logger = logging.getLogger(__name__)

def fetch_and_update_hemis_stats():
    """
    Fetches statistics from HEMIS API and updates the local HemisStatistic model.
    """
    students_url = "https://student.jbnuu.uz/rest/v1/public/stat-student"
    employees_url = "https://student.jbnuu.uz/rest/v1/public/stat-employee"
    
    headers = {}
    # if hasattr(settings, 'HEMIS_TOKEN') and settings.HEMIS_TOKEN:
    #      headers["Authorization"] = f"Bearer {settings.HEMIS_TOKEN}"

    students_count = 0
    teachers_count = 0

    # Fetch students
    try:
        response = requests.get(students_url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "data" in data and "education_type" in data["data"] and "Jami" in data["data"]["education_type"]:
                jami_data = data["data"]["education_type"]["Jami"]
                erkak = int(jami_data.get("Erkak", 0))
                ayol = int(jami_data.get("Ayol", 0))
                students_count = erkak + ayol
    except Exception as e:
        logger.error(f"Error fetching students stats from HEMIS: {e}")

    # Fetch employees/teachers
    try:
        response = requests.get(employees_url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "data" in data and "employment_form" in data["data"]:
                emp_form = data["data"]["employment_form"]
                asosiy = int(emp_form.get("Asosiy ish joy", 0))
                orindoshlik_ichki = int(emp_form.get("O‘rindoshlik (ichki-asosiy)", 0))
                orindoshlik_tashqi = int(emp_form.get("O‘rindoshlik (tashqi)", 0))
                teachers_count = asosiy + orindoshlik_ichki + orindoshlik_tashqi
    except Exception as e:
        logger.error(f"Error fetching employees stats from HEMIS: {e}")

    # Update database
    stats = HemisStatistic.load()
    if students_count > 0:
        stats.students_count = students_count
    if teachers_count > 0:
        stats.teachers_count = teachers_count
        
    stats.save()
    
    return stats
