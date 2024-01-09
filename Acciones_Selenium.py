from tkinter import messagebox
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def buscar_identificacion():
    identificacion = input("Ingrese la identificación: ")
    driver = None

    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")

        driver = webdriver.Chrome(options=options)
        driver.get("https://www.rues.org.co/RM")

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "txtSearchNIT")))

        input_identificacion = driver.find_element(By.ID, "txtSearchNIT")
        input_identificacion.clear()
        input_identificacion.send_keys(identificacion)

        driver.find_element(By.ID, "btnConsultaNIT").click()

        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//table[@id='rmTable2']//tbody//td")))

        table_html = driver.find_element(By.ID, "rmTable2").get_attribute("outerHTML")
        soup = BeautifulSoup(table_html, 'html.parser')

        tbody = soup.find('tbody')
        if tbody:
            rows = tbody.find_all('tr')

            data = ""
            for row in rows:
                data_cells = row.find_all('td')
                if data_cells:
                    for column, cell in zip(["Razon Social ó Nombre", "Sigla", "NIT o Núm Id.", "Estado", "Cámara de Comercio", "Matrícula", "Organización Jurídica", "Categoría"], data_cells):
                        data += f"{column}: {cell.text.strip()}\n"
                    data += "\n---\n"

            messagebox.showinfo("Información de la empresa", data)

    except TimeoutException:
        messagebox.showerror("Error", "Tiempo de espera agotado. La página puede haber tardado demasiado en cargar.")
    except NoSuchElementException as e:
        messagebox.showerror("Error", f"No se pudo encontrar el elemento: {type(e).__name__} - {str(e)}")
    except WebDriverException as e:
        messagebox.showerror("Error", f"Excepción del WebDriver: {str(e)}")
    except Exception as e:
        messagebox.showerror("Error", f"Ha ocurrido un error en la búsqueda: {type(e).__name__} - {str(e)}")

    finally:
        if driver:
            driver.quit()

buscar_identificacion()