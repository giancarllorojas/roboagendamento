# Bot de agendamento RioCard Universitário

### Dependências Gerais
Selenium
ChromeDriver
Xvfb e Xphyr(Caso usando VirtualDisplay)

### Dependências Python
```sh
$ pip install pyvirtualdisplay
$ pip install selenium
$ pip install requests
```

### Como rodar
```sh
$ python bot.py max_date visibility use_proxy use_virtual_display
```

Como eu fiz isso pra uso pessoal, para escolher a Modalidade de agendamento e o CPF a ser agendado é necessário ainda mexer no código nesta versão.

max_date: Data máxima pro agendamento no formato DD/MM/yyyy
visibility: Se visível ou não as ações do bot - false ou true
use_proxy: Se uso ou não proxy(Precisa de uma api de proxy) - false ou true
use_virtual_display: Se usa ou não um display virtual de video - false ou true
