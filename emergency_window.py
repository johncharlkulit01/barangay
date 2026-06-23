import customtkinter as ctk
from tkinter import messagebox
from db_config import get_db_connection


class SafetyGuideModal(ctk.CTkToplevel):
    def __init__(self, master, category, content):
        super().__init__(master)
        self.title(f"Safety Guide: {category}")
        self.geometry("420x520")
        self.resizable(False, False)
        self.configure(fg_color="#FFFFFF")  # Light background

        self.transient(master)
        self.grab_set()

        ctk.CTkLabel(
            self,
            text=category,
            font=("Segoe UI", 20, "bold"),
            text_color="#1E293B"
        ).pack(pady=20)

        textbox = ctk.CTkTextbox(
            self,
            width=350,
            height=350,
            fg_color="#F8FAFC",
            text_color="#1E293B",
            border_color="#CBD5E1",
            corner_radius=8
        )
        textbox.pack(pady=10, padx=20)
        textbox.insert("0.0", content)
        textbox.configure(state="disabled")

        ctk.CTkButton(
            self,
            text="Close",
            command=self.destroy,
            fg_color="#EF4444",
            hover_color="#DC2626",
            corner_radius=8,
            height=36
        ).pack(pady=10)


class EmergencyDashboard(ctk.CTkFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="#F8FAFC")  # ✅ Light main background
        self.app = app_controller
        self.selected_id = None
        self.selected_frame = None
        self._refresh_job = None

        self.pack(fill="both", expand=True, padx=15, pady=15)

        # Scrollable container
        self.scroll_container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        self.scroll_container.pack(fill="both", expand=True)

        # Header
        ctk.CTkLabel(
            self.scroll_container,
            text="🚨 EMERGENCY & DISASTER SYSTEM",
            font=("Segoe UI", 28, "bold"),
            text_color="#EF4444"
        ).pack(anchor="w", pady=(10, 20))

        # --- Report Emergency Section ---
        self.report_frame = ctk.CTkFrame(
            self.scroll_container,
            fg_color="#FFFFFF",
            corner_radius=15
        )
        self.report_frame.pack(fill="x", pady=10, padx=5)

        ctk.CTkLabel(
            self.report_frame,
            text="📝 Report Emergency",
            font=("Segoe UI", 18, "bold"),
            text_color="#1E293B"
        ).pack(anchor="w", padx=15, pady=10)

        self.category = ctk.CTkComboBox(
        self.report_frame,
        values=["Fire", "Medical", "Crime", "Disaster", "Other"],
        fg_color="#F1F5F9",
        border_color="#CBD5E1",
        button_color="#E2E8F0",
        button_hover_color="#CBD5E1",
        text_color="#1E293B",
        height=40
        )
        self.category.set("Select Category")
        self.category.pack(fill="x", padx=15, pady=5)

        # ✅ Bagong linya: Magbubukas ang listahan kahit saan pindutin
        self.category.bind("<Button-1>", lambda e: self.category._clicked())

        self.location = ctk.CTkEntry(
            self.report_frame,
            placeholder_text="📍 Exact location",
            fg_color="#FFFFFF",
            border_color="#CBD5E1",
            text_color="#1E293B",
            height=40
        )
        self.location.pack(fill="x", padx=15, pady=5)

        self.contact_entry = ctk.CTkEntry(
            self.report_frame,
            placeholder_text="📞 Contact number (11 digits)",
            fg_color="#FFFFFF",
            border_color="#CBD5E1",
            text_color="#1E293B",
            height=40
        )
        self.contact_entry.pack(fill="x", padx=15, pady=5)

        self.send_btn = ctk.CTkButton(
            self.report_frame,
            text="🚨 SEND EMERGENCY REPORT",
            fg_color="#EF4444",
            hover_color="#DC2626",
            font=("Segoe UI", 14, "bold"),
            height=42,
            corner_radius=8,
            command=self.send_emergency
        )
        self.send_btn.pack(fill="x", padx=15, pady=15)

        # --- Admin Controls ---
        if self.app.role == "admin":
            self.admin_frame = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
            self.admin_frame.pack(fill="x", pady=10)

            ctk.CTkLabel(
                self.admin_frame,
                text="⚙️ Update Status:",
                font=("Segoe UI", 14, "bold"),
                text_color="#1E293B"
            ).pack(side="left", padx=(0, 10))

            ctk.CTkButton(
                self.admin_frame,
                text="Responding",
                fg_color="#F59E0B",
                hover_color="#D97706",
                text_color="#FFFFFF",
                corner_radius=8,
                command=lambda: self.update_status("Responding")
            ).pack(side="left", padx=5)

            ctk.CTkButton(
                self.admin_frame,
                text="Resolved",
                fg_color="#16A34A",
                hover_color="#15803D",
                text_color="#FFFFFF",
                corner_radius=8,
                command=lambda: self.update_status("Resolved")
            ).pack(side="left", padx=5)

            ctk.CTkButton(
                self.admin_frame,
                text="Pending",
                fg_color="#94A3B8",
                hover_color="#64748B",
                text_color="#FFFFFF",
                corner_radius=8,
                command=lambda: self.update_status("Pending")
            ).pack(side="left", padx=5)

            ctk.CTkButton(
                self.admin_frame,
                text="Completed",
                fg_color="#2563EB",
                hover_color="#1D4ED8",
                text_color="#FFFFFF",
                corner_radius=8,
                command=lambda: self.update_status("Completed")
            ).pack(side="left", padx=5)

        # --- Emergency Reports List ---
        self.tree = ctk.CTkFrame(
            self.scroll_container,
            fg_color="#FFFFFF",
            corner_radius=15
        )
        self.tree.pack(fill="both", expand=True, pady=10, padx=5)

        ctk.CTkLabel(
            self.tree,
            text="📋 List of Emergency Reports",
            font=("Segoe UI", 16, "bold"),
            text_color="#1E293B"
        ).pack(anchor="w", padx=15, pady=10)

        # --- Safety Guides ---
        self.create_guide_menu()

        # --- Information Cards ---
        self.create_card(
            "☎️ Emergency Hotlines",
            ["Barangay Hotline: 0912-345-6789",
             "Emergency Desk: 888-0000",
             "National Emergency: 911",
             "Fire Department: 160",
             "Police Assistance: 117"],
            "#FFFFFF", "#F59E0B"
        )

        self.create_card(
            "🏠 Evacuation Centers",
            ["Barangay Covered Court",
             "Barangay Hall",
             "Public School Gym",
             "High School Grounds"],
            "#FFFFFF", "#16A34A"
        )

        self.create_card(
            "🎒 Emergency Kit Checklist",
            ["Water & canned food",
             "Flashlight & batteries",
             "First aid kit",
             "Important documents",
             "Power bank & light",
             "Extra clothes & blanket"],
            "#FFFFFF", "#2563EB"
        )

        # Load data and start auto-refresh
        self.load_data()
        self.auto_refresh()

    def load_data(self):
        conn = get_db_connection()
        if not conn:
            return

        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT id, username, category, location, status, created_at
                FROM emergency_reports
                WHERE status != 'Completed'
                ORDER BY id DESC
            """)
            rows = cur.fetchall()

            # Clear old content
            for w in self.tree.winfo_children():
                if not isinstance(w, ctk.CTkLabel) or w.cget("text") != "📋 List of Emergency Reports":
                    w.destroy()

            if not rows:
                ctk.CTkLabel(
                    self.tree,
                    text="✅ No active emergency reports at this time.",
                    text_color="#64748B",
                    font=("Segoe UI", 14)
                ).pack(pady=40)
                return

            # Render each report
            for r in rows:
                frame = ctk.CTkFrame(self.tree, fg_color="#F8FAFC", corner_radius=10)
                frame.pack(fill="x", padx=12, pady=6)
                frame.bind("<Button-1>", lambda e, rid=r["id"], f=frame: self.select_row(rid, f))
                frame.configure(cursor="hand2")

                # Top row info
                top_row = ctk.CTkFrame(frame, fg_color="transparent")
                top_row.pack(fill="x", padx=12, pady=8)

                status_color = self.get_status_color(r['status'])
                ctk.CTkLabel(
                    top_row,
                    text=f"● {r['status']}",
                    text_color=status_color,
                    font=("Segoe UI", 12, "bold")
                ).pack(side="right")

                ctk.CTkLabel(
                    top_row,
                    text=f"🚨 {r['category']}",
                    font=("Segoe UI", 14, "bold"),
                    text_color="#1E293B"
                ).pack(side="left")

                ctk.CTkLabel(
                    top_row,
                    text=f"👤 {r['username']}",
                    text_color="#475569",
                    font=("Segoe UI", 12)
                ).pack(side="left", padx=10)

                ctk.CTkLabel(
                    top_row,
                    text=f"📍 {r['location']}",
                    text_color="#64748B",
                    font=("Segoe UI", 12)
                ).pack(side="right")

                # Timestamp
                ctk.CTkLabel(
                    frame,
                    text=f"🕒 Reported: {r['created_at']}",
                    text_color="#94A3B8",
                    font=("Segoe UI", 10)
                ).pack(anchor="w", padx=12, pady=(0, 8))

        finally:
            cur.close()
            conn.close()

    def select_row(self, rid, frame):
        # Reset all frames
        for child in self.tree.winfo_children():
            if isinstance(child, ctk.CTkFrame):
                child.configure(fg_color="#F8FAFC")

        self.selected_id = rid
        self.selected_frame = frame
        if self.selected_frame.winfo_exists():
            self.selected_frame.configure(fg_color="#DBEAFE")  # Light highlight

    def send_emergency(self):
        category = self.category.get()
        location = self.location.get().strip()
        contact = self.contact_entry.get().strip()

        # Validation
        if category == "Select Category":
            messagebox.showwarning("Incomplete", "Please select an emergency category.")
            return
        if not location or len(location) < 5:
            messagebox.showwarning("Incomplete", "Please enter a valid location.")
            return
        if not contact.isdigit() or len(contact) != 11:
            messagebox.showwarning("Error", "Contact number must be exactly 11 digits.")
            return

        conn = get_db_connection()
        if not conn:
            messagebox.showerror("Error", "Database connection failed.")
            return

        try:
            cur = conn.cursor()
            sql = """
                INSERT INTO emergency_reports (username, category, location, contact, status)
                VALUES (%s, %s, %s, %s, 'Pending')
            """
            cur.execute(sql, (self.app.username, category, location, contact))
            conn.commit()

            messagebox.showinfo("Success", f"✅ {category} report submitted successfully!")

            # Reset fields
            self.category.set("Select Category")
            self.location.delete(0, "end")
            self.contact_entry.delete(0, "end")

            self.load_data()

        except Exception as e:
            messagebox.showerror("Database Error", f"Failed: {e}")
        finally:
            cur.close()
            conn.close()

    def update_status(self, new_status):
        if not self.selected_id:
            messagebox.showwarning("Warning", "Select a report first!")
            return

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE emergency_reports SET status=%s WHERE id=%s", (new_status, self.selected_id))
        conn.commit()
        cur.close()
        conn.close()

        self.load_data()

    def auto_refresh(self):
        self.load_data()
        if self._refresh_job:
            self.after_cancel(self._refresh_job)
        self._refresh_job = self.after(10000, self.auto_refresh)

    def get_status_color(self, status):
        colors = {
            "Pending": "#94A3B8",
            "Responding": "#F59E0B",
            "Resolved": "#64748B",
            "Completed": "#16A34A"
        }
        return colors.get(status, "#1E293B")

    def create_card(self, title, items, bg, color):
        card = ctk.CTkFrame(self.scroll_container, fg_color=bg, corner_radius=15)
        card.pack(fill="x", pady=10, padx=5)

        ctk.CTkLabel(
            card,
            text=title,
            font=("Segoe UI", 18, "bold"),
            text_color=color
        ).pack(anchor="w", padx=15, pady=10)

        ctk.CTkLabel(
            card,
            text="\n".join([f"• {i}" for i in items]),
            text_color="#334155",
            justify="left",
            font=("Segoe UI", 12)
        ).pack(anchor="w", padx=15, pady=(0, 15))

    def create_guide_menu(self):
        guide_frame = ctk.CTkFrame(
            self.scroll_container,
            fg_color="#FFFFFF",
            corner_radius=15
        )
        guide_frame.pack(fill="x", pady=10, padx=5)

        ctk.CTkLabel(
            guide_frame,
            text="📚 Safety Guides & Procedures",
            font=("Segoe UI", 18, "bold"),
            text_color="#2563EB"
        ).pack(anchor="w", padx=15, pady=10)

        button_frame = ctk.CTkFrame(guide_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=5, padx=15)

        guides = {
            "🔥 Fire": "✅ WHAT TO DO:\n\n1. Stay low under smoke.\n2. Cover nose/mouth with wet cloth.\n3. Do NOT use elevators.\n4. Check doors for heat before opening.\n5. Call Fire Dept: 160 or 911.\n6. Evacuate calmly to assembly area.",
            "🌀 Typhoon": "✅ WHAT TO DO:\n\n1. Secure windows and roof.\n2. Charge phones and lights.\n3. Store water and food.\n4. Listen to news updates.\n5. Stay indoors. Do not go out.\n6. Evacuate if ordered by officials.",
            "🌊 Flood": "✅ WHAT TO DO:\n\n1. Move to higher ground immediately.\n2. Turn off main power switch.\n3. Do NOT walk/swim in floodwater.\n4. Avoid electric posts/wires.\n5. Bring emergency kit with you.\n6. Wait for rescue if trapped.",
            "🏥 Medical": "✅ WHAT TO DO:\n\n1. Check if safe to approach.\n2. Do not move injured person unless danger.\n3. Call emergency: 911.\n4. Apply first aid if trained.\n5. Loosen tight clothing.\n6. Keep person calm and warm."
        }

        for cat, text in guides.items():
            ctk.CTkButton(
                button_frame,
                text=cat,
                width=110,
                fg_color="#2563EB",
                hover_color="#1D4ED8",
                text_color="#FFFFFF",
                corner_radius=8,
                command=lambda c=cat, t=text: SafetyGuideModal(self, c, t)
            ).pack(side="left", padx=5, pady=5)