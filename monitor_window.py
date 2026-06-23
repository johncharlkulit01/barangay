import customtkinter as ctk
from tkinter import messagebox
from db_config import get_db_connection


class DetailsView(ctk.CTkToplevel):
    def __init__(self, master, data):
        super().__init__(master)
        self.title("Appointment Details")
        self.geometry("420x480")
        self.resizable(False, False)
        self.configure(fg_color="#F8FAFC")  # Light background
        self.grab_set()
        self.transient(master)

        ctk.CTkLabel(
            self, 
            text="📋 Queue Details", 
            font=("Segoe UI", 20, "bold"),
            text_color="#1E293B"  # Dark text
        ).pack(pady=20)

        # Details card
        card = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=12, border_width=1, border_color="#E2E8F0")
        card.pack(fill="both", expand=True, padx=20, pady=10)

        fields = ["Fullname", "Document_type", "Contact", "Age", "Status"]
        for field in fields:
            val = data.get(field.lower(), "N/A")
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=8)
            
            ctk.CTkLabel(
                row, 
                text=f"{field}:", 
                font=("Segoe UI", 12, "bold"),
                text_color="#334155"
            ).pack(side="left")
            
            ctk.CTkLabel(
                row, 
                text=str(val), 
                font=("Segoe UI", 12),
                text_color="#1E293B"
            ).pack(side="right")

        ctk.CTkButton(
            self, 
            text="Close", 
            command=self.destroy,
            fg_color="#DC2626",
            hover_color="#B91C1C",
            text_color="#FFFFFF",
            corner_radius=8,
            height=36
        ).pack(pady=20)


class MonitorDashboard(ctk.CTkFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="#F8FAFC")  # Main light background
        self.app = app_controller
        self.running = True
        self.last_data_count = -1
        self.seen_appointments = {}

        self.pack(fill="both", expand=True, padx=15, pady=15)

        # --- Header ---
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(10, 20))

        ctk.CTkLabel(
            header,
            text="🔴 LIVE QUEUE MONITOR",
            font=("Segoe UI", 28, "bold"),
            text_color="#1E293B"
        ).pack(side="left")

        self.search_entry = ctk.CTkEntry(
            header, 
            placeholder_text="🔍 Search by name...", 
            width=220,
            height=40,
            fg_color="#FFFFFF",
            border_color="#CBD5E1",
            text_color="#1E293B"
        )
        self.search_entry.pack(side="right", padx=10)
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_queue())

        # --- Scrollable Queue List ---
        self.scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="#F1F5F9",  # Soft gray background
            corner_radius=15
        )
        self.scroll.pack(fill="both", expand=True)

        self.load_queue()
        self.auto_refresh()

    def delete_appointment(self, appointment_id):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this queue item?"):
            conn = None
            try:
                conn = get_db_connection()
                if conn:
                    cur = conn.cursor()
                    cur.execute("DELETE FROM appointments WHERE id = %s", (appointment_id,))
                    conn.commit()
                    cur.close()

                self.last_data_count = -1
                self.load_queue()

            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete: {e}")
            finally:
                if conn:
                    conn.close()

    def open_details(self, appointment_id):
        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM appointments WHERE id = %s", (appointment_id,))
            data = cur.fetchone()
            cur.close()
            
            if data:
                DetailsView(self, data)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load details: {e}")
        finally:
            if conn: 
                conn.close()

    def load_queue(self):
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return

            cur = conn.cursor(dictionary=True)
            search_query = self.search_entry.get().strip()

            if search_query:
                sql = """
                    SELECT * FROM appointments
                    WHERE fullname LIKE %s
                    AND status IN ('Pending', 'Approved', 'Rejected')
                    ORDER BY FIELD(status,'Pending','Approved','Rejected'), id DESC
                """
                cur.execute(sql, (f"%{search_query}%",))
            else:
                sql = """
                    SELECT * FROM appointments
                    WHERE status IN ('Pending', 'Approved', 'Rejected')
                    ORDER BY FIELD(status,'Pending','Approved','Rejected'), id DESC
                """
                cur.execute(sql)

            rows = cur.fetchall()
            cur.close()

            # Skip refresh if no changes
            if len(rows) == self.last_data_count and not search_query:
                return
            self.last_data_count = len(rows)

            # Clear old content
            for w in self.scroll.winfo_children():
                w.destroy()

            # Empty state
            if not rows:
                empty_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
                empty_frame.pack(pady=70)

                ctk.CTkLabel(empty_frame, text="📭", font=("Segoe UI", 70)).pack()
                ctk.CTkLabel(
                    empty_frame, 
                    text="No pending appointments", 
                    font=("Segoe UI", 18, "bold"), 
                    text_color="#64748B"
                ).pack(pady=10)
                ctk.CTkLabel(
                    empty_frame, 
                    text="Queue is clear", 
                    font=("Segoe UI", 13), 
                    text_color="#94A3B8"
                ).pack()
                return

            # Create queue cards with alternating light colors
            for i, row in enumerate(rows, 1):
                status = (row.get("status") or "Pending").upper()
                # Status colors
                if status == "PENDING":
                    status_color = "#F59E0B"
                elif status == "APPROVED":
                    status_color = "#16A34A"
                elif status == "REJECTED":
                    status_color = "#DC2626"
                else:
                    status_color = "#6B7280"

                # Alternating card background
                card_bg = "#FFFFFF" if i % 2 == 0 else "#E2E8F0"

                # Card container
                card = ctk.CTkFrame(
                    self.scroll, 
                    fg_color=card_bg, 
                    corner_radius=12, 
                    height=100,  # Increased height a bit to fit bigger badge
                    border_width=1,
                    border_color="#CBD5E1"
                )
                card.pack(fill="x", pady=8, padx=10)
                card.pack_propagate(False)

                # Top row: Number + Name + Actions
                top = ctk.CTkFrame(card, fg_color="transparent")
                top.pack(fill="x", padx=15, pady=(12, 5))

                ctk.CTkLabel(
                    top,
                    text=f"#{i} • {row.get('fullname', 'Unknown')}",
                    font=("Segoe UI", 16, "bold"),
                    text_color="#1E293B"
                ).pack(side="left")

                ctk.CTkButton(
                    top,
                    text="Delete",
                    fg_color="#DC2626",
                    hover_color="#B91C1C",
                    text_color="#FFFFFF",
                    width=70,
                    height=30,
                    corner_radius=6,
                    font=("Segoe UI", 11),
                    command=lambda id=row['id']: self.delete_appointment(id)
                ).pack(side="right", padx=3)

                ctk.CTkButton(
                    top,
                    text="View",
                    fg_color="#2563EB",
                    hover_color="#1D4ED8",
                    text_color="#FFFFFF",
                    width=70,
                    height=30,
                    corner_radius=6,
                    font=("Segoe UI", 11),
                    command=lambda id=row['id']: self.open_details(id)
                ).pack(side="right", padx=3)

                # Bottom row: Document Type
                bottom = ctk.CTkFrame(card, fg_color="transparent")
                bottom.pack(fill="x", padx=15)

                ctk.CTkLabel(
                    bottom,
                    text=row.get("document_type", "N/A"),
                    font=("Segoe UI", 13),
                    text_color="#475569"
                ).pack(side="left")

                # ✅ BIGGER & MORE VISIBLE STATUS BADGE
                status_badge = ctk.CTkLabel(
                    card,
                    text=status,
                    fg_color=status_color,
                    text_color="#FFFFFF",
                    corner_radius=10,
                    font=("Segoe UI", 13, "bold"),  # Larger font
                    width=130,   # Wider
                    height=36    # Taller
                )
                status_badge.pack(side="right", padx=15, pady=(0, 12))

                # Notification for status changes
                app_id = row.get('id')
                current_status = status 

                if app_id not in self.seen_appointments or self.seen_appointments[app_id] != current_status:
                    self.seen_appointments[app_id] = current_status
                    if self.last_data_count != -1:
                        try:
                            self.app.push_notification(
                                f"Queue Update: {row.get('fullname')} is now {current_status}", 
                                "info"
                            )
                        except:
                            pass

        except Exception as e:
            print("Queue Load Error:", e)
        finally:
            if conn:
                conn.close()

    def auto_refresh(self):
        if self.running and self.winfo_exists():
            self.load_queue()
            self.after(3000, self.auto_refresh)