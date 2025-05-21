import time
from datetime import timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import csv

# Засекаем начало
start_time = time.time()

# Настройка undetected_chromedriver
options = uc.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
# options.add_argument("--headless")  # Включи при необходимости

driver = uc.Chrome(options=options)

url = "https://onlinelibrary.wiley.com/"
driver.get(url)
time.sleep(5)

search_query = "science"

# Поиск по сайту
try:
    search_input = WebDriverWait(driver, 10).until(
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
    driver.quit()
    exit()

# CSV setup
with open("wiley_results.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["№", "Название", "Авторы", "Журнал", "Выпуск", "Дата публикации", "Ссылка"])

    result_index = 1

    while True:
        print(f"\nОбработка новой страницы...")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.item__body"))
        )
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        items = soup.select("div.item__body")

        for item in items:
            try:
                title_tag = item.select_one("span.hlFld-Title a.publication_title")
                title = title_tag.get_text(strip=True) if title_tag else "N/A"
                link = title_tag["href"] if title_tag else "#"

                authors = [a.get_text(strip=True) for a in item.select(".meta__authors a.publication_contrib_author")]
                journal = item.select_one("a.publication_meta_serial")
                journal_text = journal.get_text(strip=True) if journal else "N/A"

                issue = item.select_one("a.publication_meta_volume_issue")
                issue_text = issue.get_text(strip=True) if issue else "N/A"

                pub_date = item.select_one("p.meta__epubDate")
                pub_date_text = pub_date.get_text(strip=True) if pub_date else "N/A"

                full_link = "https://onlinelibrary.wiley.com" + link if link.startswith("/") else link

                print(f"\n{result_index}. {title}")
                print(f"Авторы: {', '.join(authors)}")
                print(f"Журнал: {journal_text}, {issue_text}")
                print(f"{pub_date_text}")
                print(f"Ссылка: {full_link}")

                writer.writerow([result_index, title, ", ".join(authors), journal_text, issue_text, pub_date_text, full_link])
                result_index += 1

            except Exception as e:
                print(f"Ошибка при разборе статьи: {str(e)[:100]}...")

        # Переход на следующую страницу
        try:
            next_btn = driver.find_element(By.CSS_SELECTOR, "a.pagination__btn--next:not(.disabled)")
            driver.execute_script("arguments[0].click();", next_btn)
            time.sleep(3)
        except:
            print("Следующей страницы нет или кнопка неактивна.")
            break

driver.quit()

# Засекаем конец
end_time = time.time()
elapsed_time = timedelta(seconds=end_time - start_time)
print(f"\n⏱️ Скрипт завершён. Общее время выполнения: {elapsed_time}")
