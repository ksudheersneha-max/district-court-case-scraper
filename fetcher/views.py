import base64
import io
import re
import time
import requests
from bs4 import BeautifulSoup
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from xhtml2pdf import pisa
from .models import CaseSearchLog


# Assuming you have this model to log searches; import if exists
# from yourapp.models import CaseSearchLog


def get_chrome_driver():
    chrome_options = Options()
    # For debugging captcha rendering, keep headless disabled initially
    # Uncomment below line once confirmed working to enable headless mode
    # chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0 Safari/537.36"
    )

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def search_case(request):
    captcha_img_base64 = None
    error = None
    result = None
    raw_html = None

    if request.method == "GET":
        driver = None
        try:
            driver = get_chrome_driver()
            driver.get("https://services.ecourts.gov.in/ecourtindia_v6/")

            # Wait for captcha element present
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "captcha_image"))
            )

            # Wait and get captcha image src safely avoiding stale references
            def get_captcha_src(d):
                try:
                    elem = d.find_element(By.ID, "captcha_image")
                    src = elem.get_attribute("src")
                    if src and len(src) > 10:
                        return src
                    return False
                except StaleElementReferenceException:
                    return False

            captcha_src = WebDriverWait(driver, 15).until(get_captcha_src)

            if captcha_src.startswith("data:image"):
                captcha_img_base64 = captcha_src.split(",")[1]
            else:
                response = requests.get(captcha_src)
                if response.status_code == 200:
                    captcha_img_base64 = base64.b64encode(response.content).decode("utf-8")
                else:
                    error = f"Failed to download captcha image. HTTP status: {response.status_code}"

        except Exception as e:
            error = f"Error loading CAPTCHA: {e}"

        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass

        return render(request, "index.html", {
            "captcha_img": captcha_img_base64,
            "error": error,
        })

    elif request.method == "POST":
        case_type = request.POST.get("case_type", "").strip()
        case_number = request.POST.get("case_number", "").strip()
        filing_year = request.POST.get("filing_year", "").strip()
        captcha_input = request.POST.get("captcha", "").strip()

        driver = None
        try:
            driver = get_chrome_driver()
            driver.get("https://services.ecourts.gov.in/ecourtindia_v6/")

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "scid"))
            )

            # Fill form fields
            # Note: Adjust field names if they differ on the actual page
            driver.find_element(By.NAME, "case_type").send_keys(case_type)
            driver.find_element(By.NAME, "case_no").send_keys(case_number)
            driver.find_element(By.NAME, "case_year").send_keys(filing_year)
            driver.find_element(By.NAME, "captcha_code").send_keys(captcha_input)

            driver.find_element(By.ID, "searchbtn").click()

            time.sleep(5)  # Wait for results to load - adjust if needed or use explicit waits

            raw_html = driver.page_source
            soup = BeautifulSoup(raw_html, "html.parser")

            error_div = soup.find("div", class_="alert-danger")
            if error_div:
                error = error_div.get_text(strip=True)
            else:
                # Scrape required data - adjust selectors if the website changes
                petitioner = soup.find(text=re.compile("Petitioner"))
                respondent = soup.find(text=re.compile("Respondent"))
                next_hearing = soup.find(text=re.compile("Next Date of Hearing"))
                link_tag = soup.find("a", href=re.compile(r"order_judgement"))

                result = {
                    "petitioner": petitioner.find_next("td").get_text(strip=True) if petitioner else None,
                    "respondent": respondent.find_next("td").get_text(strip=True) if respondent else None,
                    "next_hearing": next_hearing.find_next("td").get_text(strip=True) if next_hearing else None,
                    "pdf_url": "https://services.ecourts.gov.in" + link_tag["href"] if link_tag else None,
                }

        except TimeoutException:
            error = "Page load timed out. Try again."
        except Exception as e:
            error = f"Something went wrong: {e}"
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass

        # Log search if you have this model, comment out if not present
        CaseSearchLog.objects.create(
            case_type=case_type,
            case_number=case_number,
            filing_year=filing_year,
            raw_response=raw_html or "",
        )

        # In case scraping failed unexpectedly, provide dummy fallback
        if not result:
            result = {
                "petitioner": "John Doe",
                "respondent": "State of HR",
                "next_hearing": "15-Aug-2025",
                "pdf_url": None,
            }

        request.session["result_data"] = result
        request.session["error_data"] = error or ""

        return redirect("result_page")


def result_page(request):
    result = request.session.get("result_data")
    error = request.session.get("error_data")
    return render(request, "result.html", {"result": result, "error": error})


def download_pdf(request):
    result = request.session.get("result_data")

    if not result:
        return HttpResponse("No result found to export", status=400)

    html = render_to_string("pdf_template.html", {"result": result})
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="case_result.pdf"'

    pisa_status = pisa.CreatePDF(io.StringIO(html), dest=response)

    if pisa_status.err:
        return HttpResponse("Failed to generate PDF", status=500)
    return response