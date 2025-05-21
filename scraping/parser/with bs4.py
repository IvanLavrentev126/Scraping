import time
from datetime import timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import csv

def set_date_filter(driver):
    print("\nВыберите временной фильтр:")
    print("1 - All Dates")
    print("2 - Last (месяц / 6 месяцев / год)")
    print("3 - Custom Range")

    choice = input("Введите номер варианта (1/2/3): ").strip()

    try:
        if choice == "1":
            all_dates_radio = driver.find_element(By.ID, "anyDate")
            driver.execute_script("arguments[0].click();", all_dates_radio)
            print("Установлен фильтр: All Dates")

        elif choice == "2":
            last_radio = driver.find_element(By.ID, "staticRange")
            driver.execute_script("arguments[0].click();", last_radio)
            time.sleep(1)

            print("\nВыберите диапазон:")
            print("1 - Последний месяц")
            print("2 - Последние 6 месяцев")
            print("3 - Последний год")
            range_choice = input("Введите номер варианта (1/2/3): ").strip()

            select = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "staticRangeSelect"))
            )

            if range_choice == "1":
                select.send_keys("month")
            elif range_choice == "2":
                select.send_keys("6 months")
            elif range_choice == "3":
                select.send_keys("year")
            else:
                print("Неверный выбор диапазона.")
            print("Установлен фильтр: Last")

        elif choice == "3":
            custom_range_radio = driver.find_element(By.XPATH, "//input[@name='Ppub' and @id='range']")
            driver.execute_script("arguments[0].click();", custom_range_radio)
            time.sleep(1)

            from_month = input("Введите начальный месяц (1–12): ").strip()
            from_year = input("Введите начальный год (например, 2022): ").strip()
            to_month = input("Введите конечный месяц (1–12): ").strip()
            to_year = input("Введите конечный год (например, 2024): ").strip()

            driver.find_element(By.ID, "fromMonth").send_keys(from_month)
            driver.find_element(By.ID, "fromYear").send_keys(from_year)
            driver.find_element(By.ID, "toMonth").send_keys(to_month)
            driver.find_element(By.ID, "toYear").send_keys(to_year)

            print(f"Установлен фильтр: с {from_month}.{from_year} по {to_month}.{to_year}")

        else:
            print("Неверный ввод. Фильтр не установлен.")

    except Exception as e:
        print("Ошибка при установке фильтра даты:", e)

# Засекаем время начала
start_time = time.time()

# Настройка браузера
options = uc.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = uc.Chrome(options=options)
driver.get("https://onlinelibrary.wiley.com/")
time.sleep(5)

search_query = "science"
search_field = "Keyword"  # Возможные значения: AllField, Title, Contrib, Keyword, Abstract, Affiliation, FundingAgency

# Переход на страницу Advanced Search
try:
    adv_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/search/advanced')]"))
    )
    adv_link.click()
    print("Перешли в раздел расширенного поиска")
except Exception as e:
    print("Не удалось перейти в Advanced Search:", e)
    driver.quit()
    exit()

# Ожидание формы и выполнение поиска
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "text1"))
    )

    # Выбор поля поиска
    select_element = driver.find_element(By.ID, "searchArea1")
    for option in select_element.find_elements(By.TAG_NAME, "option"):
        if option.get_attribute("value") == search_field:
            option.click()
            break

    # Ввод поискового запроса
    search_input = driver.find_element(By.ID, "text1")
    search_input.clear()
    search_input.send_keys(search_query)

    # Установка фильтра даты
    set_date_filter(driver)

    search_input.send_keys(Keys.RETURN)
    print(f"Выполняется поиск по '{search_query}' в поле '{search_field}'")

except Exception as e:
    print("Ошибка при настройке формы расширенного поиска:", e)
    driver.quit()
    exit()

# Подготовка CSV
with open("wiley_results.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["№", "Название", "Авторы", "Журнал", "Выпуск", "Дата публикации", "Ссылка"])

    result_index = 1

    while True:
        try:
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
                    full_link = "https://onlinelibrary.wiley.com" + link if link.startswith("/") else link

                    authors = [a.get_text(strip=True) for a in item.select(".meta__authors a.publication_contrib_author")]
                    journal = item.select_one("a.publication_meta_serial")
                    journal_text = journal.get_text(strip=True) if journal else "N/A"

                    issue = item.select_one("a.publication_meta_volume_issue")
                    issue_text = issue.get_text(strip=True) if issue else "N/A"

                    pub_date = item.select_one("p.meta__epubDate")
                    pub_date_text = pub_date.get_text(strip=True) if pub_date else "N/A"

                    print(f"{result_index}. {title}")
                    print(f"Авторы: {', '.join(authors)}")
                    print(f"Журнал: {journal_text}, {issue_text}")
                    print(f"Дата: {pub_date_text}")
                    print(f"Ссылка: {full_link}\n")

                    writer.writerow([
                        result_index,
                        title,
                        ", ".join(authors),
                        journal_text,
                        issue_text,
                        pub_date_text,
                        full_link
                    ])
                    result_index += 1

                except Exception as e:
                    print("Ошибка при обработке публикации:", e)

            # Переход на следующую страницу
            try:
                next_btn = driver.find_element(By.CSS_SELECTOR, "a.pagination__btn--next:not(.disabled)")
                driver.execute_script("arguments[0].click();", next_btn)
                time.sleep(3)
            except:
                print("Все страницы обработаны.")
                break

        except Exception as e:
            print("Ошибка при загрузке страницы с результатами:", e)
            break

driver.quit()

# Вывод времени выполнения
end_time = time.time()
elapsed_time = timedelta(seconds=end_time - start_time)
print(f"Скрипт завершён. Время выполнения: {elapsed_time}")
