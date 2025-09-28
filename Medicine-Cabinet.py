import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle
from datetime import datetime
from tkinter import filedialog
import os

class MedicineCabinet:
    # region constructor
    def __init__(self):
        self.load_database()
        self.setup_gui()
        self.start()
    
    def load_database(self):
        # Connect to SQLite database
        self.conn = sqlite3.connect("medicine_cabinet.db")
        self.cursor = self.conn.cursor()

        # Create tables if they don't exist
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS medicine (
            barcode TEXT PRIMARY KEY,
            name TEXT,
            description TEXT
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT,
            name TEXT,
            description TEXT,
            exp_date TEXT,
            FOREIGN KEY (barcode) REFERENCES medicine(barcode)
        )
        """)
        
        self.conn.commit()

    def setup_gui(self):
        # ------------------ GUI setup ------------------
        self.root = tk.Tk()
        self.root.title("Medicine Cabinet Manager")
        icon = tk.PhotoImage(file="favicon.png")
        self.root.iconphoto(False, icon)
        self.root.geometry("1100x800")
        self.root.minsize(width=1100,height=800)

        # ------------------ Style ------------------
        DARKBLUE = '#024275'
        BLUE = '#2881c9'
        LIGHTBLUE = '#5eabeb'
        
        style = ttk.Style()
        style.theme_use('default')
        style.configure('Custom.TFrame', background=LIGHTBLUE)
        style.configure('Custom.TLabelframe', background=LIGHTBLUE, foreground=DARKBLUE)
        style.configure('Custom.TLabelframe.Label', background=LIGHTBLUE, foreground=DARKBLUE)
        style.configure('TNotebook', background=LIGHTBLUE, borderwidth=0)
        style.configure('TNotebook.Tab', background=BLUE, foreground='white', padding=[10, 5])
        style.map('TNotebook.Tab',
                background=[('selected', DARKBLUE)],
                foreground=[('selected', 'white')])
        style.configure('TNotebook.Tab', borderwidth=1, relief='raised')
        style.configure('Custom.TButton',
                        background=BLUE,
                        foreground='white',
                        font=('Segoe UI', 10, 'bold'),
                        padding=6)
        style.map('Custom.TButton',
                background=[('active', DARKBLUE)],
                foreground=[('active', 'white')])

        # ------------------ Notebook ------------------
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True)

        # ------------------ Inventory ------------------
        inventory_tab = ttk.Frame(notebook)
        inventory_tab.configure(style='Custom.TFrame')
        notebook.add(inventory_tab, text="Inventory Database")

        inv_input_frame = ttk.LabelFrame(inventory_tab, text="Add Inventory Item")
        inv_input_frame.configure(style='Custom.TLabelframe')
        inv_input_frame.pack(fill='x', padx=10, pady=5)

        tk.Label(inv_input_frame, text="Barcode:").grid(row=0, column=0)
        tk.Label(inv_input_frame, text="Expiration Date (YYYY-MM-DD):").grid(row=1, column=0)

        self.inv_barcode_entry = tk.Entry(inv_input_frame, width=50)
        self.inv_exp_entry = tk.Entry(inv_input_frame, width=50)

        self.inv_barcode_entry.grid(row=0, column=1, sticky='NEWS',padx=10,pady=2)
        self.inv_exp_entry.grid(row=1, column=1, sticky='NEWS',padx=10,pady=2)
        inv_buttons_frame = tk.Frame(inv_input_frame, background=LIGHTBLUE)
        inv_buttons_frame.grid(row=0,column=2,rowspan=2,pady=10)
        
        ttk.Button(inv_buttons_frame, text="Add Inventory", command=self.inventory_action_add, style='Custom.TButton').grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(inv_buttons_frame, text="Delete Selected", command=self.inventory_action_delete, style='Custom.TButton').grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(inv_buttons_frame, text="Generate Inventory PDF", command=self.inventory_action_generate_pdf, style='Custom.TButton').grid(row=0, column=2, padx=5, pady=5)

        # Inventory table
        self.inv_tree = ttk.Treeview(inventory_tab, columns=("ID", "Barcode", "Name", "Description", "Exp Date"), show='headings')

        # Configure headings
        for col in ("ID", "Barcode", "Name", "Description", "Exp Date"):
            self.inv_tree.heading(col, text=col)

        # Create vertical scrollbar
        inv_scrollbar = ttk.Scrollbar(inventory_tab, orient="vertical", command=self.inv_tree.yview)
        self.inv_tree.configure(yscrollcommand=inv_scrollbar.set)

        # Layout: pack both treeview and scrollbar
        self.inv_tree.pack(side='left', fill='both', expand=True, padx=10, pady=5)
        inv_scrollbar.pack(side='right', fill='y')

        # apply style to widgets
        for widget in inv_input_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(bg=LIGHTBLUE, fg=DARKBLUE)
            elif isinstance(widget, tk.Entry):
                widget.configure(bg='white', fg=DARKBLUE)
        
        # ------------------ Medicine ------------------
        medicine_tab = ttk.Frame(notebook)
        medicine_tab.configure(style='Custom.TFrame')
        notebook.add(medicine_tab, text="Medicine Database")

        # Medicine input frame
        med_input_frame = ttk.LabelFrame(medicine_tab, text="Add Medicine")
        med_input_frame.configure(style='Custom.TLabelframe')
        med_input_frame.pack(fill='x', padx=10, pady=5)

        tk.Label(med_input_frame, text="Barcode:").grid(row=0, column=0)
        tk.Label(med_input_frame, text="Name:").grid(row=1, column=0)
        tk.Label(med_input_frame, text="Description:").grid(row=2, column=0)

        self.med_barcode_entry = tk.Entry(med_input_frame, width=50)
        self.med_name_entry = tk.Entry(med_input_frame, width=50)
        self.med_desc_entry = tk.Entry(med_input_frame, width=50)

        self.med_barcode_entry.grid(row=0, column=1)
        self.med_name_entry.grid(row=1, column=1)
        self.med_desc_entry.grid(row=2, column=1)
        med_buttons_frame = tk.Frame(med_input_frame, background=LIGHTBLUE)
        med_buttons_frame.grid(row=0,column=2,rowspan=3,pady=10)

        ttk.Button(med_buttons_frame, text="Add Medicine", command=self.database_action_add, style='Custom.TButton').grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(med_buttons_frame, text="Delete Selected", command=self.database_action_delete, style='Custom.TButton').grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(med_buttons_frame, text="Import from CSV", command=self.database_action_import, style='Custom.TButton').grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(med_buttons_frame, text="Export to CSV", command=self.database_action_export, style='Custom.TButton').grid(row=0, column=3, padx=5, pady=5)

        # Medicine table
        self.med_tree = ttk.Treeview(medicine_tab, columns=("Barcode", "Name", "Description"), show='headings')

        # Configure headings
        for col in ("Barcode", "Name", "Description"):
            self.med_tree.heading(col, text=col)

        # Create a vertical scrollbar
        med_scrollbar = ttk.Scrollbar(medicine_tab, orient="vertical", command=self.med_tree.yview)
        self.med_tree.configure(yscrollcommand=med_scrollbar.set)

        # Layout: pack both tree and scrollbar
        self.med_tree.pack(side='left', fill='both', expand=True, padx=10, pady=5)
        med_scrollbar.pack(side='right', fill='y')

        # apply style to widgets
        for widget in med_input_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(bg=LIGHTBLUE, fg=DARKBLUE)
            elif isinstance(widget, tk.Entry):
                widget.configure(bg='white', fg=DARKBLUE)

        # ------------------ Load Data ------------------
        self.inventory_action_load()
        self.database_action_load()
    
    def start(self):
        self.root.mainloop()
    
    # endregion
    # region inventory
    def inventory_action_add(self):
        barcode = self.inv_barcode_entry.get()
        exp_date = self.inv_exp_entry.get()
        try:
            exp = datetime.strptime(exp_date, "%Y-%m-%d")
            if exp < datetime.now():
                messagebox.showwarning("Warning", "Expiration date is in the past.")

            self.cursor.execute("SELECT name, description FROM medicine WHERE barcode = ?", (barcode,))
            result = self.cursor.fetchone()

            if result:
                name, desc = result
                self.cursor.execute("""
                    INSERT INTO inventory (barcode, name, description, exp_date)
                    VALUES (?, ?, ?, ?)
                """, (barcode, name, desc, exp_date))
                self.conn.commit()

                # Get the ID of the newly inserted row
                new_id = self.cursor.lastrowid

                messagebox.showinfo("Info", f"Write the number {new_id} on the box")
                self.inventory_action_load()
            else:
                messagebox.showerror("Error", "Medicine not found in database.")
        except ValueError:
            messagebox.showerror("Error", "Invalid expiration date format.")


    def inventory_action_delete(self):
        selected = self.inv_tree.selection()
        if selected:
            inv_id = self.inv_tree.item(selected[0])['values'][0]
            self.cursor.execute("DELETE FROM inventory WHERE id = ?", (inv_id,))
            self.conn.commit()
            self.inventory_action_load()

    def inventory_action_load(self):
        # Clear existing rows
        for row in self.inv_tree.get_children():
            self.inv_tree.delete(row)

        # Fetch and sort inventory by name
        for row in self.cursor.execute("SELECT * FROM inventory ORDER BY name ASC"):
            values = list(row)
            exp_date = values[-1]
            try:
                if datetime.strptime(exp_date, "%Y-%m-%d") < datetime.now():
                    self.inv_tree.insert("", "end", values=values, tags=('expired',))
                else:
                    self.inv_tree.insert("", "end", values=values)
            except:
                continue

        # Highlight expired items
        self.inv_tree.tag_configure('expired', background='red')

    def inventory_action_generate_pdf(self):
        filename = "Inventory Report.pdf"
        # Fetch inventory data sorted by name
        self.cursor.execute("SELECT id, barcode, name, description, exp_date FROM inventory ORDER BY name ASC")
        data = self.cursor.fetchall()

        # Create PDF document
        doc = SimpleDocTemplate(filename, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        # Title
        elements.append(Paragraph("Inventory Report", styles['Title']))
        elements.append(Spacer(1, 6))

        # Add current date
        current_date = datetime.now().strftime("Created on: %Y-%m-%d")
        elements.append(Paragraph(current_date, styles['Normal']))
        elements.append(Spacer(1, 12))

        # Table style
        small_style = ParagraphStyle(name='Small', fontSize=6, leading=8)
        header_style = ParagraphStyle(name='HeaderSmallWhite', fontSize=6, leading=8, textColor=colors.white, alignment=1)
        table_data = [[Paragraph(col, header_style) for col in ["ID", "Barcode", "Name", "Description", "Expiration Date"]]]

        # Table rows
        for row in data:
            exp_date = row[-1]
            try:
                if datetime.strptime(exp_date, "%Y-%m-%d") < datetime.now():
                    styled_row = [Paragraph(f'<font color="red">{cell}</font>', small_style) for cell in row]
                    table_data.append(styled_row)
                else:
                    table_data.append([Paragraph(str(cell), small_style) for cell in row])
            except:
                table_data.append([Paragraph(str(cell), small_style) for cell in row])

        # Estimate column widths based on max content length
        col_widths = []
        # Estimate column widths based on raw string length before Paragraph conversion
        raw_data = [["ID", "Barcode", "Name", "Description", "Expiration Date"]] + data
        col_widths = []
        for col_index in range(len(raw_data[0])):
            max_len = max(len(str(row[col_index])) for row in raw_data)
            col_widths.append(max(50, min(200, max_len * 5)))  # Adjust scaling as needed

        # Create table with dynamic column widths
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#024275')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),  # Header font size
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor('#5eabeb')])
        ]))

        elements.append(table)
        doc.build(elements)

        # Done
        os.startfile(filename)
    
    # endregion
    # region database
    def database_action_add(self):
        barcode = self.med_barcode_entry.get()
        name = self.med_name_entry.get()
        desc = self.med_desc_entry.get()
        if barcode and name:
            try:
                self.cursor.execute("INSERT INTO medicine VALUES (?, ?, ?)", (barcode, name, desc))
                self.conn.commit()
                self.database_action_load()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Barcode already exists.")
        else:
            messagebox.showerror("Error", "Barcode and Name are required.")

    def database_action_delete(self):
        selected = self.med_tree.selection()
        if selected:
            barcode = self.med_tree.item(selected[0])['values'][0]
            self.cursor.execute("DELETE FROM medicine WHERE barcode = ?", (barcode,))
            self.conn.commit()
            self.database_action_load()

    def database_action_load(self):
        # Clear existing rows
        for row in self.med_tree.get_children():
            self.med_tree.delete(row)

        # Fetch and sort medicine data by name
        for row in self.cursor.execute("SELECT * FROM medicine ORDER BY name ASC"):
            self.med_tree.insert("", "end", values=row)

    def database_action_import(self):
        # Open file dialog to select CSV file
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv")]
        )

        if not file_path:
            messagebox.showerror("Error","No file selected")
            return

        # Read and insert CSV data
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        for line in lines[1:]:  # Skip header
            parts = line.strip().split(',')
            if len(parts) != 3:
                messagebox.showerror("Error",f"Skipping malformed line: {line}")
                continue
            barcode, name, description = parts
            try:
                self.cursor.execute("""
                    INSERT INTO medicine (barcode, name, description)
                    VALUES (?, ?, ?)
                """, (barcode, name, description))
            except sqlite3.IntegrityError:
                messagebox.showerror("Error",f"Duplicate barcode found: {barcode} — skipping.")
            except Exception as e:
                messagebox.showerror("Error",f"Error inserting line: {line} — {e}")

        self.conn.commit()
        messagebox.showinfo("Info","CSV data loaded successfully!")
        self.database_action_load()

    def database_action_export(self):
        # Create hidden Tkinter root window
        root = tk.Tk()
        root.withdraw()

        # Ask user where to save the CSV file
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save Medicine Data As"
        )

        if not file_path:
            messagebox.showwarning("Warning","Export cancelled!")
            return

        # Fetch all rows
        self.cursor.execute("SELECT barcode, name, description FROM medicine")
        rows = self.cursor.fetchall()

        # Write to CSV manually
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write("Barcode,Name,Description\n")
            for row in rows:
                line = ','.join(f'"{str(cell)}"' if ',' in str(cell) else str(cell) for cell in row)
                file.write(line + '\n')

        messagebox.showinfo("Info", f"Data exported successfully to {file_path}")
        # endregion

MedicineCabinet()