payment_id = "111"
amount = 1000
percent = 10
statuses = ["Одобрено","Отклонено","В обработке","Требует подтверждение","Недостаточно средств"]

for status in statuses:
    print(status)

def calculate_fee(amount:int, percent:int) -> float:
    return amount * (percent / 100)

payments = [
    {"id": "TX-001", "amount":100000, "status":"Отклонено"},
    {"id": "TX-002", "amount":1000, "status":"Одобрено"},
    {"id": "TX-003", "amount":100, "status":"Одобрено"}
            ]
total_approved = 0

for payment in payments:
    if payment["status"] == "Одобрено":
        total_approved += payment["amount"]
print(f"Сумма одобренных платежей {total_approved}")


print(f"ID операции {payment_id} сумма: {amount} статус {statuses[0]}\n Комиссия {calculate_fee(amount, percent)}")

if amount > 10000:
    print("Требуется дополнительная проверка")
else:
    print("Стандартная проверка")
