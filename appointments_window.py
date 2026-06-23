import customtkinter as ctk
from tkinter import messagebox
from db_config import get_db_connection
from db_utils import add_history


class AppointmentsDashboard(ctk.CTkFrame):

    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="#F8FAFC")  # ✅ Light main background
        self.pack(fill="both", expand=True, padx=15, pady=15)

        self.app = app_controller

        # --- Header Section ---
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(10, 20))

        ctk.CTkLabel(
            header,
            text="📋 APPOINTMENTS MANAGEMENT",
            font=("Segoe UI", 24, "bold"),
            text_color="#1E293B"  # ✅ Dark text for light background
        ).pack(side="left")

        ctk.CTkButton(
            header,
            text="🔄 Refresh",
            command=self.load,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            height=36,
            corner_radius=8
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            header,
            text="🗑 Delete All",
            fg_color="#dc2626",
            hover_color="#b91c1c",
            command=self.delete_all_appointments,
            height=36,
            corner_radius=8
        ).pack(side="right", padx=5)

        # --- Search & Filter Section ---
        search = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=12)
        search.pack(fill="x", pady=(0, 15), padx=5)

        self.search_entry = ctk.CTkEntry(
            search, 
            placeholder_text="🔍 Search by name...",
            fg_color="#F1F5F9",
            border_color="#CBD5E1",
            text_color="#1E293B",
            height=40
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=15, pady=10)
        self.search_entry.bind("<KeyRelease>", lambda e: self.load())

        self.status_filter = ctk.CTkOptionMenu(
            search, 
            values=["All", "Pending", "Approved", "Rejected", "Cancelled"],
            command=lambda e: self.load(),
            fg_color="#F1F5F9",
            button_color="#E2E8F0",
            button_hover_color="#CBD5E1",
            text_color="#1E293B",
            height=40
        )
        self.status_filter.pack(side="left", padx=5, pady=10)

        ctk.CTkButton(
            search,
            text="Clear",
            command=self.clear,
            fg_color="#94A3B8",
            hover_color="#64748B",
            height=40,
            corner_radius=8
        ).pack(side="left", padx=(5, 15), pady=10)

        # --- Main Content Area ---
        self.frame = ctk.CTkScrollableFrame(
            self, 
            fg_color="#F1F5F9", 
            corner_radius=15
        )
        self.frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.load()

    def open_review_window(self, r):
        review_win = ctk.CTkToplevel(self)
        review_win.title(f"Review: {r.get('fullname')}")
        review_win.geometry("420x620")
        review_win.configure(fg_color="#FFFFFF")  # ✅ Light background
        review_win.attributes("-topmost", True)

        ctk.CTkLabel(
            review_win, 
            text="📋 APPOINTMENT DETAILS", 
            font=("Segoe UI", 18, "bold"),
            text_color="#1E293B"
        ).pack(pady=20)

        def add_detail(label, value):
            f = ctk.CTkFrame(review_win, fg_color="#F8FAFC", corner_radius=8)
            f.pack(fill="x", padx=25, pady=4)
            ctk.CTkLabel(
                f, 
                text=f"{label}:", 
                font=("Segoe UI", 12, "bold"),
                text_color="#1E293B"
            ).pack(side="left", padx=12, pady=10)
            ctk.CTkLabel(
                f, 
                text=str(value), 
                font=("Segoe UI", 12),
                text_color="#334155"
            ).pack(side="right", padx=12)

        add_detail("Full Name", r.get('fullname'))
        add_detail("Gender", r.get('gender', 'N/A'))
        add_detail("Document Type", r.get('document_type'))
        add_detail("Appointment Date", r.get('appointment_date'))
        add_detail("Current Status", r.get('status'))
        add_detail("Purpose", r.get('purpose', 'N/A'))

        # Action Buttons
        btn_frame = ctk.CTkFrame(review_win, fg_color="transparent")
        btn_frame.pack(side="bottom", pady=30)

        u = self.safe_username(r)

        ctk.CTkButton(
            btn_frame, 
            text="✅ Approve", 
            fg_color="#27AE60", 
            hover_color="#229954",
            width=90,
            height=36,
            corner_radius=8,
            command=lambda: [self.update(r['id'], "Approved", r['appointment_date'], u), review_win.destroy()]
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame, 
            text="❌ Reject", 
            fg_color="#E74C3C", 
            hover_color="#C0392B",
            width=90,
            height=36,
            corner_radius=8,
            command=lambda: [self.update(r['id'], "Rejected", r['appointment_date'], u), review_win.destroy()]
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame, 
            text="🗑 Delete", 
            fg_color="#95A5A6", 
            hover_color="#7F8C8D",
            width=90,
            height=36,
            corner_radius=8,
            command=lambda: [self.delete_appointment(r['id']), review_win.destroy()]
        ).pack(side="left", padx=5)

    def get_reason(self, title):
        dialog = ctk.CTkInputDialog(
            text="Please enter the reason:", 
            title=title,
            fg_color="#FFFFFF",
            entry_fg_color="#F1F5F9",
            entry_text_color="#1E293B",
            button_fg_color="#2563eb"
        )
        reason = dialog.get_input()
        return reason if reason and reason.strip() != "" else None

    def clear(self):
        self.search_entry.delete(0, "end")
        self.load()

    def safe_username(self, r):
        return r.get("fullname") or r.get("username") or self.app.username or "Unknown"

    def update(self, id, status, date, user):
        if not messagebox.askyesno("Confirm Action", f"Mark this appointment as {status}?"):
            return

        reason = None
        queue_id = None
        conn = None

        try:
            conn = get_db_connection()
            if not conn:
                return

            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM appointments WHERE id=%s", (id,))
            r = cur.fetchone()

            if not r:
                return

            if status in ["Rejected", "Cancelled"]:
                reason = self.get_reason(f"{status} Reason")
                if not reason:
                    messagebox.showwarning("Input Required", "Reason is required to proceed!")
                    return

            cur.execute(
                "UPDATE appointments SET status=%s, reason=%s WHERE id=%s",
                (status, reason, id)
            )

            if status == "Approved":
                queue_id = f"Q-{id:04d}"
                try:
                    cur.execute("""
                        INSERT INTO queue (queue_id, appointment_id, status)
                        VALUES (%s, %s, %s)
                    """, (queue_id, id, "waiting"))
                except Exception as q_err:
                    print("QUEUE INSERT ERROR:", q_err)

                try:
                    cur.execute(
                        "UPDATE appointments SET queue_id=%s WHERE id=%s",
                        (queue_id, id)
                    )
                except Exception as e:
                    print("QUEUE ID UPDATE ERROR:", e)

            conn.commit()

            add_history(
                self.safe_username(r),
                r.get("document_type"),
                r.get("purpose"),
                status,
                r.get("appointment_date"),
                queue_id if queue_id else "N/A"
            )

            self.load()

        except Exception as e:
            messagebox.showerror("Error", f"Update Failed: {e}")
        finally:
            if conn:
                conn.close()

    def delete_appointment(self, appointment_id):
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this appointment?"):
            return

        conn = get_db_connection()
        if not conn:
            return

        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM queue WHERE appointment_id=%s", (appointment_id,))
            cur.execute("DELETE FROM appointments WHERE id=%s", (appointment_id,))
            conn.commit()
            messagebox.showinfo("Success", "Appointment deleted successfully!")
            self.load()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            if conn:
                conn.close()

    def delete_all_appointments(self):
        if not messagebox.askyesno("WARNING", "This will delete ALL appointments and cannot be undone! Proceed?"):
            return

        conn = get_db_connection()
        if not conn:
            return

        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM queue")
            cur.execute("DELETE FROM appointments")
            conn.commit()
            messagebox.showinfo("Success", "All appointments have been deleted!")
            self.load()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            if conn:
                conn.close()

    def load(self):
        for w in self.frame.winfo_children():
            w.destroy()

        conn = get_db_connection()
        if not conn:
            return

        rows = []
        try:
            cur = conn.cursor(dictionary=True)
            query = "SELECT * FROM appointments WHERE 1=1 "
            params = []
            if self.search_entry.get().strip():
                query += "AND fullname LIKE %s "
                params.append(f"%{self.search_entry.get().strip()}%")
            if self.status_filter.get() != "All":
                query += "AND status = %s "
                params.append(self.status_filter.get())
            query += "ORDER BY id DESC"
            cur.execute(query, tuple(params))
            rows = cur.fetchall()
        finally:
            if conn:
                conn.close()

        for r in rows:
            # Appointment Card
            card = ctk.CTkFrame(self.frame, fg_color="#FFFFFF", corner_radius=12)
            card.pack(fill="x", pady=8, padx=8)

            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True, padx=15, pady=15)

            # Info Labels
            labels = [
                ctk.CTkLabel(info_frame, text=f"👤 {r.get('fullname', 'Unknown')}", font=("Segoe UI", 14, "bold"), text_color="#1E293B"),
                ctk.CTkLabel(info_frame, text=f"📄 {r.get('document_type')}", text_color="#334155"),
                ctk.CTkLabel(info_frame, text=f"⚤ Gender: {r.get('gender', 'N/A')}", text_color="#64748B"),
                ctk.CTkLabel(info_frame, text=f"📅 {r.get('appointment_date')}", text_color="#64748B")
            ]
            for w in labels:
                w.pack(anchor="w")

            # Status Label with color coding
            status_val = r.get('status', 'Pending')
            if status_val == "Approved":
                color = "#27AE60"
            elif status_val == "Rejected":
                color = "#E74C3C"
            elif status_val == "Pending":
                color = "#F39C12"
            elif status_val == "Cancelled":
                color = "#95A5A6"
            else:
                color = "#64748B"

            ctk.CTkLabel(
                info_frame, 
                text=f"📌 Status: {status_val}", 
                font=("Segoe UI", 12, "bold"),
                text_color=color
            ).pack(anchor="w", pady=(5, 0))

            # View Button
            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(side="right", padx=15)

            ctk.CTkButton(
                btn_frame, 
                text="View Details", 
                width=110,
                height=38,
                fg_color="#3498DB",
                hover_color="#2980B9",
                corner_radius=8,
                command=lambda data=r: self.open_review_window(data)
            ).pack(pady=10)