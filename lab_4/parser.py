import time
import csv
import logging
from playwright.sync_api import sync_playwright

logging.basicConfig(
    filename='scraping.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def wait_for(ms):
    time.sleep(ms / 1000)


def scrape_page(page, page_number, max_items=10):
    """Функция для обработки одной страницы товаров, с ограничением на количество товаров."""
    logging.info(f"Парсинг страницы {page_number}...")

    # Ожидаем, пока загрузятся карточки товаров
    page.wait_for_selector(".product-card__wrapper")
    elements = page.query_selector_all(".product-card__wrapper")
    logging.info(f"На странице {page_number} найдено {len(elements)} товаров.")

    products = []
    for i in range(min(max_items, len(elements))):
        element = elements[i]
        try:
            title = element.query_selector(".product-card__name").inner_text().strip()
            price_text = element.query_selector(".product-card__price").inner_text().strip()

            # Извлекаем цену, удаляя ненужные символы
            price = price_text.split()[0]
            cleaned_title = title.replace("/", "").strip()

            product_url = element.query_selector("a").get_attribute("href")
            products.append({"title": cleaned_title, "price": price, "url": product_url})

            logging.info(f"Товар {i + 1} на странице {page_number}: {cleaned_title} - {price} руб.")
        except Exception as e:
            logging.error(f"Ошибка при извлечении данных для товара на странице {page_number}: {e}")

    return products


def save_to_csv(products, page_number):
    """Сохранение данных в CSV файл"""
    filename = f"products_page_{page_number}.csv"
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Название", "Цена", "Ссылка"])
        for product in products:
            writer.writerow([product["title"], product["price"], product["url"]])
    logging.info(f"Данные с страницы {page_number} сохранены в файл {filename}.")


def scrape():
    try:
        with sync_playwright() as p:
            logging.info("Запуск браузера Chromium...")
            browser = p.chromium.launch(headless=False, args=['--no-sandbox', '--disable-setuid-sandbox'])
            page = browser.new_page()
            page.goto("https://www.wildberries.ru/")

            page.fill("#searchInput", "транспортир")
            page.keyboard.press("Enter")
            logging.info("Выполнен поиск по запросу 'транспортир'.")

            page.wait_for_selector(".catalog-page")
            logging.info("Каталог товаров загружен.")

            page.click(".dropdown-filter__btn--sorter")
            wait_for(5000)
            price_ascending = page.query_selector(".j-catalog-sort:nth-child(3)")
            if price_ascending:
                price_ascending.click()
                wait_for(5000)
            logging.info("Сортировка товаров по цене выполнена.")

            products = scrape_page(page, 1, max_items=10)
            save_to_csv(products, 1)

            total_pages = 5
            all_products = products

            for page_number in range(2, total_pages + 1):
                logging.info(f"Переход на страницу {page_number}...")

                next_button = page.query_selector(".pagination-next")
                if next_button:
                    next_button.click()
                    wait_for(5000)
                else:
                    logging.warning(f"Не удалось найти кнопку для перехода на следующую страницу {page_number}.")

                additional_products = scrape_page(page, page_number)
                all_products.extend(additional_products)

                save_to_csv(additional_products, page_number)

            browser.close()
            logging.info("Браузер закрыт.")

    except Exception as e:
        logging.error(f"Произошла ошибка при выполнении скрапинга: {e}")


if __name__ == "__main__":
    logging.info("Запуск скрипта скрапинга...")
    scrape()
    logging.info("Скрипт завершил работу.")
