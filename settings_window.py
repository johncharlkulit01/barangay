import customtkinter as ctk
from tkinter import messagebox
from db_config import get_db_connection
import hashlib
import re

class SettingsDashboard(ctk.CTkFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="#F8FAFC")  # Light background
        self.app = app_controller
        self.pack(fill="both", expand=True)

        # --- Add Scrollable Frame ---
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="#F8FAFC",
            corner_radius=0
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.build_ui()
        self.load_profile()

    def build_ui(self):
        # --- Header ---
        ctk.CTkLabel(
            self.scroll_frame,
            text="⚙️ USER SETTINGS",
            font=("Segoe UI", 24, "bold"),
            text_color="#1E293B"
        ).pack(pady=(10, 25), anchor="w")

        # --- Profile Information Section ---
        profile_frame = ctk.CTkFrame(
            self.scroll_frame, 
            fg_color="#FFFFFF", 
            corner_radius=15,
            border_width=1,
            border_color="#E2E8F0"
        )
        profile_frame.pack(fill="x", pady=(0, 15), padx=5)

        ctk.CTkLabel(
            profile_frame,
            text="👤 Profile Information",
            font=("Segoe UI", 16, "bold"),
            text_color="#1E293B"
        ).pack(anchor="w", padx=20, pady=(15, 10))

        self.fullname = self.create_input(profile_frame, "Full Name")
        self.email = self.create_input(profile_frame, "Email Address")
        self.contact = self.create_input(profile_frame, "Contact Number")
        self.address = self.create_input(profile_frame, "Complete Address")

        ctk.CTkButton(
            profile_frame,
            text="💾 Save Profile",
            fg_color="#3B82F6",
            hover_color="#2563EB",
            text_color="#FFFFFF",
            corner_radius=8,
            command=self.save_profile
        ).pack(anchor="e", padx=20, pady=15)

        # --- Change Password Section ---
        pass_frame = ctk.CTkFrame(
            self.scroll_frame, 
            fg_color="#FFFFFF", 
            corner_radius=15,
            border_width=1,
            border_color="#E2E8F0"
        )
        pass_frame.pack(fill="x", pady=(0, 15), padx=5)

        ctk.CTkLabel(
            pass_frame,
            text="🔑 Change Password",
            font=("Segoe UI", 16, "bold"),
            text_color="#1E293B"
        ).pack(anchor="w", padx=20, pady=(15, 10))

        self.old_pass = self.create_password_field(pass_frame, "Old Password")
        self.new_pass = self.create_password_field(pass_frame, "New Password")
        self.confirm_pass = self.create_password_field(pass_frame, "Confirm New Password")

        ctk.CTkButton(
            pass_frame,
            text="🔄 Update Password",
            fg_color="#16A34A",
            hover_color="#15803D",
            text_color="#FFFFFF",
            corner_radius=8,
            command=self.change_password
        ).pack(anchor="e", padx=20, pady=15)

        # --- Activity Info ---
        self.activity_label = ctk.CTkLabel(
            self.scroll_frame, 
            text="Last login: Loading...", 
            text_color="#475569",
            font=("Segoe UI", 12)
        )
        self.activity_label.pack(pady=(5, 15))

        # --- Action Buttons ---
        ctk.CTkButton(
            self.scroll_frame,
            text="❌ Delete My Account",
            fg_color="#DC2626",
            hover_color="#B91C1C",
            text_color="#FFFFFF",
            height=42,
            corner_radius=10,
            command=self.delete_account
        ).pack(fill="x", padx=5, pady=(0, 10))
        
        ctk.CTkButton(
            self.scroll_frame,
            text="⬅️ Back to Dashboard",
            fg_color="#64748B",
            hover_color="#475569",
            text_color="#FFFFFF",
            height=42,
            corner_radius=10,
            command=self.go_back
        ).pack(fill="x", padx=5)

    def create_input(self, parent, placeholder):
        entry = ctk.CTkEntry(
            parent, 
            placeholder_text=placeholder,
            height=40,
            fg_color="#FFFFFF",
            border_color="#CBD5E1",
            text_color="#1E293B"
        )
        entry.pack(fill="x", padx=20, pady=6)
        return entry

    def create_password_field(self, parent, placeholder):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=6)

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

        ctk.CTkButton(
            frame, 
            text="👁", 
            width=40, 
            height=40,
            fg_color="#E2E8F0",
            hover_color="#CBD5E1",
            text_color="#1E293B",
            corner_radius=6,
            command=lambda: self.toggle_pass(entry)
        ).pack(side="right", padx=5)
        return entry

    def toggle_pass(self, entry):
        entry.configure(show="" if entry.cget("show") == "*" else "*")

    def go_back(self):
        self.destroy()
        self.app.show_dashboard(self.app.username, self.app.role)
 
    def logout(self):
        self.app.logout()

    def load_profile(self):
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute("""
                SELECT full_name, email, contact, address, last_login
                FROM users
                WHERE username=%s
            """, (self.app.username,))

            data = cur.fetchone()
            if data:
                if data.get("full_name"): self.fullname.insert(0, data["full_name"])
                if data.get("email"): self.email.insert(0, data["email"])
                if data.get("contact"): self.contact.insert(0, data["contact"])
                if data.get("address"): self.address.insert(0, data["address"])

                last_login = data.get("last_login")
                if last_login:
                    self.activity_label.configure(text=f"Last login: {last_login}")
                else:
                    self.activity_label.configure(text="Last login: First time login")

        finally:
            cur.close()
            conn.close()

    def save_profile(self):
        email = self.email.get().strip()
        if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messagebox.showerror("Error", "Invalid Email Format")
            return

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE users
                SET full_name=%s, email=%s, contact=%s, address=%s
                WHERE username=%s
            """, (
                self.fullname.get(), 
                email, 
                self.contact.get(), 
                self.address.get(), 
                self.app.username
            ))
            conn.commit()
            messagebox.showinfo("Success", "✅ Profile updated successfully!")
        finally:
            cur.close()
            conn.close()

    def change_password(self):
        old = self.old_pass.get().strip()
        new = self.new_pass.get().strip()
        confirm = self.confirm_pass.get().strip()

        if not old or not new or not confirm:
            messagebox.showwarning("Missing Fields", "Please fill in all password fields")
            return
        if new != confirm:
            messagebox.showerror("Error", "New passwords do not match")
            return
        if len(new) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters long")
            return

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute("SELECT password FROM users WHERE username=%s", (self.app.username,))
            user = cur.fetchone()
            
            old_hash = hashlib.sha256(old.encode()).hexdigest()
            if user["password"] != old_hash:
                messagebox.showerror("Error", "Old password is incorrect")
                return

            new_hash = hashlib.sha256(new.encode()).hexdigest()
            cur.execute("UPDATE users SET password=%s WHERE username=%s", (new_hash, self.app.username))
            conn.commit()
            messagebox.showinfo("Success", "✅ Password updated successfully!")
            
            # Clear fields
            for entry in [self.old_pass, self.new_pass, self.confirm_pass]:
                entry.delete(0, 'end')
        finally:
            cur.close()
            conn.close()

    def delete_account(self):
        if messagebox.askyesno(
            "Confirm Deletion", 
            "⚠️ Are you sure you want to delete your account?\nThis action cannot be undone!"
        ):
            conn = get_db_connection()
            cur = conn.cursor()
            try:
                cur.execute("DELETE FROM users WHERE username=%s", (self.app.username,))
                conn.commit()
                messagebox.showinfo("Account Deleted", "Your account has been removed successfully.")
                self.app.logout()
            finally:
                cur.close()
                conn.close()