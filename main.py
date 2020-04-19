from time import sleep

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from configuration import vk_login, vk_password, low_age, max_age, accept, deny, grades_limit
from constatnes import LOGIN_PAGE, DAYVINCHIK_IM

driver: WebDriver = None


def main():
    global driver
    driver = webdriver.Chrome()

    login_in = login_into_vk()
    if login_in:
        print('Успешный логин!\nИдем лайкать тяночек!')
        dayvinchik_main()
    else:
        driver.close()
        print('Залогиниться не удалось :(')


def login_into_vk():
    driver.get(LOGIN_PAGE)

    login_field = driver.find_element_by_id('email')
    password_field = driver.find_element_by_id('pass')

    login_field.send_keys(vk_login if vk_login else input())
    password_field.send_keys(vk_password if vk_password else input())
    driver.find_element_by_id('login_button').click()

    try:
        auth_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'login_authcheck_submit_btn')))
        auth_field = driver.find_element_by_id('authcheck_code')
        auth_field.clear()
        auth_field.send_keys(input('Введите код для аутентификации: '))
        driver.find_element_by_id('login_authcheck_submit_btn').click()

        if 'background-color' in auth_field.get_attribute('style'):
            print('Неверный код аутентификации!')
            return False
        try:
            captcha = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'recaptcha')))
            print('Пройдите капчу и нажмите Enter в поле ввода (ЗДЕСЬ!)')
            confirm = input('Нажмите Enter')
            return check_login()
        except TimeoutException:
            return check_login()
    except TimeoutException:
        login = check_login()
        if login:
            print('Успешный вход без 2FA!')
            return True
        else:
            return True


def check_login():
    driver.get(LOGIN_PAGE)
    if driver.current_url != LOGIN_PAGE:
        return True
    else:
        return False


def send_message(msg):
    message_field = driver.find_element_by_id('im_editable-91050183')
    message_field.click()
    message_field.send_keys(msg)
    message_field.send_keys(Keys.ENTER)


def dayvinchik_main():
    driver.get(DAYVINCHIK_IM)

    for i in range(grades_limit if grades_limit else 999999):
        name, age = get_last_message_info()
        print(f'{i}: {name.capitalize()}, {age}', end=' - ')
        if low_age <= age <= max_age:
            send_message(accept)
            print('accept')
        else:
            send_message(deny)
            print('deny')
        sleep(4)


def get_last_message_info():
    messages = driver.find_elements_by_class_name('_im_mess_stack')  # Элементы сообщений
    last_message = messages[-1]

    last_text = last_message.find_element_by_xpath(".//div[@class='im-mess-stack--content']"
                                                   "/ul[@class='ui_clean_list im-mess-stack--mess _im_stack_messages']"
                                                   "/li[1]"
                                                   "/div[@class='im-mess--text wall_module _im_log_body']").text

    info = last_text.split('\n')[2].split(',')
    return info[0], int(info[1].strip())


if __name__ == '__main__':
    main()
