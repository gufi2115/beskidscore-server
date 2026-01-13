
# Beskidscore API

Beskidscore.pl jest to aplikacja to przeglądania wyników meczów piłkarskich z niższych lig.

## 🛠️ Technologia

* **Serwer:** Python 3.10, Django 4.2, Django REST Framework
* **Baza danych:** PostgreSQL
* **Autentykacja:** JWT (SimpleJWT)
* **Narzędzia:** Docker, Postman (do testowania API)
* **Klient:** TypeScript (stworzyny przy pomocy Github Copilot)
## Demo

beskidscore.pl

https://www.youtube.com/watch?v=-aOCnSFXfIA

https://www.youtube.com/watch?v=l8NtT7SAu4c

https://www.youtube.com/watch?v=hNycKkNd3mk

https://www.youtube.com/watch?v=LWJWx9K0rVI

## Zmienne w .env

`SECRET_KEY`

`DEBUG`

`DATABASE_NAME`

`DATABASE_USER`

`DATABASE_PASSWORD`

`DATABASE_HOST`

`DATABASE_PORT`

## Instalacja

```bash
  cd beskidscore-server/
  nano .env
  docker compose up --build
```
    
## 🚀 O mnie i o projekcje

Projekt ten powstał jak już wspominałem by ułatwic użytkownikom dostęp do wyników meczów, ponieważ wiekszość stron na rynku nie oferuje tego w jasny i przyjrzysty sposób. Ja sam uczę się Framework`a Django a więc ten projekt jest dla mnie nie tylko przyjemny kontekście tego, że lubie piłke nożną i gram w jednej z tych lig ale również daje mi się rozwijać. Pomimo tego, że samo rozumowanie DRF i uczenie się tego od podstaw jest ciężkie i żmudne, a przy okazji trzeba być cierpliwym jak maszyna zlaguje przy 16 gb ram no ale w dzisiejszych czasach to i tak sporo ;) to step-by-step pokonuje wyzwania. Jak np. system logowania, który zjadł trochę czasu. Sam projekt jest w trakcie rozwoju teraz pracuję nad mikroserwise CRUDowym do przetrzymywania zdjęć i dawania ich przy pomocy nginx. Chciałbym jeszcze wykonać swoją integracje z facebookiem, ponieważ tej nie wykonałem ja i naprawić celery tak aby umożliwiały co minute akualizację tabeli. W przyszłość chciałbym zrobić system do obstawiania tych meczów aby przyciągnąć uwagę ludzi.
