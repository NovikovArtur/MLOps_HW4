# HW4

Для запуска нужны Docker Compose и `dbt/teta-ml-1-2025/train.csv` из [набора транзакций](https://www.kaggle.com/competitions/teta-ml-1-2025). CSV не входит в репозиторий.

```bash
docker compose up --build -d
docker compose ps -a
```

ClickHouse запускается на порту 8124. Затем сервис `dbt` загружает данные, устанавливает пакеты, строит модели, запускает тесты и генерирует документацию. После успешного завершения с кодом 0 документация доступна на [localhost:8084](http://localhost:8084).

```bash
docker compose logs --tail=100 dbt
docker compose exec -T clickhouse clickhouse-client --user hw4 --password hw4_local --query 'SELECT count() FROM transactions_db.transactions'
```

Для исходного `train.csv` ожидается 786431 строка. Повторная загрузка заменяет таблицу целиком без дублирования. При ошибке загрузки старая таблица сохраняется.

Модели находятся в `dbt/`: источник `transactions_db.transactions`, staging `stg_transactions` и шесть витрин в базе `analytics`.

| Витрина | Содержание |
| --- | --- |
| `mart_daily_state_metrics` | Дневные объёмы по штатам, средний чек, P95, доля крупных покупок |
| `mart_fraud_by_category` | Количество, суммы и доля фрода по категориям |
| `mart_fraud_by_state` | Фрод по штатам, уникальные клиенты и мерчанты |
| `mart_customer_risk_profile` | История клиента и уровень риска |
| `mart_hourly_fraud_pattern` | Фрод по дням недели и часам |
| `mart_merchant_analytics` | Оборот и подозрительность мерчантов |

Суммы хранятся с двумя знаками после запятой. SMALL меньше 100, MEDIUM от 100 до 1000, LARGE от 1000. Доли выражены в процентах. Риск HIGH начинается с 5% фрода, MEDIUM с 1%. Для подозрительного мерчанта дополнительно нужны минимум 100 транзакций. Пороги задаются в `dbt/dbt_project.yml`.

ID клиента получен из имени, фамилии, пола, штата и координат, поэтому возможны совпадения и разделение истории после переезда. Риск описывает имеющуюся разметку, а не прогноз. Время сохраняется без сдвига как UTC, поскольку в CSV нет часового пояса. Справочник содержит 50 штатов и DC.

Версии: `dbt-core 1.10.15`, `dbt-clickhouse 1.9.7`. Используются `dbt_utils`, `dbt_date`, `dbt_expectations` и собственные макросы. Тесты по заданию: `not_null`, `unique`, `accepted_values`, уникальность сочетаний ключей, два singular-теста на суммы и fraud_rate, два unit-теста на staging и дневную витрину. SQLFluff запускается через `make lint` и pre-commit.

```bash
make test
make lint
docker compose down
```

В `results/` сохраняются лог тестов `test.log` и версии `versions.log`. Для сдачи приложите лог тестов и скриншот DAG из dbt Docs, а версии укажите в описании PR. Граф открывается значком в правом нижнем углу страницы модели; для `stg_transactions` включите родителей и потомков.

