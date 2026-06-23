import customtkinter as ctk
from tkinter import messagebox
from db_config import get_db_connection
from datetime import datetime
from tkinter import filedialog
from tkcalendar import DateEntry
import threading


class RequestFormWindow(ctk.CTkFrame):
    def __init__(self, master, app, username, role, extra):
        super().__init__(master, fg_color="#F8FAFC")
        self.app = app
        self.username = username
        self.pack(fill="both", expand=True)

        # Scrollable Container
        self.scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=15,
            border_width=1,
            border_color="#E2E8F0"
        )
        self.scroll.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        ctk.CTkLabel(
            self.scroll,
            text="📝 CREATE APPOINTMENT",
            font=("Segoe UI", 28, "bold"),
            text_color="#1E293B"
        ).pack(pady=(25, 30))

        # ----------------------
        # 1. Full Name - READ ONLY
        # ----------------------
        self.name_entry = ctk.CTkEntry(
            self.scroll,
            placeholder_text="Full Name",
            height=45,
            fg_color="#F1F5F9",
            border_color="#CBD5E1",
            text_color="#1E293B"
        )
        self.name_entry.pack(fill="x", pady=8, padx=15)

        # ----------------------
        # 2. Gender ComboBox
        # ----------------------
        self.gender_entry = ctk.CTkComboBox(
            self.scroll,
            values=["Male", "Female", "Other"],
            height=45,
            fg_color="#FFFFFF",
            border_color="#CBD5E1",
            text_color="#1E293B",
            button_color="#3B82F6",
            button_hover_color="#2563EB"
        )
        self.gender_entry.set("Select Gender")
        self.gender_entry.pack(fill="x", pady=8, padx=15)
        self.gender_entry.bind("<Button-1>", lambda e: self.gender_entry._clicked())

        # ----------------------
        # 3. Service ComboBox
        # ----------------------
        self.service = ctk.CTkComboBox(
            self.scroll,
            values=[
                "Barangay Clearance", "Certificate of Residency",
                "Barangay Business Clearance", "Barangay Indigency",
                "Barangay Construction Clearance", "Barangay Calamity Certification",
                "First-Time Jobseeker Certificate", "Barangay ID", "PWD ID", "Senior Citizen ID",
            ],
            height=45,
            fg_color="#FFFFFF",
            border_color="#CBD5E1",
            text_color="#1E293B",
            button_color="#3B82F6",
            button_hover_color="#2563EB"
        )
        self.service.set("Select Service")
        self.service.pack(fill="x", pady=8, padx=15)
        self.service.configure(command=self.show_requirements)
        self.service.bind("<Button-1>", lambda e: self.service._clicked())

        # ----------------------
        # 4. Contact Number
        # ----------------------
        self.contact_entry = ctk.CTkEntry(
            self.scroll,
            placeholder_text="Contact Number (11 digits)",
            height=45,
            fg_color="#FFFFFF",
            border_color="#CBD5E1",
            text_color="#1E293B"
        )
        self.contact_entry.pack(fill="x", pady=8, padx=15)

        # ----------------------
        # 5. Address
        # ----------------------
        self.address_entry = ctk.CTkEntry(
            self.scroll,
            placeholder_text="Full Address",
            height=45,
            fg_color="#FFFFFF",
            border_color="#CBD5E1",
            text_color="#1E293B"
        )
        self.address_entry.pack(fill="x", pady=8, padx=15)

        # ----------------------
        # 6. Date Picker
        # ----------------------
        self.date_entry = DateEntry(
            self.scroll,
            width=20,
            height=45,
            background='#16A34A',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd',
            font=("Segoe UI", 12),
            bordercolor="#CBD5E1"
        )
        self.date_entry.pack(fill="x", pady=8, padx=15)
        self.date_entry.bind("<Button-1>", lambda e: self.date_entry.drop_down())

        # ----------------------
        # 7. Email
        # ----------------------
        self.email_entry = ctk.CTkEntry(
            self.scroll,
            placeholder_text="Email Address",
            height=45,
            fg_color="#FFFFFF",
            border_color="#CBD5E1",
            text_color="#1E293B"
        )
        self.email_entry.pack(fill="x", pady=8, padx=15)

        # ----------------------
        # 8. Time Selection
        # ----------------------
        self.time_entry = ctk.CTkComboBox(
            self.scroll,
            values=[
                "08:00 AM", "09:00 AM", "10:00 AM",
                "11:00 AM", "01:00 PM", "02:00 PM",
                "03:00 PM", "04:00 PM"
            ],
            height=45,
            fg_color="#FFFFFF",
            border_color="#CBD5E1",
            text_color="#1E293B",
            button_color="#3B82F6",
            button_hover_color="#2563EB"
        )
        self.time_entry.set("08:00 AM")
        self.time_entry.pack(fill="x", pady=8, padx=15)
        self.time_entry.bind("<Button-1>", lambda e: self.time_entry._clicked())

        # ----------------------
        # 9. Purpose Textbox - IMPROVED PLACEHOLDER
        # ----------------------
        self.purpose = ctk.CTkTextbox(
            self.scroll,
            height=90,
            fg_color="#FFFFFF",
            border_color="#CBD5E1",
            border_width=2,
            corner_radius=8,
            text_color="#94A3B8"  # Gray color for placeholder
        )
        self.purpose.pack(fill="x", pady=10, padx=15)
        self.purpose.insert("0.0", "Type your purpose here...")

        # Bind events for placeholder behavior
        self.purpose.bind("<FocusIn>", self._on_purpose_focus_in)
        self.purpose.bind("<FocusOut>", self._on_purpose_focus_out)

        # ----------------------
        # Requirements Label
        # ----------------------
        self.requirements_label = ctk.CTkLabel(
            self.scroll,
            text="📋 Requirements will appear here...",
            justify="left",
            font=("Segoe UI", 12),
            text_color="#475569"
        )
        self.requirements_label.pack(anchor="w", pady=(5, 10), padx=20)

        # ----------------------
        # File Upload
        # ----------------------
        self.file_path = ctk.StringVar()
        ctk.CTkButton(
            self.scroll,
            text="📎 Upload Requirement",
            command=self.upload_file,
            fg_color="#3B82F6",
            hover_color="#2563EB",
            text_color="#FFFFFF",
            height=42,
            corner_radius=8
        ).pack(fill="x", pady=8, padx=15)

        self.file_label = ctk.CTkLabel(
            self.scroll,
            text="No file selected",
            text_color="#64748B",
            font=("Segoe UI", 12)
        )
        self.file_label.pack(anchor="w", padx=20, pady=(0, 10))

        # ----------------------
        # Agreement Checkbox
        # ----------------------
        self.agree_check = ctk.CTkCheckBox(
            self.scroll,
            text="I certify that all information provided is true and correct.",
            font=("Segoe UI", 12),
            text_color="#1E293B",
            fg_color="#3B82F6",
            hover_color="#2563EB",
            border_color="#94A3B8"
        )
        self.agree_check.pack(anchor="w", pady=15, padx=20)

        # ----------------------
        # Load user data AFTER all fields are created
        # ----------------------
        self.load_user_info()

        # ----------------------
        # Submit Button
        # ----------------------
        self.submit_btn = ctk.CTkButton(
            self,
            text="✅ SUBMIT APPOINTMENT",
            fg_color="#16A34A",
            hover_color="#15803D",
            text_color="#FFFFFF",
            height=46,
            font=("Segoe UI", 14, "bold"),
            corner_radius=10,
            command=self.submit_appointment
        )
        self.submit_btn.pack(side="bottom", fill="x", padx=25, pady=20)

    # ----------------------
    # Placeholder Functions for Purpose
    # ----------------------
    def _on_purpose_focus_in(self, event):
        # If the text is still the placeholder, clear it and change color
        current_text = self.purpose.get("1.0", "end").strip()
        if current_text == "Type your purpose here...":
            self.purpose.delete("1.0", "end")
            self.purpose.configure(text_color="#1E293B")  # Normal text color

    def _on_purpose_focus_out(self, event):
        # If empty, put back the placeholder
        current_text = self.purpose.get("1.0", "end").strip()
        if not current_text:
            self.purpose.insert("1.0", "Type your purpose here...")
            self.purpose.configure(text_color="#94A3B8")  # Gray placeholder

    def load_user_info(self):
        conn = get_db_connection()
        if not conn:
            return

        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT full_name, contact, address, email
                FROM users
                WHERE username=%s
            """, (self.username,))
            row = cur.fetchone()

            if row:
                # Lagay ang pangalan, tapos i-disable
                if row["full_name"]:
                    self.name_entry.configure(state="normal")
                    self.name_entry.delete(0, "end")
                    self.name_entry.insert(0, row["full_name"])
                    self.name_entry.configure(state="disabled")

                if row["contact"]:
                    self.contact_entry.delete(0, "end")
                    self.contact_entry.insert(0, row["contact"])

                if row["address"]:
                    self.address_entry.delete(0, "end")
                    self.address_entry.insert(0, row["address"])

                if row["email"]:
                    self.email_entry.delete(0, "end")
                    self.email_entry.insert(0, row["email"])

        except Exception as e:
            messagebox.showerror("DB Error", f"Could not load user data: {e}")
        finally:
            cur.close()
            conn.close()

    def clear_form(self):
        # Reset name field
        self.name_entry.configure(state="normal")
        self.name_entry.delete(0, "end")
        self.name_entry.configure(state="disabled")

        # Reset others
        self.contact_entry.delete(0, "end")
        self.address_entry.delete(0, "end")
        self.email_entry.delete(0, "end")
        self.date_entry.set_date(datetime.today())
        
        # Reset Purpose with placeholder
        self.purpose.delete("1.0", "end")
        self.purpose.insert("1.0", "Type your purpose here...")
        self.purpose.configure(text_color="#94A3B8")
        
        self.service.set("Select Service")
        self.gender_entry.set("Select Gender")
        self.time_entry.set("08:00 AM")
        self.file_path.set("")
        self.file_label.configure(text="No file selected", text_color="#64748B")
        self.agree_check.deselect()

    def cancel_appointment(self, appointment_id):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("UPDATE appointments SET status='Cancelled by Resident' WHERE id=%s", (appointment_id,))
            conn.commit()
            messagebox.showinfo("Success", "Appointment cancelled successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not cancel: {e}")
        finally:
            if conn:
                conn.close()

    def show_requirements(self, service):
        reqs = {
            "Barangay Clearance": "• Valid Government ID\n• Latest Cedula",
            "Certificate of Residency": "• Valid Government ID\n• Proof of Address (Utility Bill)",
            "Barangay Business Clearance": "• DTI Registration\n• Valid ID\n• Lease Contract (if rented)",
            "Barangay Indigency": "• Valid ID\n• Certificate of Income / Tax Exemption",
            "First-Time Jobseeker Certificate": "• Valid ID\n• Birth Certificate / PSA"
        }
        self.requirements_label.configure(
            text=reqs.get(service, "• No specific requirements listed.")
        )

    def upload_file(self):
        file = filedialog.askopenfilename()
        if file:
            self.file_path.set(file)
            self.file_label.configure(text=f"✅ {file.split('/')[-1]}", text_color="#16A34A")

    def validate_date(self, date_text):
        try:
            datetime.strptime(date_text, "%Y-%m-%d")
            return True
        except:
            return False

    def submit_appointment(self):
        # Kunin value mula sa naka-disable na field
        self.name_entry.configure(state="normal")
        name = self.name_entry.get().strip()
        self.name_entry.configure(state="disabled")

        email = self.email_entry.get().strip()
        service = self.service.get().strip()
        contact = self.contact_entry.get().strip()
        date = self.date_entry.get().strip()
        time_val = self.time_entry.get().strip()
        
        # Get purpose, ignore placeholder text
        purpose_raw = self.purpose.get("1.0", "end").strip()
        purpose = "" if purpose_raw == "Type your purpose here..." else purpose_raw
        
        address = self.address_entry.get().strip()
        current_file_path = self.file_path.get()
        gender = self.gender_entry.get().strip()

        # ----------------------
        # Validation
        # ----------------------
        if not all([name, service, contact, date, time_val, purpose, address, gender]) or gender == "Select Gender":
            messagebox.showwarning("Missing Fields", "Please fill in all required fields.")
            return
        if self.agree_check.get() == 0:
            messagebox.showwarning("Agreement Required", "You must agree to the certification.")
            return
        if "@" not in email or "." not in email:
            messagebox.showerror("Invalid Email", "Please enter a valid email address.")
            return
        if not contact.isdigit() or len(contact) != 11:
            messagebox.showerror("Invalid Contact", "Contact must be 11 digits (e.g. 09171234567).")
            return
        if not self.validate_date(date):
            messagebox.showerror("Invalid Date", "Please select a valid date.")
            return

        confirm = messagebox.askyesno(
            "Confirm Appointment",
            f"""
Please confirm your details:

Name: {name}
Gender: {gender}
Service: {service}
Date: {date}
Time: {time_val}
Address: {address}

Proceed?
"""
        )
        if not confirm:
            return

        self.submit_btn.configure(state="disabled", text="Submitting...")

        threading.Thread(
            target=self.process_db_submission,
            args=(name, service, contact, date, time_val, purpose, current_file_path, gender, address, email),
            daemon=True
        ).start()

    def process_db_submission(self, name, service, contact, date, time_val, purpose,
                              current_file_path, gender, address, email):
        conn = None
        cur = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()

            # Check slot limit per time
            cur.execute("""
                SELECT COUNT(*) FROM appointments
                WHERE appointment_date=%s AND appointment_time=%s
            """, (date, time_val))
            count = cur.fetchone()[0]
            MAX_SLOT = 5
            if count >= MAX_SLOT:
                self.after(0, lambda: messagebox.showwarning(
                    "Slot Full", "This time slot is already fully booked. Please choose another."
                ))
                return

            # Check daily limit
            cur.execute("SELECT setting_value FROM system_settings WHERE setting_key='max_daily_appointments'")
            result = cur.fetchone()
            max_limit = int(result[0]) if result else 50

            cur.execute("SELECT COUNT(*) FROM appointments WHERE appointment_date=%s", (date,))
            daily_count = cur.fetchone()[0]
            if daily_count >= max_limit:
                self.after(0, lambda: messagebox.showwarning(
                    "Daily Limit Reached", f"Maximum {max_limit} appointments allowed per day."
                ))
                return

            # Create queue ID
            queue_id = f"Q-{datetime.now().strftime('%H%M%S')}"

            # Insert appointment
            cur.execute("""
                INSERT INTO appointments
                (queue_id, fullname, contact, document_type, purpose,
                appointment_date, appointment_time, status, username, file_path, gender, address, email)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                queue_id, name, contact, service, purpose, date, time_val,
                "Pending", self.username, current_file_path, gender, address, email
            ))

            # Get position in queue
            cur.execute("SELECT COUNT(*) FROM appointments WHERE status='Pending'")
            position = cur.fetchone()[0]

            # Insert into queue status
            cur.execute("""
                INSERT INTO queue_status (queue_no, position, now_serving, status)
                VALUES (%s, %s, %s, %s)
            """, (queue_id, position, "---", "Pending"))

            # Log to history
            cur.execute("""
                INSERT INTO transaction_history (username, action, details, queue_id)
                VALUES (%s,%s,%s,%s)
            """, (self.username, "Appointment Created", service, queue_id))

            conn.commit()

            self.after(0, self.show_success, queue_id, name, service, date, time_val, address)
            self.after(0, self.clear_form)

        except Exception as e:
            self.after(0, lambda err=e: messagebox.showerror("Error", f"Failed: {str(e)}"))
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
            self.after(0, lambda: self.submit_btn.configure(state="normal", text="SUBMIT APPOINTMENT"))

    def show_success(self, queue_id, name, service, date, time_val, address):
        messagebox.showinfo(
            "✅ Appointment Successful",
            f"""
Your appointment has been recorded!

Queue ID: {queue_id}
Name: {name}
Service: {service}
Date: {date}
Time: {time_val}
Address: {address}

Please keep this Queue ID for reference.
You will be notified once approved.
"""
        )