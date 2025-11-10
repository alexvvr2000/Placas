# Placas
Tracker de placas de automóvil con las siguientes características:

* Listar placas de automóvil por medio de una foto
* Dar opción de copiar texto de la placa, además de tener opción de mandarse por correo electrónico
* El formulario del correo electrónico debe contener:
  - Correo al que se mandará
  - Nombre del propietario del automóvil
  - Modelo del automóvil
* Al momento de mandarse el correo, aparte de la información que se mandó, tiene que dar la ubicación de dónde se tomó la foto en automático

## Ejemplo de archivo config.ini valido
```
[email]
smtp_server = smtp.gmail.com
smtp_port = 587
username = tu_email@gmail.com
password = tu_password_de_aplicacion
from_email = tu_email@gmail.com
enabled = true

[app]
debug = true
host = 0.0.0.0
port = 5000
max_file_size = 16

[ocr]
languages = es,en
confidence_threshold = 0.4
```