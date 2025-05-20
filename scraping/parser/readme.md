# Инструкция по использованию парсера Wiley
## 1. Что делает скрипт
Скрипт автоматически выполняет поиск по ключевому слову на сайте Wiley Online Library, обходит все страницы с результатами, извлекает информацию о публикациях и сохраняет данные в файл wiley_results.csv.
___
## 2. Требования
Перед запуском убедитесь, что установлены следующие библиотеки:

```py
    pip list
```
Должны быть эти билиотеки
```py
selenium
undetected-chromedriver
pandas
```
Если библиотек нет
```py
pip install -r requirements.txt
```
## 3. Этапы работы скрипта

1. Открывает сайт Wiley.
2. Вводит поисковый запрос (по умолчанию: "science") в строку поиска.
```py
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

WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "div.item__body"))
)
```

Для каждой найденной статьи собирает:
1. название,
2. авторов,
3. название журнала,
4. номер выпуска,
5. дату публикации,
6. ссылку.
```py
#Обработка результатов запроса
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
```
1. Если сайт долго загружается, можно увеличить время ожидания, указав большее значение в time.sleep.
2. Если структура сайта изменилась, потребуется обновить селекторы в коде.
3. Если браузер не запускается, проверьте, установлен ли Google Chrome и не блокируется ли системой.
## Все данные сохраняются в файл wiley_results.csv, который создаётся в той же директории, где находится скрипт