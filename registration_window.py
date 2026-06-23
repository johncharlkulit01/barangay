import customtkinter as ctk
from tkinter import messagebox
from db_config import get_db_connection
import mysql.connector
import hashlib


class SearchableDropdown(ctk.CTkFrame):
    def __init__(self, master, values, placeholder="Select", command=None):
        super().__init__(master, fg_color="transparent")

        self.values = values
        self.command = command

        self.var = ctk.StringVar()

        self.entry = ctk.CTkEntry(
            self, 
            textvariable=self.var, 
            placeholder_text=placeholder,
            height=40,
            fg_color="#FFFFFF",
            border_color="#CBD5E1",
            text_color="#1E293B"
        )
        self.entry.pack(fill="x", ipady=5)

        self.listbox_frame = ctk.CTkFrame(self, fg_color="#F8FAFC", corner_radius=8, border_width=1, border_color="#E2E8F0")
        self.listbox_frame.pack(fill="x", pady=(3, 0))
        self.listbox_frame.pack_forget()

        self.items = []

        self.entry.bind("<KeyRelease>", self.filter_list)
        self.entry.bind("<FocusOut>", lambda e: self.listbox_frame.pack_forget())

    def filter_list(self, event=None):
        text = self.var.get().lower()

        for widget in self.items:
            widget.destroy()
        self.items.clear()

        if not text:
            self.listbox_frame.pack_forget()
            return

        filtered = [v for v in self.values if text in v.lower()]

        if not filtered:
            self.listbox_frame.pack_forget()
            return

        self.listbox_frame.pack(fill="x")

        for value in filtered:
            btn = ctk.CTkButton(
                self.listbox_frame,
                text=value,
                fg_color="transparent",
                hover_color="#E2E8F0",
                text_color="#1E293B",
                anchor="w",
                height=36,
                command=lambda v=value: self.select(v)
            )
            btn.pack(fill="x", padx=4, pady=2)
            self.items.append(btn)

    def select(self, value):
        self.var.set(value)
        self.listbox_frame.pack_forget()
        if self.command:
            self.command(value)

    def get(self):
        return self.var.get()

    def set(self, value):
        self.var.set(value)


class RegistrationWindow(ctk.CTkToplevel):
    def __init__(self, app_controller):
        super().__init__()
        self.app = app_controller
        self.title("Resident Registration")

        self.resizable(False, False)

        # CENTER WINDOW
        window_width = 1200
        window_height = 700

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = int((screen_width / 2) - (window_width / 2))
        y = int((screen_height / 2) - (window_height / 2))

        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # ✅ Light Theme Base Color
        self.configure(fg_color="#F8FAFC")

        self.bind("<Escape>", lambda e: self.close_window())

        # Back Button
        ctk.CTkButton(
            self,
            text="← Back to Login",
            fg_color="transparent",
            text_color="#3B82F6",
            hover_color="#E2E8F0",
            font=("Segoe UI", 13),
            command=self.close_window
        ).pack(anchor="w", padx=25, pady=(15, 0))

        # Header
        ctk.CTkLabel(
            self,
            text="📝 Create Your Account",
            font=("Segoe UI", 24, "bold"),
            text_color="#1E293B"
        ).pack(pady=(15, 25))

        # Location Data
        self.location_data = {
            "Cavite - Bacoor": ["Alima", "Aniban I", "Aniban II"],
            "Cavite - Carmona": ["Maduya", "Lantic"],
            "Cavite - Cavite City": ["San Roque", "San Francisco"],
            "Cavite - Dasmariñas": ["Salitran I", "Salitran II", "Paliparan"],
            "Cavite - General Trias": ["Bacao", "San Francisco"],
            "Cavite - Imus": ["Alapan I", "Anabu I"],
            "Cavite - Tagaytay": ["Sungay South", "Silang Junction"],
            "Cavite - Trece Martires": ["San Agustin", "San Miguel"],

            "Laguna - Calamba": ["Bagong Kalsada", "Banlic", "Canlubang"],
            "Laguna - San Pedro City": ["Landayan", "Sto. Niño"],
            "Laguna - Biñan City": ["Sto. Domingo", "San Antonio"],
            "Laguna - Santa Rosa City": ["Balibago", "Don Jose"],
            "Laguna - Cabuyao City": ["Banlic", "Marinig"],
            "Laguna - San Pablo City": ["San Vicente", "San Gabriel"],

            "Batangas - Lipa City": ["Adya", "Balintawak"],
            "Batangas City": ["Alangilan", "Bolbok"],
            "Tanauan": ["Altura", "Bañadero"],
            "Santo Tomas": ["San Vicente", "San Miguel"],
            "Calaca": ["Dacanlao", "Quisumbing"],

            "Rizal - Antipolo City": ["Cupang", "De la Paz", "Mambugan"],
            "Angono": ["Poblacion Ibaba", "San Roque"],
            "Baras": ["San Salvador", "Concepcion"],
            "Binangonan": ["Batingan", "Darangan"],
            "Cainta": ["San Andres", "Santo Domingo"],
            "Cardona": ["Del Remedio", "Calahan"],
            "Jalajala": ["Bayugo", "Punta"],
            "Morong": ["San Pedro", "San Juan"],
            "Pililla": ["Malaya", "Bagumbayan"],
            "Montalban (Rodriguez)": ["Balite", "San Isidro"],
            "San Mateo": ["Guitnang Bayan", "Ampid"],
            "Tanay": ["Cayabu", "Sampaloc"],
            "Taytay": ["Dolores", "San Juan"],
            "Teresa": ["May-Iba", "Bagumbayan"],

            "Quezon - Lucena": ["Gulang-Gulang", "Dalahican"],
            "Tayabas City": ["Wakas", "Gibanga"],

            # NCR / Metro Manila
            "Manila": ["Ermita", "Malate", "Sampaloc", "Tondo"],
            "Quezon City": ["Diliman", "Commonwealth", "Batasan Hills", "Novaliches"],
            "Makati City": ["Poblacion", "Bel-Air", "San Lorenzo", "Bangkal"],
            "Pasig City": ["Ugong", "Ortigas Center", "Rosario", "Santolan"],
            "Taguig City": ["Fort Bonifacio", "Pinagsama", "Western Bicutan"],
            "Pasay City": ["Baclaran", "Malibay", "San Rafael"],
            "Mandaluyong City": ["Plainview", "Addition Hills", "Wack-Wack Greenhills"],
            "San Juan City": ["Greenhills", "Little Baguio", "West Crame"],
            "Marikina City": ["Concepcion Uno", "Parang", "Marikina Heights"],
            "Parañaque City": ["Baclaran", "Don Bosco", "BF Homes"],
            "Las Piñas City": ["Almanza Uno", "Pamplona Tres", "Zapote"],
            "Muntinlupa City": ["Alabang", "Tunasan", "Putatan"],
            "Caloocan City": ["Bagong Barrio", "Grace Park", "Bagumbong"],
            "Malabon City": ["Potrero", "Tinajeros", "Longos"],
            "Navotas City": ["Bagumbayan North", "San Roque", "Tangos"],
            "Valenzuela City": ["Karuhatan", "Marulas", "Paso de Blas"],
            "Pateros": ["Aguho", "San Pedro", "Sta. Ana"]
        }

        # Main Container
        main_container = ctk.CTkFrame(self, fg_color="#F8FAFC")
        main_container.pack(fill="both", expand=True)

        # Form Frame ✅ Light Theme
        self.form_frame = ctk.CTkScrollableFrame(
            main_container, 
            fg_color="#FFFFFF", 
            corner_radius=15,
            border_width=1,
            border_color="#E2E8F0"
        )
        self.form_frame.pack(fill="both", expand=True, padx=60, pady=20)

        # Input Fields
        self.fullname = self.create_input("Full Name")
        self.age = self.create_input("Age")
        self.email = self.create_input("Email Address")
        self.address = self.create_input("Complete Address")
        self.contact = self.create_input("Contact Number")
        self.valid_id_entry = self.create_input("Valid ID Number")
        self.username = self.create_input("Username")

        self.password = self.create_password_input("Password")
        self.confirm_password = self.create_password_input("Confirm Password")

        # ✅ GINAWANG KAGAYA NG COMOBOX SA LOGIN
        self.gender = self.create_standard_combobox(["Male", "Female", "Other"], "Gender")
        self.civil_status = self.create_standard_combobox(
            ["Single", "Married", "Widowed", "Separated"],
            "Civil Status"
        )

        # Location Details
        ctk.CTkLabel(
            self.form_frame, 
            text="📍 Location Details", 
            font=("Segoe UI", 15, "bold"),
            text_color="#334155"
        ).pack(pady=(20, 5), anchor="w")

        # ✅ GINAWANG KAGAYA NG COMOBOX SA LOGIN
        self.city = self.create_standard_combobox(
            list(self.location_data.keys()), 
            "Select City",
            command=self.update_barangay_list
        )

        self.barangay = self.create_standard_combobox([], "Select City First")
        self.barangay.configure(state="disabled")

        # Register Button ✅ Matches main app
        self.register_btn = ctk.CTkButton(
            self.form_frame,
            text="✅ REGISTER ACCOUNT",
            fg_color="#16A34A",
            hover_color="#15803D",
            text_color="#FFFFFF",
            height=44,
            font=("Segoe UI", 14, "bold"),
            corner_radius=10,
            command=self.register_user
        )
        self.register_btn.pack(fill="x", pady=25)

    # ✅ BAGONG FUNCTION: Parehong style ng combobox sa login
    def create_standard_combobox(self, values, placeholder, command=None):
        combo = ctk.CTkComboBox(
            self.form_frame,
            values=values,
            height=40,
            fg_color="#FFFFFF",
            border_color="#CBD5E1",
            text_color="#1E293B",
            button_color="#3B82F6",
            button_hover_color="#2563EB",
            command=command
        )
        combo.pack(pady=6, fill="x")
        combo.set(placeholder)
        # ✅ Same click behavior
        combo.bind("<Button-1>", lambda e: combo._clicked())
        return combo

    def create_input(self, placeholder):
        entry = ctk.CTkEntry(
            self.form_frame, 
            placeholder_text=placeholder, 
            height=40,
            fg_color="#FFFFFF",
            border_color="#CBD5E1",
            text_color="#1E293B"
        )
        entry.pack(pady=6, fill="x")
        return entry

    def create_password_input(self, placeholder):
        frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        frame.pack(pady=6, fill="x")

        entry = ctk.CTkEntry(
            frame, 
            placeholder_text=placeholder, 
            show="*", 
            height=40,
            fg_color="#FFFFFF",
            border_color="#CBD5E1",
            text_color="#1E293B"
        )
        entry.pack(side="left", fill="x", expand=True)

        def toggle():
            if entry.cget("show") == "*":
                entry.configure(show="")
                btn.configure(text="🙈")
            else:
                entry.configure(show="*")
                btn.configure(text="👁")

        btn = ctk.CTkButton(
            frame, 
            text="👁", 
            width=42, 
            height=40,
            fg_color="#E2E8F0",
            hover_color="#CBD5E1",
            text_color="#1E293B",
            corner_radius=6,
            command=toggle
        )
        btn.pack(side="right", padx=5)

        return entry

    def update_barangay_list(self, city):
        barangays = self.location_data.get(city, [])
        if barangays:
            self.barangay.configure(values=barangays, state="normal", fg_color="#FFFFFF")
            self.barangay.set("Select Barangay")
        else:
            self.barangay.configure(values=[], state="disabled", fg_color="#F1F5F9")
            self.barangay.set("Select City First")
    
    def close_window(self):
        self.app.deiconify()   # show login again
        self.destroy()

    def register_user(self):
        city = self.city.get()
        barangay = self.barangay.get()

        full_name = self.fullname.get().strip()
        username = self.username.get().strip()
        password = self.password.get().strip()
        confirm = self.confirm_password.get().strip()

        email = self.email.get().strip()
        contact = self.contact.get().strip()

        if not all([full_name, username, password, email, contact]):
            messagebox.showwarning("Incomplete", "Please fill up all required fields")
            return

        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return

        if city in ["Select City", "", None] or barangay in ["Select Barangay", "", None]:
            messagebox.showwarning("Incomplete", "Please select your City and Barangay")
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            hashed = hashlib.sha256(password.encode()).hexdigest()

            cursor.execute("""
                INSERT INTO users
                (username, password, full_name, email, contact, address,
                gender, civil_status, valid_id_number, city, barangay, role)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'resident')
            """, (
                username,
                hashed,
                full_name,
                email,
                contact,
                self.address.get(),
                self.gender.get(),
                self.civil_status.get(),
                self.valid_id_entry.get(),
                city,
                barangay
            ))

            conn.commit()
            messagebox.showinfo("Success", "✅ Account created successfully! You can now login.")
            self.close_window()

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {str(err)}")

        finally:
            if conn:
                conn.close()