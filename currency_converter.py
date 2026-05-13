import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os

API_KEY = "YOUR_API_KEY"  # Замените на свой ключ с exchangerate-api.com
API_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}/pair/"
HISTORY_FILE = "history.json"

class CurrencyConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        self.root.geometry("600x450")

        self.history = []
        self.load_history()

        self.create_widgets()
        self.update_history_table()

    def create_widgets(self):
        # Валюта "Из"
        tk.Label(self.root, text="Из:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        self.from_currency = ttk.Combobox(self.root, values=["USD", "EUR", "RUB", "GBP", "CNY"], width=5)
        self.from_currency.current(0)
        self.from_currency.grid(row=0, column=1, padx=10, pady=5)

        # Валюта "В"
        tk.Label(self.root, text="В:").grid(row=0, column=2, padx=10, pady=5, sticky='e')
        self.to_currency = ttk.Combobox(self.root, values=["USD", "EUR", "RUB", "GBP", "CNY"], width=5)
        self.to_currency.current(1)
        self.to_currency.grid(row=0, column=3, padx=10, pady=5)

        # Сумма
        tk.Label(self.root, text="Сумма:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        self.amount_entry = tk.Entry(self.root)
        self.amount_entry.grid(row=1, column=1, columnspan=3, padx=10, pady=5, sticky='we')

        # Кнопка конвертации
        tk.Button(self.root, text="Конвертировать", command=self.convert).grid(row=2, column=0, columnspan=4, pady=10)

        # Результат
        self.result_label = tk.Label(self.root, text="", font=('Arial', 12))
        self.result_label.grid(row=3, column=0, columnspan=4, pady=5)

        # Таблица истории
        self.tree = ttk.Treeview(self.root, columns=("from", "to", "amount", "result", "rate"), show="headings")
        self.tree.heading("from", text="Из")
        self.tree.heading("to", text="В")
        self.tree.heading("amount", text="Сумма")
        self.tree.heading("result", text="Результат")
        self.tree.heading("rate", text="Курс")
        self.tree.grid(row=4, column=0, columnspan=4, padx=10, pady=5, sticky='nsew')

    def convert(self):
        amount = self.amount_entry.get()
        from_cur = self.from_currency.get()
        to_cur = self.to_currency.get()

        if not amount:
            messagebox.showerror("Ошибка", "Введите сумму!")
            return

        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Сумма должна быть положительной")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
            return

        pair = f"{from_cur}/{to_cur}"
        url = API_URL + pair

        try:
            response = requests.get(url)
            data = response.json()
            if data.get("result") != "success":
                raise Exception(data.get("error-type", "Неизвестная ошибка API"))
            
            rate = data["conversion_rate"]
            result = round(amount * rate, 2)
            
            self.result_label.config(text=f"{amount} {from_cur} = {result} {to_cur} (Курс: {rate})")
            
            # Сохраняем в историю
            self.history.append({
                "from": from_cur,
                "to": to_cur,
                "amount": amount,
                "result": result,
                "rate": rate,
                "date": data["time_last_update_utc"]
            })
            self.save_history()
            self.update_history_table()

        except Exception as e:
            messagebox.showerror("Ошибка API", f"Не удалось получить курс: {e}")

    def update_history_table(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        for entry in self.history:
            self.tree.insert("", "end", values=(entry["from"], entry["to"], entry["amount"], entry["result"], entry["rate"]))

    def save_history(self):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False)

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                self.history = json.load(f)

if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverter(root)
    root.mainloop()
