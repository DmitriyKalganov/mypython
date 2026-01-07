#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Merger - Desktop приложение для объединения PDF файлов
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import scrolledtext
from PyPDF2 import PdfMerger
import sys


class PDFMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Merger - Объединение PDF файлов")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Список выбранных PDF файлов
        self.pdf_files = []

        # Настройка интерфейса
        self.setup_ui()

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""

        # Заголовок
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)

        title_label = tk.Label(
            title_frame,
            text="📄 PDF Merger",
            font=("Arial", 20, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(pady=15)

        # Основной контейнер
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Описание
        description = tk.Label(
            main_frame,
            text="Добавьте PDF файлы и объедините их в один документ",
            font=("Arial", 11),
            fg="#555"
        )
        description.pack(pady=(0, 15))

        # Кнопки управления
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 15))

        self.add_button = tk.Button(
            button_frame,
            text="➕ Добавить PDF файлы",
            command=self.add_files,
            bg="#3498db",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.add_button.pack(side=tk.LEFT, padx=(0, 10))

        self.remove_button = tk.Button(
            button_frame,
            text="❌ Удалить выбранный",
            command=self.remove_selected,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.remove_button.pack(side=tk.LEFT, padx=(0, 10))

        self.clear_button = tk.Button(
            button_frame,
            text="🗑️ Очистить всё",
            command=self.clear_all,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.clear_button.pack(side=tk.LEFT)

        # Список файлов
        list_frame = tk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        list_label = tk.Label(
            list_frame,
            text="Выбранные PDF файлы:",
            font=("Arial", 11, "bold"),
            anchor=tk.W
        )
        list_label.pack(fill=tk.X, pady=(0, 5))

        # Scrollbar для списка
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_listbox = tk.Listbox(
            list_frame,
            font=("Arial", 10),
            selectmode=tk.SINGLE,
            yscrollcommand=scrollbar.set,
            height=10
        )
        self.file_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_listbox.yview)

        # Кнопки для изменения порядка
        order_frame = tk.Frame(main_frame)
        order_frame.pack(fill=tk.X, pady=(0, 15))

        self.up_button = tk.Button(
            order_frame,
            text="⬆️ Вверх",
            command=self.move_up,
            bg="#16a085",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.up_button.pack(side=tk.LEFT, padx=(0, 10))

        self.down_button = tk.Button(
            order_frame,
            text="⬇️ Вниз",
            command=self.move_down,
            bg="#16a085",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.down_button.pack(side=tk.LEFT)

        # Кнопка объединения
        self.merge_button = tk.Button(
            main_frame,
            text="🔗 Объединить PDF файлы",
            command=self.merge_pdfs,
            bg="#27ae60",
            fg="white",
            font=("Arial", 14, "bold"),
            padx=30,
            pady=15,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.merge_button.pack(fill=tk.X)

        # Статус бар
        status_frame = tk.Frame(self.root, bg="#ecf0f1", height=30)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)

        self.status_label = tk.Label(
            status_frame,
            text="Готов к работе",
            bg="#ecf0f1",
            fg="#555",
            font=("Arial", 9),
            anchor=tk.W,
            padx=10
        )
        self.status_label.pack(fill=tk.BOTH)

    def add_files(self):
        """Добавление PDF файлов"""
        files = filedialog.askopenfilenames(
            title="Выберите PDF файлы",
            filetypes=[("PDF файлы", "*.pdf"), ("Все файлы", "*.*")]
        )

        if files:
            for file in files:
                if file not in self.pdf_files:
                    self.pdf_files.append(file)
                    self.file_listbox.insert(tk.END, os.path.basename(file))

            self.update_status(f"Добавлено {len(files)} файл(ов)")

    def remove_selected(self):
        """Удаление выбранного файла"""
        selection = self.file_listbox.curselection()
        if selection:
            index = selection[0]
            self.file_listbox.delete(index)
            del self.pdf_files[index]
            self.update_status("Файл удален")
        else:
            messagebox.showwarning("Внимание", "Выберите файл для удаления")

    def clear_all(self):
        """Очистка всех файлов"""
        if self.pdf_files:
            if messagebox.askyesno("Подтверждение", "Удалить все файлы из списка?"):
                self.file_listbox.delete(0, tk.END)
                self.pdf_files.clear()
                self.update_status("Список очищен")
        else:
            messagebox.showinfo("Информация", "Список уже пуст")

    def move_up(self):
        """Переместить файл вверх"""
        selection = self.file_listbox.curselection()
        if selection:
            index = selection[0]
            if index > 0:
                # Обмен в списке файлов
                self.pdf_files[index], self.pdf_files[index-1] = \
                    self.pdf_files[index-1], self.pdf_files[index]

                # Обмен в listbox
                item = self.file_listbox.get(index)
                self.file_listbox.delete(index)
                self.file_listbox.insert(index-1, item)
                self.file_listbox.selection_set(index-1)

                self.update_status("Файл перемещен вверх")
        else:
            messagebox.showwarning("Внимание", "Выберите файл для перемещения")

    def move_down(self):
        """Переместить файл вниз"""
        selection = self.file_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.pdf_files) - 1:
                # Обмен в списке файлов
                self.pdf_files[index], self.pdf_files[index+1] = \
                    self.pdf_files[index+1], self.pdf_files[index]

                # Обмен в listbox
                item = self.file_listbox.get(index)
                self.file_listbox.delete(index)
                self.file_listbox.insert(index+1, item)
                self.file_listbox.selection_set(index+1)

                self.update_status("Файл перемещен вниз")
        else:
            messagebox.showwarning("Внимание", "Выберите файл для перемещения")

    def merge_pdfs(self):
        """Объединение PDF файлов"""
        if not self.pdf_files:
            messagebox.showwarning("Внимание", "Добавьте хотя бы один PDF файл")
            return

        if len(self.pdf_files) < 2:
            messagebox.showwarning("Внимание", "Добавьте как минимум 2 PDF файла для объединения")
            return

        # Выбор места сохранения
        output_file = filedialog.asksaveasfilename(
            title="Сохранить объединенный PDF",
            defaultextension=".pdf",
            filetypes=[("PDF файлы", "*.pdf")]
        )

        if not output_file:
            return

        try:
            self.update_status("Объединение файлов...")
            self.merge_button.config(state=tk.DISABLED)
            self.root.update()

            # Создание объединителя
            merger = PdfMerger()

            # Добавление всех файлов
            for pdf_file in self.pdf_files:
                try:
                    merger.append(pdf_file)
                except Exception as e:
                    messagebox.showerror(
                        "Ошибка",
                        f"Не удалось добавить файл:\n{os.path.basename(pdf_file)}\n\nОшибка: {str(e)}"
                    )
                    merger.close()
                    self.merge_button.config(state=tk.NORMAL)
                    self.update_status("Ошибка при объединении")
                    return

            # Сохранение результата
            merger.write(output_file)
            merger.close()

            self.merge_button.config(state=tk.NORMAL)
            self.update_status("PDF успешно объединен!")

            # Диалог успеха
            result = messagebox.askyesno(
                "Успех",
                f"PDF файлы успешно объединены!\n\nФайл сохранен:\n{output_file}\n\nОткрыть папку с файлом?"
            )

            if result:
                # Открыть папку с файлом
                folder = os.path.dirname(output_file)
                if sys.platform == 'win32':
                    os.startfile(folder)
                elif sys.platform == 'darwin':
                    os.system(f'open "{folder}"')
                else:
                    os.system(f'xdg-open "{folder}"')

        except Exception as e:
            self.merge_button.config(state=tk.NORMAL)
            messagebox.showerror("Ошибка", f"Не удалось объединить PDF файлы:\n\n{str(e)}")
            self.update_status("Ошибка при объединении")

    def update_status(self, message):
        """Обновление статуса"""
        self.status_label.config(text=message)


def main():
    """Главная функция"""
    root = tk.Tk()
    app = PDFMergerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
