import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary")
        self.root.geometry("800x500")

        # Список всех записей
        self.records = []

        # Фрейм для ввода данных
        input_frame = ttk.LabelFrame(root, text="Новая запись")
        input_frame.pack(pady=10, padx=10, fill="x")

        # Дата
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.date_entry = ttk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.date_entry.insert(0, "2025-04-30")

        # Температура
        ttk.Label(input_frame, text="Температура (°C):").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.temp_entry = ttk.Entry(input_frame, width=10)
        self.temp_entry.grid(row=0, column=3, padx=5, pady=5)
        self.temp_entry.insert(0, "15.5")

        # Описание
        ttk.Label(input_frame, text="Описание:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.desc_entry = ttk.Entry(input_frame, width=40)
        self.desc_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

        # Осадки (флажок)
        self.precip_var = tk.BooleanVar()
        precip_cb = ttk.Checkbutton(input_frame, text="Осадки", variable=self.precip_var)
        precip_cb.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        # Кнопка "Добавить запись"
        add_btn = ttk.Button(input_frame, text="Добавить запись", command=self.add_record)
        add_btn.grid(row=2, column=2, padx=5, pady=5, sticky="e")

        # Фрейм для фильтров
        filter_frame = ttk.LabelFrame(root, text="Фильтры")
        filter_frame.pack(pady=5, padx=10, fill="x")

        ttk.Label(filter_frame, text="Фильтр по дате (ГГГГ-ММ-ДД):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.filter_date_entry = ttk.Entry(filter_frame, width=15)
        self.filter_date_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(filter_frame, text="Температура выше (°C):").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.filter_temp_entry = ttk.Entry(filter_frame, width=10)
        self.filter_temp_entry.grid(row=0, column=3, padx=5, pady=5)

        filter_btn = ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        filter_btn.grid(row=0, column=4, padx=5, pady=5)

        reset_filter_btn = ttk.Button(filter_frame, text="Сбросить фильтры", command=self.reset_filters)
        reset_filter_btn.grid(row=0, column=5, padx=5, pady=5)

        # Кнопки сохранения/загрузки
        control_frame = ttk.Frame(root)
        control_frame.pack(pady=5, padx=10, fill="x")

        save_btn = ttk.Button(control_frame, text="Сохранить в JSON", command=self.save_to_json)
        save_btn.pack(side="left", padx=5)

        load_btn = ttk.Button(control_frame, text="Загрузить из JSON", command=self.load_from_json)
        load_btn.pack(side="left", padx=5)

        # Таблица для отображения записей
        self.tree = ttk.Treeview(root, columns=("date", "temp", "desc", "precip"), show="headings")
        self.tree.heading("date", text="Дата")
        self.tree.heading("temp", text="Температура")
        self.tree.heading("desc", text="Описание")
        self.tree.heading("precip", text="Осадки")
        self.tree.column("date", width=120)
        self.tree.column("temp", width=100)
        self.tree.column("desc", width=300)
        self.tree.column("precip", width=80)

        scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=10, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)

        # Попытка загрузить данные при старте
        self.load_from_json(silent=True)

    def validate_date(self, date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def add_record(self):
        date = self.date_entry.get().strip()
        temp_str = self.temp_entry.get().strip()
        description = self.desc_entry.get().strip()
        precipitation = self.precip_var.get()

        # Проверки
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД")
            return
        try:
            temperature = float(temp_str)
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом")
            return
        if not description:
            messagebox.showerror("Ошибка", "Описание не может быть пустым")
            return

        # Добавление записи
        record = {
            "date": date,
            "temperature": temperature,
            "description": description,
            "precipitation": precipitation
        }
        self.records.append(record)
        # Сортируем по дате
        self.records.sort(key=lambda x: x["date"])
        # Сбрасываем фильтры и обновляем таблицу
        self.reset_filters()
        # Очищаем поля ввода (осадки сбрасываем)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.precip_var.set(False)

        messagebox.showinfo("Успех", "Запись добавлена")

    def update_treeview(self, records_to_show):
        # Очищаем таблицу
        for row in self.tree.get_children():
            self.tree.delete(row)
        # Заполняем заново
        for rec in records_to_show:
            precip_text = "Да" if rec["precipitation"] else "Нет"
            self.tree.insert("", tk.END, values=(
                rec["date"],
                f"{rec['temperature']:.1f}",
                rec["description"],
                precip_text
            ))

    def apply_filter(self):
        filter_date = self.filter_date_entry.get().strip()
        filter_temp_str = self.filter_temp_entry.get().strip()

        filtered = self.records[:]

        if filter_date:
            if not self.validate_date(filter_date):
                messagebox.showerror("Ошибка", "Неверный формат даты в фильтре")
                return
            filtered = [r for r in filtered if r["date"] == filter_date]

        if filter_temp_str:
            try:
                min_temp = float(filter_temp_str)
                filtered = [r for r in filtered if r["temperature"] > min_temp]
            except ValueError:
                messagebox.showerror("Ошибка", "Температура фильтра должна быть числом")
                return

        self.update_treeview(filtered)

    def reset_filters(self):
        self.filter_date_entry.delete(0, tk.END)
        self.filter_temp_entry.delete(0, tk.END)
        self.update_treeview(self.records)

    def save_to_json(self):
        filename = "weather.json"
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.records, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Сохранение", f"Данные сохранены в {filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def load_from_json(self, silent=False):
        filename = "weather.json"
        if not os.path.exists(filename):
            if not silent:
                messagebox.showwarning("Загрузка", "Файл weather.json не найден")
            return
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Простая проверка структуры
            if isinstance(data, list):
                self.records = data
                self.records.sort(key=lambda x: x.get("date", ""))
                self.reset_filters()
                if not silent:
                    messagebox.showinfo("Загрузка", f"Загружено {len(self.records)} записей")
            else:
                raise ValueError("Неверный формат JSON")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiary(root)
    root.mainloop

        
