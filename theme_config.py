# theme_config.py
import customtkinter as ctk

def get_color(name):
    mode = ctk.get_appearance_mode()

    colors = {
        "bg_main": ("#F8FAFC", "#121212"),
        "bg_card": ("#FFFFFF", "#1E293B"),
        "bg_secondary": ("#E2E8F0", "#27374D"),
        "border": ("#CBD5E1", "#475569"),
        "text_primary": ("#0F172A", "#F8FAFC"),
        "text_secondary": ("#334155", "#CBD5E1"),
        "text_muted": ("#64748B", "#94A3B8"),
        "primary": ("#2563EB", "#3B82F6"),
        "primary_hover": ("#1D4ED8", "#2563EB"),
        "success": ("#16A34A", "#16A34A"),
        "success_hover": ("#15803D", "#15803D"),
        "warning": ("#F59E0B", "#F59E0B"),
        "danger": ("#DC2626", "#DC2626"),
        "danger_hover": ("#B91C1C", "#991B1B")
    }

    return colors[name][0] if mode == "Light" else colors[name][1]

def toggle_theme():
    current = ctk.get_appearance_mode()
    if current == "Dark":
        ctk.set_appearance_mode("Light")
    else:
        ctk.set_appearance_mode("Dark")