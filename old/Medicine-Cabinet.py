import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

# Connect to SQLite database
conn = sqlite3.connect("medicine_cabinet.db")
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS medicine (
    barcode TEXT PRIMARY KEY,
    name TEXT,
    description TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    barcode TEXT,
    name TEXT,
    description TEXT,
    exp_date TEXT,
    FOREIGN KEY (barcode) REFERENCES medicine(barcode)
)
""")
conn.commit()

# GUI setup
root = tk.Tk()
root.title("Medicine Cabinet Manager")

notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

# style setup
DARKBLUE = '#024275'
BLUE = '#2881c9'
LIGHTBLUE = '#5eabeb'

# ------------------ Inventory Tab ------------------
inventory_tab = ttk.Frame(notebook)
notebook.add(inventory_tab, text="Inventory Database")

inv_input_frame = ttk.LabelFrame(inventory_tab, text="Add Inventory Item")
inv_input_frame.pack(fill='x', padx=10, pady=5)

tk.Label(inv_input_frame, text="Barcode:").grid(row=0, column=0)
tk.Label(inv_input_frame, text="Expiration Date (YYYY-MM-DD):").grid(row=1, column=0)

inv_barcode_entry = tk.Entry(inv_input_frame)
inv_exp_entry = tk.Entry(inv_input_frame)

inv_barcode_entry.grid(row=0, column=1)
inv_exp_entry.grid(row=1, column=1)

def add_inventory():
    barcode = inv_barcode_entry.get()
    exp_date = inv_exp_entry.get()
    try:
        exp = datetime.strptime(exp_date, "%Y-%m-%d")
        if exp < datetime.now():
            messagebox.showwarning("Warning", "Expiration date is in the past.")
        cursor.execute("SELECT name, description FROM medicine WHERE barcode = ?", (barcode,))
        result = cursor.fetchone()
        if result:
            name, desc = result
            cursor.execute("INSERT INTO inventory (barcode, name, description, exp_date) VALUES (?, ?, ?, ?)",
                           (barcode, name, desc, exp_date))
            conn.commit()
            refresh_inventory_table()
        else:
            messagebox.showerror("Error", "Medicine not found in database.")
    except ValueError:
        messagebox.showerror("Error", "Invalid expiration date format.")

def delete_inventory():
    selected = inv_tree.selection()
    if selected:
        inv_id = inv_tree.item(selected[0])['values'][0]
        cursor.execute("DELETE FROM inventory WHERE id = ?", (inv_id,))
        conn.commit()
        refresh_inventory_table()

ttk.Button(inv_input_frame, text="Add Inventory", command=add_inventory).grid(row=2, column=0, pady=5)
ttk.Button(inv_input_frame, text="Delete Selected", command=delete_inventory).grid(row=2, column=1, pady=5)

# Inventory table
inv_tree = ttk.Treeview(inventory_tab, columns=("ID", "Barcode", "Name", "Description", "Exp Date"), show='headings')
for col in ("ID", "Barcode", "Name", "Description", "Exp Date"):
    inv_tree.heading(col, text=col)
inv_tree.pack(fill='both', expand=True, padx=10, pady=5)

def refresh_inventory_table():
    for row in inv_tree.get_children():
        inv_tree.delete(row)
    for row in cursor.execute("SELECT * FROM inventory"):
        values = list(row)
        exp_date = values[-1]
        try:
            if datetime.strptime(exp_date, "%Y-%m-%d") < datetime.now():
                inv_tree.insert("", "end", values=values, tags=('expired',))
            else:
                inv_tree.insert("", "end", values=values)
        except:
            continue
    inv_tree.tag_configure('expired', background='red')

refresh_inventory_table()


# ------------------ Medicine Tab ------------------
medicine_tab = ttk.Frame(notebook)
notebook.add(medicine_tab, text="Medicine Database")

# Medicine input frame
med_input_frame = ttk.LabelFrame(medicine_tab, text="Add Medicine")
med_input_frame.pack(fill='x', padx=10, pady=5)

tk.Label(med_input_frame, text="Barcode:").grid(row=0, column=0)
tk.Label(med_input_frame, text="Name:").grid(row=1, column=0)
tk.Label(med_input_frame, text="Description:").grid(row=2, column=0)

med_barcode_entry = tk.Entry(med_input_frame)
med_name_entry = tk.Entry(med_input_frame)
med_desc_entry = tk.Entry(med_input_frame)

med_barcode_entry.grid(row=0, column=1)
med_name_entry.grid(row=1, column=1)
med_desc_entry.grid(row=2, column=1)

def add_medicine():
    barcode = med_barcode_entry.get()
    name = med_name_entry.get()
    desc = med_desc_entry.get()
    if barcode and name:
        try:
            cursor.execute("INSERT INTO medicine VALUES (?, ?, ?)", (barcode, name, desc))
            conn.commit()
            refresh_medicine_table()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Barcode already exists.")
    else:
        messagebox.showerror("Error", "Barcode and Name are required.")

def delete_medicine():
    selected = med_tree.selection()
    if selected:
        barcode = med_tree.item(selected[0])['values'][0]
        cursor.execute("DELETE FROM medicine WHERE barcode = ?", (barcode,))
        conn.commit()
        refresh_medicine_table()

ttk.Button(med_input_frame, text="Add Medicine", command=add_medicine).grid(row=3, column=0, pady=5)
ttk.Button(med_input_frame, text="Delete Selected", command=delete_medicine).grid(row=3, column=1, pady=5)

# Medicine table
med_tree = ttk.Treeview(medicine_tab, columns=("Barcode", "Name", "Description"), show='headings')
for col in ("Barcode", "Name", "Description"):
    med_tree.heading(col, text=col)
med_tree.pack(fill='both', expand=True, padx=10, pady=5)

def refresh_medicine_table():
    for row in med_tree.get_children():
        med_tree.delete(row)
    for row in cursor.execute("SELECT * FROM medicine"):
        med_tree.insert("", "end", values=row)

refresh_medicine_table()


style = ttk.Style()
style.theme_use('default')
style.configure('Custom.TFrame', background=LIGHTBLUE)
medicine_tab.configure(style='Custom.TFrame')
inventory_tab.configure(style='Custom.TFrame')

style.configure('Custom.TLabelframe', background=LIGHTBLUE, foreground=DARKBLUE)
style.configure('Custom.TLabelframe.Label', background=LIGHTBLUE, foreground=DARKBLUE)
med_input_frame.configure(style='Custom.TLabelframe')
inv_input_frame.configure(style='Custom.TLabelframe')


for widget in med_input_frame.winfo_children():
    if isinstance(widget, tk.Label):
        widget.configure(bg=LIGHTBLUE, fg=DARKBLUE)
    elif isinstance(widget, tk.Entry):
        widget.configure(bg='white', fg=DARKBLUE)

for widget in inv_input_frame.winfo_children():
    if isinstance(widget, tk.Label):
        widget.configure(bg=LIGHTBLUE, fg=DARKBLUE)
    elif isinstance(widget, tk.Entry):
        widget.configure(bg='white', fg=DARKBLUE)

# Notebook background
style.configure('TNotebook', background=LIGHTBLUE, borderwidth=0)

# Tab styling
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

ttk.Button(med_input_frame, text="Add Medicine", command=add_medicine, style='Custom.TButton').grid(row=3, column=0, pady=5)
ttk.Button(med_input_frame, text="Delete Selected", command=delete_medicine, style='Custom.TButton').grid(row=3, column=1, pady=5)

ttk.Button(inv_input_frame, text="Add Inventory", command=add_inventory, style='Custom.TButton').grid(row=2, column=0, pady=5)
ttk.Button(inv_input_frame, text="Delete Selected", command=delete_inventory, style='Custom.TButton').grid(row=2, column=1, pady=5)


icon = tk.PhotoImage(file="favicon.png")
root.iconphoto(False, icon)

###################################
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime

def generate_inventory_pdf():
    cursor.execute("SELECT id, barcode, name, description, exp_date FROM inventory ORDER BY name ASC")
    data = cursor.fetchall()

    doc = SimpleDocTemplate("inventory_report.pdf", pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    elements.append(Paragraph("Inventory Report", styles['Title']))
    elements.append(Spacer(1, 6))

    # Add current date
    current_date = datetime.now().strftime("Created on: %Y-%m-%d")
    elements.append(Paragraph(current_date, styles['Normal']))
    elements.append(Spacer(1, 12))

    # Table header
    table_data = [["ID", "Barcode", "Name", "Description", "Expiration Date"]]

    # Table rows
    for row in data:
        exp_date = row[-1]
        try:
            if datetime.strptime(exp_date, "%Y-%m-%d") < datetime.now():
                styled_row = [Paragraph(f'<font color="red">{cell}</font>', styles['Normal']) for cell in row]
                table_data.append(styled_row)
            else:
                table_data.append([Paragraph(str(cell), styles['Normal']) for cell in row])
        except:
            table_data.append([Paragraph(str(cell), styles['Normal']) for cell in row])

    # Create table
    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#024275')),  # DARKBLUE header
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor('#5eabeb')])  # LIGHTBLUE
    ]))

    elements.append(table)
    doc.build(elements)
    messagebox.showinfo("PDF Generated", "Inventory report saved as 'inventory_report.pdf'")

ttk.Button(inventory_tab, text="Generate Inventory PDF", command=generate_inventory_pdf, style='Custom.TButton').pack(pady=10)
###################################

root.mainloop()