import json
from datetime import datetime

from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from tortoise.exceptions import DoesNotExist
from tortoise.queryset import QuerySet

from models import Rate, InsuranceRequest

app = FastAPI()

# Регистрация подключения к базе данных
register_tortoise(
    app,
    db_url="postgres://postgres:12345@localhost:5432/tech",
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)


@app.on_event("startup")
async def startup_event():
    # Загрузка данных из файла JSON в базу данных
    with open("rates.json") as file:
        rates_data = json.load(file)
        for valid_from, rates in rates_data.items():
            valid_from = datetime.strptime(valid_from, "%Y-%m-%d")
            for rate_data in rates:
                cargo_type = rate_data["cargo_type"]
                rate = rate_data["rate"]
                await Rate.create(cargo_type=cargo_type, rate=rate, valid_from=valid_from)


@app.get("/insurance")
async def calculate_insurance(cargo_type: str, declared_value: float):
    # Получение текущей даты и времени
    current_datetime = datetime.now()

    try:
        # Поиск актуальных тарифов из базы данных
        rates: QuerySet[Rate] = await Rate.filter(valid_from__lte=current_datetime).order_by("-valid_from").limit(1)

        # Поиск соответствующего тарифа для указанного типа груза
        rate: Rate = await rates.get(cargo_type=cargo_type)

        # Расчет стоимости страхования
        insurance_cost = declared_value * rate.rate

        # Сохранение информации о запросе
        await InsuranceRequest.create(cargo_type=cargo_type, declared_value=declared_value, timestamp=current_datetime)

        return {"insurance_cost": insurance_cost}
    except DoesNotExist:
        return {"message": "No rate found for the specified cargo type"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
