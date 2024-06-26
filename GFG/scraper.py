from bs4 import BeautifulSoup
import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

conn = sqlite3.connect("Courses.db")

cur = conn.cursor()
cur.execute('''
                CREATE TABLE IF NOT EXISTS COURSES (
                NAME text, 
                RATING text,
                INTERESTED text, 
                PRICE text
            )
            ''')
conn.commit()

def insert_data(data):
    try:
        cur.executemany("INSERT INTO COURSES VALUES (?, ?, ?, ?)", data)
        conn.commit()
        print("Data successfully inserted.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
def get_course_data(course_section):
    courses = []
    for item in course_section.find_all("a", class_="ui card courseListingPage_courseCardContainer__lLZiS"):
        course_name = item.find("h4", class_="ui left aligned header courseListingPage_myAuto__i6GdI sofia-pro course_heading").text
        course_rating = item.find("span", class_="urw-din")
        course_rating = "Information not available" if course_rating is None else course_rating.text
        course_interested = item.find("div", class_="courseListingPage_descriptionText__zN_K1 sofia-pro g-opacity-50 g-mb-0 grid_with__meta").text.split(" ")[0]
        course_price = item.find("p", class_="sofia-pro g-mb-0 courseListingPage_batchFee__0NlbJ")
        course_price = "0" if course_price is None else course_price.text

        courses.append((
            course_name,
            course_rating,
            course_interested,
            course_price
        ))

    return courses

def scrape_geeksforgeeks():
    url = "https://practice.geeksforgeeks.org/courses?utm_source=geeksforgeeks&utm_medium=main_header&utm_campaign=courses"

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    popular_courses = soup.find("div", class_="ui cards courseListingPage_cardLayout__multW courseListingPage_toggleCourseCards__pWBVA")
    other_courses = soup.find_all("div", class_="ui cards courseListingPage_cardLayout__multW courseListingPage_courseCardsGrid__VYBzZ")
    all_courses_data = get_course_data(popular_courses)
    for course in other_courses:
        course_data = get_course_data(course)
        all_courses_data.extend(course_data)
    driver.quit()
    return all_courses_data

if __name__ == '__main__':
    data = scrape_geeksforgeeks()
    print("Data to be inserted:", data)
    insert_data(data)