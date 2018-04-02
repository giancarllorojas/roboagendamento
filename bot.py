from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from proxy import WebProxy
from time import sleep
from random import choice
from datetime import datetime
import sys
import sendgrid

SEL_WAIT_TIME         = 10
CHECK_INTERVAL        = 20
CHANGE_PROXY_INTERVAL = 18000

class RoboAgendamento:
    def __init__(self, visibility, max_date):
        self.user_agents    = open("uas.txt").readlines()
        self.visibility     = visibility
        self.max_date       = datetime.strptime(max_date, '%d/%m/%Y')
        self.min_found_date = ""
        self.agendado       = False

    def _mount_chrome(self, visibility):
        proxy = WebProxy()

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--disable-bundled-ppapi-flash")
        chrome_options.add_argument("--enable-extensions")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-plugins-discovery")
        chrome_options.add_argument('--ignore-gpu-blacklist')
        chrome_options.add_argument("--allow-insecure-localhost")
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("user-agent=" + choice(self.user_agents))
        
        chrome_options.add_extension(proxy.get_plugin())
        
        print(self._now() + ": " + "Starting display with visibility=" + str(self.visibility))
        self.display = Display(visible=self.visibility, size=(800,600))
        self.display.start()

        self.driver = webdriver.Chrome(chrome_options=chrome_options)

        return self.driver

    def _select_tipo(self, driver):
        print(self._now() + ": " + "Selecionando tipo")
        select = self._get_select('seltipoaluno')
        select.select_by_value('2')

        WebDriverWait(driver, SEL_WAIT_TIME).until(EC.alert_is_present())
        driver.switch_to_alert().accept()

    def _put_cpf(self, driver, cpf_value):
        print(self._now() + ": " + "Inserindo CPF")
        input_cpf = driver.find_element_by_id('cpf')
        WebDriverWait(driver, SEL_WAIT_TIME).until(EC.visibility_of(input_cpf))
        input_cpf.send_keys(cpf_value)

        WebDriverWait(driver, SEL_WAIT_TIME).until(EC.presence_of_element_located((By.ID, "btn_consulta")))
        driver.find_element_by_id('btn_consulta').click()
        WebDriverWait(driver, SEL_WAIT_TIME).until(EC.presence_of_element_located((By.ID, "btn_agenda")))
        agenda = driver.find_element_by_id('btn_agenda')
        WebDriverWait(driver, SEL_WAIT_TIME).until(EC.visibility_of(agenda))

        #force click
        while True:
            try:
                agenda.click()
                sleep(0.2)
            except:
                break
    
    def _get_select(self, ident):
        WebDriverWait(self.driver, SEL_WAIT_TIME).until(EC.presence_of_element_located((By.ID, ident)))
        return Select(self.driver.find_element_by_id(ident))

    def _get_hours(self):
        hours           = []
        select_hours    = self._get_select('horaSelecionada')
        for hour in select_hours.options:
            v = hour.get_attribute('value')
            if v != '0':
                hours.append(v)
        return hours

    def _get_day(self):
        WebDriverWait(self.driver, SEL_WAIT_TIME).until(EC.presence_of_element_located((By.ID, "divDataAgenda")))
        day_input = self.driver.find_element_by_id('divDataAgenda')

        while "Aguarde" in day_input.text:
            day_input = self.driver.find_element_by_id('divDataAgenda')
        
        return day_input.text

    def _email(self, title, text):
        sg = sendgrid.SendGridAPIClient(apikey='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')
        data = {
        "personalizations": [
            {
            "to": [
                {
                "email": "defensedelesprit@gmail.com"
                },
                {
                "email": "troy.rubens@gmail.com"
                }
            ],
            "subject": "RoboAgendamento LOG - " + str(title)
            }
        ],
        "from": {
            "email": "alerta@roboagendamento.com"
        },
        "content": [
            {
            "type": "text/plain",
            "value": str(text)
            }
        ]
        }
        #print(data)
        print(self._now() + ": " + "Enviando e-mail")

        trys = 0
        
        response = sg.client.mail.send.post(request_body=data)
                

    def _agendar(self, day, hour):
        select_hours    = self._get_select('horaSelecionada')
        select_hours.select_by_value(hour)

        WebDriverWait(self.driver, SEL_WAIT_TIME).until(EC.presence_of_element_located((By.XPATH, "//img[contains(@src, 'btn_agendar')]")))
        self.driver.find_element(By.XPATH, "//img[contains(@src, 'btn_agendar')]").click()

        WebDriverWait(self.driver, SEL_WAIT_TIME).until(EC.presence_of_element_located((By.XPATH, '//button//span[text()="SIM"]')))
        self.driver.find_element(By.XPATH, '//button//span[text()="SIM"]').click()


        sleep(1)
        WebDriverWait(self.driver, SEL_WAIT_TIME).until(EC.presence_of_element_located((By.XPATH, '(//tbody)[2]')))
        res = self.driver.find_element(By.XPATH, '(//tbody)[2]')

        text = res.text.strip()

        print(text)
        self._email("AGENDADO!", text)
        self.agendado = True
        print(self._now() + ": " + "AGENDADO COM SUCESSO!")
        sys.exit()

    def _analyse(self, posto, day, hours):
        print(self._now() + ": " + "Análise = Posto:" + str(posto) + " - Dia:" + str(day) + " as " + str(hours[0]))
        day_datetime    = datetime.strptime(day, '%d/%m/%Y')
        if day_datetime <= self.max_date:
            self._agendar(day, hours.pop())

        select_hours    = self._get_select('horaSelecionada')
        
        if not self.min_found_date:
            self.min_found_date = datetime.strptime(day, '%d/%m/%Y')
        else:
            if(day_datetime < self.min_found_date):
                self.min_found_date = day_datetime

    def __exit__(self, exc_type, exc_value, traceback):
        self.driver.close()
        self.display.popen.kill()

    def __enter__(self):
        return self

    def _now(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def run(self, cpf_value):
        driver = self._mount_chrome(self.visibility)
        
        driver.get("https://www.riocard.com/rccgrt/passelivre/agenda/agendamento.asp")

        #iframe_switch = driver.find_element(By.CLASS_NAME, "iframe")
        #driver.switch_to.frame(iframe_switch)

        self._select_tipo(driver)
        self._put_cpf(driver, cpf_value)
        
        print(self._now() + ": " + "Entrando no modo análise de horários")
        select = self._get_select('cboTipoAgenda')
        select.select_by_value('4')

        select = self._get_select('idPostoAtendimento')
        
        for i in range(0, int(CHANGE_PROXY_INTERVAL/CHECK_INTERVAL)):
            print(self._now() + ": " + "Checando horarios.")
            for opt in select.options:
                WebDriverWait(driver, SEL_WAIT_TIME).until(EC.visibility_of(opt))
                v = opt.get_attribute('value')
                if v != "0":
                    select.select_by_value(v)
                    day   = self._get_day()
                    hours = self._get_hours()
                    
                    self._analyse(opt.text, day, hours)
            sleep(CHECK_INTERVAL)

        self._email("Ultimos 30 minutos", "Melhor dia encontrado: " + str(self.min_found_date))
        self._close()

if(len(sys.argv) < 2):
    print("Usage: bot.py visibility")
    sys.exit()
try:
    visibility = True if sys.argv[1] == 'true' else False
except:
    print("Visibility must be a bool value")
    sys.exit()

with RoboAgendamento(visibility, "01/05/2018") as robo:
    while not robo.agendado:
        try:
            robo.run("046.294.481-60")
        except Exception as e:
            print("Excecao: " + str(e))
            with open("logs.txt", "a") as log:
                log.write(str(e) + "\n")
            continue