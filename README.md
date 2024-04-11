# FiscalCheck (client)
Сервис позволяет отслеживать сроки годности фискальных накопителей в контрольно-кассовых машинах производства "АТОЛ". Имеется функционал Telegram-бота, который оповестит о подходящих к концу сроках годности в Telegram-канал. Представляет из себя базовый API и панель управления с входом через Active Directory\
Данный код является клиентской частью и не работает без запущенного сервера\

## Установка и запуск
Перед началом использования разверните [сервер](https://github.com/AnLobanov/fiscalcheck) и пропишите в скрипте IP-адрес или доменное имя сервера\
Запустите скрипт fc-client.py перед запуском любого обычного кассового ПО\
Необходимо, чтобы рядом со скриптом в той же директории находилась [библиотека libfptr10.py](https://integration.atol.ru/api/?utm_source=google.com&utm_medium=organic&utm_campaign=google.com&utm_referrer=google.com#podklyuchenie-k-proektu) и были установлены драйвера для ККМ
