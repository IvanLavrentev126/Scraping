from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver
import time
import csv

driver = undetected_chromedriver.Chrome()
url = "https://onlinelibrary.wiley.com/"
driver.get(url)

time.sleep(5)

search_query = "science"

if url in driver.current_url:
    try:
        search_input = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='AllField']"))
        )
        print("Поле поиска найдено.")
        
        search_input.clear()
        search_input.send_keys(search_query)
        time.sleep(0.5)
        search_input.send_keys(Keys.RETURN)
        print("Поиск запущен!")

    except Exception as e:
        print("Ошибка при поиске поля ввода:", e)

# Ожидаем первую страницу результатов
WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "div.item__body"))
)

# CSV setup
with open("wiley_results.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["№", "Название", "Авторы", "Журнал", "Выпуск", "Дата публикации", "Ссылка"])

    result_index = 1

    while True:
        print(f"\nОбработка новой страницы...")

        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.item__body"))
        )
        books = driver.find_elements(By.CSS_SELECTOR, "div.item__body")

        for book in books:
            try:
                title = book.find_element(By.CSS_SELECTOR, "span.hlFld-Title a.publication_title").text
                link = book.find_element(By.CSS_SELECTOR, "span.hlFld-Title a.publication_title").get_attribute("href")
                authors = [a.text for a in book.find_elements(By.CSS_SELECTOR, ".meta__authors a.publication_contrib_author")]
                journal = book.find_element(By.CSS_SELECTOR, "a.publication_meta_serial").text if book.find_elements(By.CSS_SELECTOR, "a.publication_meta_serial") else "N/A"
                volume_issue = book.find_element(By.CSS_SELECTOR, "a.publication_meta_volume_issue").text if book.find_elements(By.CSS_SELECTOR, "a.publication_meta_volume_issue") else "N/A"
                pub_date = book.find_element(By.CSS_SELECTOR, "p.meta__epubDate").text if book.find_elements(By.CSS_SELECTOR, "p.meta__epubDate") else "N/A"

                print(f"\n{result_index}. {title}")
                print(f"Авторы: {', '.join(authors)}")
                print(f"Журнал: {journal}, {volume_issue}")
                print(f"{pub_date}")
                print(f"Ссылка: {link}")
                
                writer.writerow([result_index, title, ", ".join(authors), journal, volume_issue, pub_date, link])
                result_index += 1

            except Exception as e:
                print(f"Ошибка при парсинге: {str(e)[:100]}...")

        # Пытаемся перейти на следующую страницу
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "a.pagination__btn--next")
            next_href = next_button.get_attribute("href")
            if next_href:
                print("Переход на следующую страницу...")
                driver.get(next_href)
                time.sleep(3)
            else:
                print("Кнопка 'Следующая' неактивна.")
                break
        except:
            print("Все страницы обработаны.")
            break

time.sleep(2)
driver.quit()
