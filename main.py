import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt


class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("800x500")

        # SQLite veritabanı bağlantısı
        self.conn = sqlite3.connect("finances.db")
        self.cursor = self.conn.cursor()

        # transaction veritabanı oluştur
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT,
                amount REAL,
                category TEXT,
                date TEXT,
                type TEXT
            )
        ''')
        self.conn.commit()

        # kullanıcı arayüz bileşenleri
        self.label_description = tk.Label(root, text="Açıklama:", bg="#3498DB", fg="white")
        self.entry_description = tk.Entry(root, bg="lightgray")

        self.label_amount = tk.Label(root, text="Miktar:", bg="#3498DB", fg="white")
        self.entry_amount = tk.Entry(root, bg="lightgray")

        self.label_category = tk.Label(root, text="Kategori:", bg="#3498DB", fg="white")
        self.entry_category = tk.Entry(root, bg="lightgray")

        self.label_date = tk.Label(root, text="Tarih:", bg="#3498DB", fg="white")
        self.entry_date = DateEntry(root, width=12, background='#3498DB', foreground='white', borderwidth=2)

        self.label_type = tk.Label(root, text="İşlem Türü:", bg="#3498DB", fg="white")
        self.type_var = tk.StringVar()
        self.type_var.set("Expense")
        self.type_expense = tk.Radiobutton(root, text="gider", variable=self.type_var, value="Gider", bg="#8B7355", fg="white")
        self.type_income = tk.Radiobutton(root, text="Gelir", variable=self.type_var, value="Gelir", bg="#8B7355", fg="white")

        self.btn_add = tk.Button(root, text="İşlemi Ekle", command=self.add_transaction, bg="#2ECC71", fg="white")
        self.btn_update = tk.Button(root, text="Veriyi Güncelle", command=self.update_transaction, bg="#F39C12", fg="white")
        self.btn_delete = tk.Button(root, text="İşlemi Sil", command=self.delete_transaction, bg="#E74C3C", fg="white")
        self.btn_view = tk.Button(root, text="İşlemleri Görüntüle", command=self.view_transactions, bg="#3498DB", fg="white")

        # Treeview gösterimi
        self.tree = ttk.Treeview(root, columns=("ID", "Description", "Amount", "Category", "Date", "Type"), show="headings", style="My.Treeview")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Description", text="Açıklama")
        self.tree.heading("Amount", text="Miktar")
        self.tree.heading("Category", text="Kategori")
        self.tree.heading("Date", text="Tarih")
        self.tree.heading("Type", text="Tür")

        # Toplam gelir ve gider Label
        self.label_total_incomes = tk.Label(root, text="Toplam Gelir: 0.00TL", bg="#2ECC71", fg="white")
        self.label_total_expenses = tk.Label(root, text="Toplam Gider: 0.00TL", bg="#E74C3C", fg="white")
        self.label_total_fark = tk.Label(root, text="Fark: 0.00TL", bg="#3498DB", fg="white")

        # Grid Layout
        self.label_description.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.entry_description.grid(row=0, column=1, padx=10, pady=10)

        self.label_amount.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.entry_amount.grid(row=1, column=1, padx=10, pady=10)

        self.label_category.grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.entry_category.grid(row=2, column=1, padx=10, pady=10)

        self.label_date.grid(row=3, column=0, padx=10, pady=10, sticky="e")
        self.entry_date.grid(row=3, column=1, padx=10, pady=10)

        self.label_type.grid(row=4, column=0, padx=10, pady=10, sticky="e")
        self.type_expense.grid(row=4, column=1, padx=10, pady=10)
        self.type_income.grid(row=4, column=2, padx=10, pady=10)

        self.btn_add.grid(row=5, column=0, pady=10)
        self.btn_update.grid(row=5, column=1, pady=10)
        self.btn_delete.grid(row=5, column=2, pady=10)
        self.btn_view.grid(row=5, column=3, pady=10)

        self.tree.grid(row=6, column=0, columnspan=4, pady=10)

        self.label_total_incomes.grid(row=7, column=0, columnspan=2, pady=10)
        self.label_total_expenses.grid(row=7, column=1, columnspan=2, pady=10)
        self.label_total_fark.grid(row=7, column=2, columnspan=2, pady=10)

        # toplam gelir ve giderler
        self.update_total_transactions()

    #ekleme fonksiyonu
    def add_transaction(self):
        description = self.entry_description.get()
        amount = self.entry_amount.get()
        category = self.entry_category.get()
        date = self.entry_date.get_date()
        transaction_type = self.type_var.get()

        if description and amount and category and date:
            try:
                amount = float(amount)
                formatted_date = date.strftime("%Y-%m-%d")
                self.cursor.execute("INSERT INTO transactions (description, amount, category, date, type) VALUES (?, ?, ?, ?, ?)",
                                    (description, amount, category, formatted_date, transaction_type))
                self.conn.commit()
                messagebox.showinfo("Başarılı", "Ekleme işlemi başarılı şekilde gerçekleşti.")
                self.clear_entry_fields()
                self.view_transactions()
            except ValueError:
                messagebox.showerror("Hata", "Miktar geçerli bir değer olmalı!")
        else:
            messagebox.showwarning("Uyarı", "İstenilen tüm bilgileri giriniz.")
        self.update_total_transactions()
        self.display_pie_chart()
 
    #gösterme fonksiyonu
    def view_transactions(self):
        self.tree.delete(*self.tree.get_children())  # Clear existing data
        self.cursor.execute("SELECT * FROM transactions ORDER BY date DESC")
        rows = self.cursor.fetchall()
        for row in rows:
            self.tree.insert("", "end", values=row)
        self.update_total_transactions()
        self.display_pie_chart()

    #güncelleme fonksiyonu
    def update_transaction(self):
        selected_item = self.get_selected_tree_item()
        if selected_item:
            transaction_id = selected_item[0]
            new_description = self.entry_description.get()
            new_amount = self.entry_amount.get()
            new_category = self.entry_category.get()
            new_date = self.entry_date.get_date()
            new_type = self.type_var.get()

            if new_description and new_amount and new_category and new_date:
                try:
                    new_amount = float(new_amount)
                    formatted_date = new_date.strftime("%Y-%m-%d")
                    self.cursor.execute("UPDATE transactions SET description=?, amount=?, category=?, date=?, type=? WHERE id=?",
                                        (new_description, new_amount, new_category, formatted_date, new_type, transaction_id))
                    self.conn.commit()
                    messagebox.showinfo("Başarılı", "Güncelleme işlemi başarıyla gerçekleşti.")
                    self.clear_entry_fields()
                    self.view_transactions()
                except ValueError:
                    messagebox.showerror("Hata", "Miktar geçerli bir değer olmalı!")
            else:
                messagebox.showwarning("Uyarı", "İstenilen tüm bilgileri giriniz.")
        else:
            messagebox.showwarning("Uyarı", "Güncellemek istediğiniz işlemi seçiniz.")
        self.update_total_transactions()
        self.display_pie_chart()

    #silme fonksiyonu
    def delete_transaction(self):
        selected_item = self.get_selected_tree_item()
        if selected_item:
            transaction_id = selected_item[0]
            result = messagebox.askyesno("Kontrol", "Bu işlemi silmek istediğinize emin misiniz?")
            if result:
                self.cursor.execute("DELETE FROM transactions WHERE id=?", (transaction_id,))
                self.conn.commit()
                messagebox.showinfo("Başarılı", "İşlem başarıyla silindi.")
                self.view_transactions()
        else:
            messagebox.showwarning("Uyarı", "Silinecek işlemi seçiniz.")
        self.update_total_transactions()
        self.display_pie_chart()

    #gelir gider toplam ve fark işlemleri
    def update_total_transactions(self):
        self.cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='Gider'")
        self.total_expenses = self.cursor.fetchone()[0]
        self.total_expenses = self.total_expenses if self.total_expenses else 0.00
        self.label_total_expenses.config(text=f"Toplam Gider: {self.total_expenses:.2f}TL")

        self.cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='Gelir'")
        self.total_incomes = self.cursor.fetchone()[0]
        self.total_incomes = self.total_incomes if self.total_incomes else 0.00
        self.label_total_incomes.config(text=f"Toplam Gelir: {self.total_incomes:.2f}TL")

        self.fark = self.total_incomes - self.total_expenses
        self.label_total_fark.config(text=f"Fark: {self.fark:.2f}TL")

    def get_selected_tree_item(self):
        selected_item = self.tree.focus()
        if selected_item:
            return self.tree.item(selected_item, 'values')
        return None

    #temizleme fonksiyonu
    def clear_entry_fields(self):
        self.entry_description.delete(0, tk.END)
        self.entry_amount.delete(0, tk.END)
        self.entry_category.delete(0, tk.END)
        self.entry_date.set_date(datetime.now())  #tarihi bugüne ayarla
    
    #pasta grafiği
    def display_pie_chart(self):
        labels = ['Gelir', 'Gider', 'Fark']
        sizes = [self.total_incomes, self.total_expenses, abs(self.fark)]
        colors = ['#2ECC71', '#E74C3C', '#3498DB']
        fig, ax = plt.subplots(figsize=(1.8,1.8))  # boyut ayarla
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        plt.axis('equal')  #pasta grafiğinin yuvarlak olduğuna emin oluyor
        plt.title('Gelir-Gider-Fark Dağılımı')
        plt.show()
        
# main Tkinter ekranı oluştur
root = tk.Tk()
app = ExpenseTracker(root)
root.mainloop()