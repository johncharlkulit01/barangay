import customtkinter as ctk
import os
from datetime import datetime
from tkinter import messagebox
from db_config import get_db_connection


class AdminSettingsDashboard(ctk.CTkFrame):

    def __init__(self, master, app_controller):
        # ✅ PALIT NG KULAY: Main background mula sa light theme
        super().__init__(master, fg_color="#f1f5f9")

        self.app = app_controller
        self.pack(fill="both", expand=True, padx=15, pady=15)

        self.show_pass_old = False
        self.show_pass_new = False
        self.show_pass_confirm = False

        # Header
        ctk.CTkLabel(
            self,
            text="ADMIN SYSTEM SETTINGS",
            font=("Segoe UI", 26, "bold"),
            text_color="#1e293b"  # ✅ Kulay ng text mula sa light
        ).pack(pady=(10, 20))

        # Main container
        main = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=15)  # ✅ Kulay mula sa light
        main.pack(fill="both", expand=True, padx=10, pady=10)

        # Left panel - Admin Info
        left = ctk.CTkFrame(main, fg_color="#f8fafc", width=320, corner_radius=12)  # ✅ Kulay mula sa light
        left.pack(side="left", fill="y", padx=15, pady=15)
        left.pack_propagate(False)

        ctk.CTkLabel(
            left, 
            text="ADMIN PROFILE", 
            font=("Segoe UI", 18, "bold"),
            text_color="#1e293b"  # ✅ Kulay ng text
        ).pack(pady=(20, 15))

        info_frame = ctk.CTkFrame(left, fg_color="#ffffff", corner_radius=10)  # ✅ Kulay mula sa light
        info_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(
            info_frame, 
            text="Admin Information", 
            text_color="#64748b",  # ✅ Kulay ng text
            font=("Segoe UI", 13)
        ).pack(anchor="w", padx=15, pady=(15, 5))

        ctk.CTkLabel(
            info_frame, 
            text=f"👤 Username: {self.app.username}", 
            text_color="#1e293b",  # ✅ Kulay ng text
            font=("Segoe UI", 14)
        ).pack(anchor="w", padx=15, pady=3)
        
        ctk.CTkLabel(
            info_frame, 
            text=f"🎖️ Role: {self.app.role}", 
            text_color="#1e293b",  # ✅ Kulay ng text
            font=("Segoe UI", 14)
        ).pack(anchor="w", padx=15, pady=(3, 15))

        # Scrollable right area
        right = ctk.CTkScrollableFrame(main, fg_color="transparent")
        right.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        # Change Password Section
        pass_section = ctk.CTkFrame(right, fg_color="#ffffff", corner_radius=12)  # ✅ Kulay mula sa light
        pass_section.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            pass_section, 
            text="🔑 Change Admin Password", 
            font=("Segoe UI", 16, "bold"),
            text_color="#1e293b"  # ✅ Kulay ng text
        ).pack(anchor="w", padx=20, pady=(15, 10))

        # Old Password
        self.old_pass = ctk.CTkEntry(
            pass_section, 
            placeholder_text="Enter Old Password", 
            show="*",
            fg_color="#f8fafc",  # ✅ Kulay ng input
            border_color="#cbd5e1",  # ✅ Kulay ng border
            text_color="#1e293b",  # ✅ Kulay ng text sa loob
            height=40
        )
        self.old_pass.pack(fill="x", padx=20, pady=5)

        self.old_eye = ctk.CTkButton(
            pass_section, 
            text="👁", 
            width=45, 
            height=30,
            fg_color="transparent",
            hover_color="#e2e8f0",  # ✅ Kulay ng hover
            command=self.toggle_old
        )
        self.old_eye.pack(anchor="e", padx=20, pady=(0, 10))

        # New Password
        self.new_pass = ctk.CTkEntry(
            pass_section, 
            placeholder_text="Enter New Password", 
            show="*",
            fg_color="#f8fafc",  # ✅ Kulay ng input
            border_color="#cbd5e1",
            text_color="#1e293b",
            height=40
        )
        self.new_pass.pack(fill="x", padx=20, pady=5)

        self.new_eye = ctk.CTkButton(
            pass_section, 
            text="👁", 
            width=45, 
            height=30,
            fg_color="transparent",
            hover_color="#e2e8f0",
            command=self.toggle_new
        )
        self.new_eye.pack(anchor="e", padx=20, pady=(0, 10))

        # Confirm Password
        self.confirm_pass = ctk.CTkEntry(
            pass_section, 
            placeholder_text="Confirm New Password", 
            show="*",
            fg_color="#f8fafc",
            border_color="#cbd5e1",
            text_color="#1e293b",
            height=40
        )
        self.confirm_pass.pack(fill="x", padx=20, pady=5)

        self.confirm_eye = ctk.CTkButton(
            pass_section, 
            text="👁", 
            width=45, 
            height=30,
            fg_color="transparent",
            hover_color="#e2e8f0",
            command=self.toggle_confirm
        )
        self.confirm_eye.pack(anchor="e", padx=20, pady=(0, 10))

        ctk.CTkButton(
            pass_section,
            text="Update Password",
            fg_color="#3b82f6",  # ✅ Kulay ng button mula sa light
            hover_color="#2563eb",
            height=40,
            font=("Segoe UI", 14, "bold"),
            command=self.update_password
        ).pack(pady=(0, 20), fill="x", padx=20)

        # Barangay Information Section
        brgy_section = ctk.CTkFrame(right, fg_color="#ffffff", corner_radius=12)  # ✅ Kulay mula sa light
        brgy_section.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            brgy_section, 
            text="🏘️ Barangay Information", 
            font=("Segoe UI", 16, "bold"),
            text_color="#1e293b"
        ).pack(anchor="w", padx=20, pady=(15, 10))

        self.barangay_entry = ctk.CTkEntry(
            brgy_section, 
            placeholder_text="Barangay Name",
            fg_color="#f8fafc",
            border_color="#cbd5e1",
            text_color="#1e293b",
            height=40
        )
        self.barangay_entry.pack(fill="x", padx=20, pady=5)

        self.captain_entry = ctk.CTkEntry(
            brgy_section, 
            placeholder_text="Captain / Chairman Full Name",
            fg_color="#f8fafc",
            border_color="#cbd5e1",
            text_color="#1e293b",
            height=40
        )
        self.captain_entry.pack(fill="x", padx=20, pady=5)

        # Appointment Settings
        appt_section = ctk.CTkFrame(brgy_section, fg_color="transparent")
        appt_section.pack(fill="x", padx=20, pady=(15, 20))

        ctk.CTkLabel(
            appt_section, 
            text="📅 Maximum Daily Appointments", 
            font=("Segoe UI", 14, "bold"),
            text_color="#1e293b"
        ).pack(anchor="w", pady=(0, 5))

        self.max_appointments = ctk.CTkEntry(
            appt_section,
            placeholder_text="e.g. 50",
            fg_color="#f8fafc",
            border_color="#cbd5e1",
            text_color="#1e293b",
            height=40
        )
        self.max_appointments.pack(fill="x", pady=5)

        # Action Buttons
        ctk.CTkButton(
            right,
            text="💾 Save System Changes",
            fg_color="#22c55e",  # ✅ Kulay mula sa light
            hover_color="#16a34a",
            height=42,
            font=("Segoe UI", 14, "bold"),
            command=self.save_settings
        ).pack(pady=(0, 10), fill="x")

        ctk.CTkButton(
            right,
            text="💿 Backup Database",
            fg_color="#fbbf24",  # ✅ Kulay mula sa light
            hover_color="#f59e0b",
            height=42,
            font=("Segoe UI", 14, "bold"),
            command=self.backup_database
        ).pack(fill="x")

        self.load_settings()

    # --- Toggle Password Visibility ---
    def toggle_old(self):
        self.show_pass_old = not self.show_pass_old
        self.old_pass.configure(show="" if self.show_pass_old else "*")

    def toggle_new(self):
        self.show_pass_new = not self.show_pass_new
        self.new_pass.configure(show="" if self.show_pass_new else "*")

    def toggle_confirm(self):
        self.show_pass_confirm = not self.show_pass_confirm
        self.confirm_pass.configure(show="" if self.show_pass_confirm else "*")

    # --- Load Settings from DB ---
    def load_settings(self):
        conn = get_db_connection()
        if not conn:
            return

        try:
            cur = conn.cursor()
            cur.execute("SELECT setting_key, setting_value FROM system_settings")
            data = dict(cur.fetchall())

            self.barangay_entry.insert(0, data.get("barangay_name", ""))
            self.captain_entry.insert(0, data.get("captain_name", ""))
            self.max_appointments.insert(
                0,
                data.get("max_daily_appointments", "50")
            )

        finally:
            cur.close()
            conn.close()

    # --- Save Settings ---
    def save_settings(self):
        barangay = self.barangay_entry.get().strip()
        captain = self.captain_entry.get().strip()
        max_daily = self.max_appointments.get().strip()

        if not barangay or not captain or not max_daily:
            messagebox.showwarning("Warning", "Please fill in all fields!")
            return

        conn = get_db_connection()
        if not conn:
            return

        try:
            cur = conn.cursor()

            cur.execute("""
                UPDATE system_settings
                SET setting_value=%s
                WHERE setting_key='barangay_name'
            """, (barangay,))

            cur.execute("""
                UPDATE system_settings
                SET setting_value=%s
                WHERE setting_key='captain_name'
            """, (captain,))

            cur.execute("""
                UPDATE system_settings
                SET setting_value=%s
                WHERE setting_key='max_daily_appointments'
            """, (max_daily,))

            conn.commit()
            messagebox.showinfo("Success", "System settings updated successfully!")

        finally:
            cur.close()
            conn.close()

    # --- Update Password ---
    def update_password(self):
        old = self.old_pass.get().strip()
        new = self.new_pass.get().strip()
        confirm = self.confirm_pass.get().strip()

        if not old or not new or not confirm:
            messagebox.showwarning("Warning", "All password fields are required!")
            return

        if new != confirm:
            messagebox.showerror("Error", "New passwords do not match")
            return

        if len(new) < 6:
            messagebox.showwarning("Warning", "Password must be at least 6 characters long")
            return

        conn = get_db_connection()
        if not conn:
            return

        try:
            cur = conn.cursor()
            cur.execute("SELECT password FROM users WHERE username=%s", (self.app.username,))
            data = cur.fetchone()

            if not data or data[0] != old:
                messagebox.showerror("Error", "Current password is incorrect")
                return

            cur.execute("""
                UPDATE users
                SET password=%s
                WHERE username=%s
            """, (new, self.app.username))

            conn.commit()
            messagebox.showinfo("Success", "Password updated successfully!")
            
            # Clear fields after success
            self.old_pass.delete(0, "end")
            self.new_pass.delete(0, "end")
            self.confirm_pass.delete(0, "end")

        finally:
            cur.close()
            conn.close()

    # --- Backup Database ---
    def backup_database(self):
        try:
            filename = f"barangay_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
            command = f"mysqldump -u root barangay_systsem > {filename}"

            os.system(command)
            messagebox.showinfo(
                "Backup Complete",
                f"Database backup saved as:\n{filename}"
            )

        except Exception as e:
            messagebox.showerror("Error", f"Backup failed: {str(e)}")