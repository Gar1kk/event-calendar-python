from tkinter import *
from datetime import datetime, date
import sqlite3
from calendar_utils import parse_event_date, event_status

db = sqlite3.connect("events.db")
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT, event_date TEXT, name TEXT)")
db.commit()

days = ["понедельник", "вторник", "среда", "четверг",
        "пятница", "суббота", "воскресенье"]

months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
          "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]

root = Tk()
root.title("Календарь событий")
root.geometry("430x350")


def add_event():
    win = Toplevel(root)
    win.title("Добавить событие")
    win.geometry("350x300")

    Label(win, text="Название события:").pack(pady=5)
    name_entry = Entry(win, width=35)
    name_entry.pack()

    Label(win, text="Дата события (дд.мм.гггг):").pack(pady=5)
    date_entry = Entry(win, width=35)
    date_entry.pack()

    info = Label(win, text="")
    info.pack(pady=10)

    def save():
        name = name_entry.get().strip()
        text_date = date_entry.get()

        if name == "":
            info["text"] = "Введите название события"
            return

        try:
            event_date = parse_event_date(text_date)
        except ValueError:
            info["text"] = "Неверная дата"
            return

        # Формат YYYY-MM-DD позволяет сортировать даты в SQLite как текст.
        cursor.execute(
            "INSERT INTO events (event_date, name) VALUES (?, ?)",
            (event_date.isoformat(), name)
        )
        db.commit()

        info["text"] = "Событие добавлено!"
        name_entry.delete(0, END)
        date_entry.delete(0, END)

    Button(win, text="Сохранить", command=save).pack(pady=5)
    Button(win, text="Назад", command=win.destroy).pack()


def open_events():
    win = Toplevel(root)
    win.title("Просмотр событий")
    win.geometry("750x450")

    today = date.today()

    top = Frame(win, bg="lightblue")
    top.pack(side=TOP, fill=X)
    Label(top, text="Сегодня: " + today.strftime("%d.%m.%Y") +
          ", " + days[today.weekday()], bg="lightblue",
          font=("Arial", 14)).pack(pady=10)

    bottom = Frame(win)
    bottom.pack(side=BOTTOM, fill=X, pady=10)

    left = Frame(win)
    left.pack(side=LEFT, padx=15, pady=10, fill=Y)

    right = Frame(win)
    right.pack(side=LEFT, padx=10, pady=10, fill=BOTH, expand=True)

    Label(left, text="Введите год:").pack()
    year_entry = Entry(left, width=15)
    year_entry.pack(pady=5)
    year_entry.insert(0, str(today.year))

    Label(left, text="Выберите месяц:").pack(pady=5)
    # Сохраняем выбор месяца при переходе к другим полям.
    month_list = Listbox(left, height=12, selectmode=SINGLE,
                        exportselection=0)
    month_list.pack()

    for month in months:
        month_list.insert(END, month)

    Label(right, text="События", font=("Arial", 14)).pack()
    result = Text(right, width=45, height=18)
    result.pack(fill=BOTH, expand=True)

    def show_events():
        result.delete(1.0, END)
        year = year_entry.get()
        selected = month_list.curselection()

        if not year.isdigit() or len(year) != 4 or year == "0000":
            result.insert(END, "Введите правильный год")
            return

        if len(selected) == 0:
            result.insert(END, "Выберите месяц")
            return

        month = selected[0] + 1
        # Шаблон YYYY-MM-% выбирает все даты нужного месяца.
        search_date = year + "-" + str(month).zfill(2) + "-%"

        cursor.execute(
            "SELECT event_date, name FROM events WHERE event_date LIKE ? ORDER BY event_date",
            (search_date,)
        )
        events = cursor.fetchall()

        if len(events) == 0:
            result.insert(END, "Событий нет")
            return

        for event_date, name in events:
            d = datetime.strptime(event_date, "%Y-%m-%d").date()
            status = event_status(d)

            result.insert(END, "Событие: " + name + "\n")
            result.insert(END, "Дата: " + d.strftime("%d.%m.%Y") + "\n")
            result.insert(END, "День недели: " + days[d.weekday()] + "\n")
            result.insert(END, status + "\n\n")

    Button(bottom, text="Просмотр", width=15,
           command=show_events).pack(side=LEFT, padx=20)
    Button(bottom, text="Назад", width=15,
           command=win.destroy).pack(side=RIGHT, padx=20)


def manage_events():
    win = Toplevel(root)
    win.title("Управление событиями")
    win.geometry("570x430")

    Label(win, text="Выберите событие из списка").pack(pady=8)
    event_list = Listbox(win, width=70, height=10, exportselection=False)
    event_list.pack(padx=12, pady=5)

    Label(win, text="Название:").pack()
    name_entry = Entry(win, width=45)
    name_entry.pack()
    Label(win, text="Дата (дд.мм.гггг):").pack()
    date_entry = Entry(win, width=45)
    date_entry.pack()

    info = Label(win, text="")
    info.pack(pady=7)
    event_ids = []

    def reload_events():
        event_list.delete(0, END)
        event_ids.clear()
        cursor.execute("SELECT id, event_date, name FROM events ORDER BY event_date, id")
        for event_id, event_date, name in cursor.fetchall():
            event_ids.append(event_id)
            formatted_date = datetime.strptime(event_date, "%Y-%m-%d").strftime("%d.%m.%Y")
            event_list.insert(END, formatted_date + " — " + name)

    def selected_event_id():
        choice = event_list.curselection()
        if not choice:
            info["text"] = "Сначала выберите событие"
            return None
        return event_ids[choice[0]]

    def choose_event(event=None):
        event_id = selected_event_id()
        if event_id is None:
            return
        cursor.execute("SELECT event_date, name FROM events WHERE id = ?", (event_id,))
        record = cursor.fetchone()
        if record is None:
            reload_events()
            return
        date_str, name = record
        name_entry.delete(0, END)
        name_entry.insert(0, name)
        date_entry.delete(0, END)
        date_entry.insert(0, datetime.strptime(date_str, "%Y-%m-%d").strftime("%d.%m.%Y"))
        info["text"] = ""

    def save_changes():
        event_id = selected_event_id()
        if event_id is None:
            return
        name = name_entry.get().strip()
        if not name:
            info["text"] = "Введите название события"
            return
        try:
            new_date = parse_event_date(date_entry.get())
        except ValueError:
            info["text"] = "Неверная дата"
            return
        cursor.execute(
            "UPDATE events SET name = ?, event_date = ? WHERE id = ?",
            (name, new_date.isoformat(), event_id)
        )
        db.commit()
        reload_events()
        info["text"] = "Изменения сохранены!"

    def delete_event():
        event_id = selected_event_id()
        if event_id is None:
            return
        from tkinter.messagebox import askyesno
        if not askyesno("Удаление события", "Удалить выбранное событие?", parent=win):
            return
        cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
        db.commit()
        reload_events()
        name_entry.delete(0, END)
        date_entry.delete(0, END)
        info["text"] = "Событие удалено"

    event_list.bind("<<ListboxSelect>>", choose_event)
    Button(win, text="Сохранить изменения", command=save_changes).pack(pady=4)
    Button(win, text="Удалить событие", command=delete_event).pack(pady=4)
    reload_events()


Label(root, text="Календарь событий",
      font=("Arial", 20)).pack(pady=15)

try:
    # Сохраняем ссылку на изображение, чтобы Tkinter не удалил его.
    logo = PhotoImage(file="logo.gif")
    Label(root, image=logo).pack(pady=10)
except TclError:
    Label(root, text="Календарь",
          font=("Arial", 24)).pack(pady=10)

Button(root, text="Добавить событие", width=25,
       command=add_event).pack(pady=10)
Button(root, text="Просмотр событий", width=25,
       command=open_events).pack(pady=10)
Button(root, text="Управление событиями", width=25,
       command=manage_events).pack(pady=10)

root.mainloop()
db.close()
