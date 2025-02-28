import customtkinter
from customtkinter import *
from PIL import Image
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime
from tkinter import messagebox


# Add this function to create initial admin account
def create_initial_admin():
    try:
        admin_id = "admin123"  # Default admin ID
        admin_data = {
            'admin_id': admin_id,
            'password': "admin123",  # Default password
            'full_name': "System Administrator",
            'role': "admin",
            'created_at': datetime.now(),
            'last_login': datetime.now()
        }

        # Check if admin already exists
        admin_doc = db.collection('admins').document(admin_id).get()
        if not admin_doc.exists:
            db.collection('admins').document(admin_id).set(admin_data)
            print("Initial admin account created successfully!")
            print("Admin ID: admin123")
            print("Password: admin123")
        else:
            print("Admin account already exists")

    except Exception as e:
        print(f"Error creating admin account: {str(e)}")


# Add this function to the admin dashboard to manage admins
def show_admin_management(current_admin_id=None, current_admin_name=None):
    if hasattr(app, 'current_frame'):
        app.current_frame.destroy()

    admin_mgmt_frame = CTkFrame(
        app,
        width=550,
        height=620,
        corner_radius=20,
        fg_color="#1a1a1a",
        border_width=2,
        border_color="#ffffff"
    )
    admin_mgmt_frame.place(relx=0.5, rely=0.5, anchor=CENTER)
    app.current_frame = admin_mgmt_frame

    # Title
    CTkLabel(
        admin_mgmt_frame,
        text="Admin Management",
        font=("Inter", 24, "bold"),
        text_color="white"
    ).place(relx=0.5, rely=0.05, anchor=CENTER)

    # Create Admin section
    create_frame = CTkFrame(admin_mgmt_frame, fg_color="#242424", width=420, height=120)
    create_frame.place(relx=0.5, rely=0.28, anchor=CENTER)

    CTkLabel(
        create_frame,
        text="Create New Admin",
        font=("Inter", 14, "bold"),
        text_color="white"
    ).pack(pady=2)

    CTkLabel(create_frame, text="Admin ID:", font=("Inter", 11)).pack(pady=(1, 0))
    admin_id_entry = CTkEntry(create_frame, width=120, height=25)
    admin_id_entry.pack()

    CTkLabel(create_frame, text="Full Name:", font=("Inter", 11)).pack(pady=(1, 0))
    name_entry = CTkEntry(create_frame, width=120, height=25)
    name_entry.pack()

    CTkLabel(create_frame, text="Password:", font=("Inter", 11)).pack(pady=(1, 0))
    password_entry = CTkEntry(create_frame, width=120, height=25, show="*")
    password_entry.pack()

    def create_admin():
        admin_id = admin_id_entry.get()
        full_name = name_entry.get()
        password = password_entry.get()

        if not all([admin_id, full_name, password]):
            show_message("Error", "Please fill in all fields")
            return

        try:
            admin_data = {
                'admin_id': admin_id,
                'password': password,
                'full_name': full_name,
                'role': "admin",
                'created_at': datetime.now(),
                'last_login': datetime.now()
            }

            db.collection('admins').document(admin_id).set(admin_data)
            show_message("Success", "Admin account created successfully!")
            load_admin_list()

            # Clear entries
            admin_id_entry.delete(0, 'end')
            name_entry.delete(0, 'end')
            password_entry.delete(0, 'end')

        except Exception as e:
            show_message("Error", f"Failed to create admin: {str(e)}")

    CTkButton(
        create_frame,
        text="Create Admin",
        command=create_admin,
        fg_color="#1a5276",
        hover_color="#2980b9",
        width=80,
        height=25
    ).pack(pady=5)

    # Admin List section
    list_frame = CTkFrame(admin_mgmt_frame, fg_color="#242424", width=520, height=10)
    list_frame.place(relx=0.5, rely=0.7, anchor=CENTER)

    CTkLabel(
        list_frame,
        text="Admin List",
        font=("Inter", 12, "bold"),
        text_color="white"
    ).pack(pady=1)

    # Create scrollable frame for admin list
    admin_list_frame = CTkScrollableFrame(list_frame, width=470, height=200)
    admin_list_frame.pack(pady=10)

    def delete_admin(admin_id_to_delete):
        try:
            # Check if trying to delete the last admin
            admins = db.collection('admins').get()
            if len(list(admins)) <= 1:
                show_message("Error", "Cannot delete the last admin account")
                return

            # Check if trying to delete current admin
            if admin_id_to_delete == current_admin_id:
                show_message("Error", "Cannot delete your own account while logged in")
                return

            # Delete the admin document
            db.collection('admins').document(admin_id_to_delete).delete()
            show_message("Success", "Admin deleted successfully")

            # Refresh the admin list
            load_admin_list()
        except Exception as e:
            show_message("Error", f"Failed to delete admin: {str(e)}")

    def load_admin_list():
        # Clear existing list
        for widget in admin_list_frame.winfo_children():
            widget.destroy()

        # Headers
        headers_frame = CTkFrame(admin_list_frame, fg_color="transparent")
        headers_frame.pack(fill="x", padx=5, pady=5)

        CTkLabel(headers_frame, text="Admin ID", font=("Inter", 11, "bold"), width=80).pack(side="left", padx=5)
        CTkLabel(headers_frame, text="Admin Name", font=("Inter", 11, "bold"), width=120).pack(side="left", padx=5)
        CTkLabel(headers_frame, text="Last Login", font=("Inter", 11, "bold"), width=120).pack(side="left", padx=5)

        try:
            admins = db.collection('admins').get()

            for admin in admins:
                data = admin.to_dict()

                # Create frame for each admin
                admin_frame = CTkFrame(admin_list_frame, fg_color="transparent")
                admin_frame.pack(fill="x", padx=5, pady=2)

                CTkLabel(admin_frame, text=data['admin_id'], width=80).pack(side="left", padx=5)
                CTkLabel(admin_frame, text=data['full_name'], width=120).pack(side="left", padx=5)
                last_login = data['last_login'].strftime("%Y-%m-%d %H:%M") if 'last_login' in data else "Never"
                CTkLabel(admin_frame, text=last_login, width=120).pack(side="left", padx=5)

                CTkButton(
                    admin_frame,
                    text="Delete",
                    command=lambda aid=data['admin_id']: delete_admin(aid),
                    fg_color="#dc3545",
                    hover_color="#c82333",
                    width=80,
                    height=25
                ).pack(side="right", padx=5)

        except Exception as e:
            show_message("Error", f"Failed to load admin list: {str(e)}")

    # Load initial admin list
    load_admin_list()

    # Back to Dashboard button
    CTkButton(
        admin_mgmt_frame,
        text="Back to Dashboard",
        width=150,
        height=30,
        font=("Inter", 14),
        command=lambda: show_admin_dashboard(current_admin_id, current_admin_name),
        fg_color="#444444",
        text_color="white",
        hover_color="#666666",
        corner_radius=8
    ).place(relx=0.5, rely=0.95, anchor=CENTER)


# Modify the admin dashboard to include admin management
def show_admin_dashboard(admin_id, admin_name):
    if hasattr(app, 'current_frame'):
        app.current_frame.destroy()

    admin_frame = CTkFrame(
        app,
        width=1200,
        height=650,
        fg_color="#1a1a1a"
    )
    admin_frame.place(x=0, y=0)
    app.current_frame = admin_frame

    # Header
    header_frame = CTkFrame(admin_frame, fg_color="#333333", height=60, width=1200)
    header_frame.place(x=0, y=0)

    # Title
    title_label = CTkLabel(
        header_frame,
        text="Admin Dashboard",
        font=("Inter", 22, "bold"),
        text_color="white"
    )
    title_label.place(relx=0.5, rely=0.5, anchor=CENTER)

    # Admin info
    try:
        admin_doc = db.collection('admins').document(admin_id).get()
        admin_name = admin_doc.to_dict()['full_name'] if admin_doc.exists else "Unknown Admin"
        admin_label = CTkLabel(
            header_frame,
            text=f"Admin: {admin_name}",
            font=("Inter", 14),
            text_color="white"
        )
        admin_label.place(relx=0.05, rely=0.5, anchor=W)
    except Exception:
        pass

    # Manage Admins button
    manage_admins_button = CTkButton(
        header_frame,
        text="Manage Admins",
        width=120,
        height=30,
        font=("Inter", 14),
        command=lambda: show_admin_management(admin_id, admin_name),
        fg_color="#1a5276",
        text_color="white",
        hover_color="#2980b9"
    )
    manage_admins_button.place(relx=0.85, rely=0.5, anchor=E)

    # Logout button
    logout_button = CTkButton(
        header_frame,
        text="Logout",
        width=100,
        height=30,
        font=("Inter", 14),
        command=lambda: [app.current_frame.destroy(), show_login_frame()],
        fg_color="#444444",
        text_color="white",
        hover_color="#666666"
    )
    logout_button.place(relx=0.95, rely=0.5, anchor=E)

    # Content area
    content_frame = CTkFrame(admin_frame, fg_color="#242424")
    content_frame.place(x=0, y=60, relwidth=1, relheight=1)

    # Create scrollable frame for reservations
    reservations_frame = CTkScrollableFrame(content_frame, fg_color="#242424")
    reservations_frame.pack(pady=20, padx=20, fill="both", expand=True)

    # Title for reservations
    CTkLabel(
        reservations_frame,
        text="Pending Reservations",
        font=("Inter", 24, "bold"),
        text_color="white"
    ).pack(pady=(0, 20))

    # Headers for reservations table
    headers_frame = CTkFrame(reservations_frame, fg_color="transparent")
    headers_frame.pack(fill="x", padx=10, pady=5)

    headers = ["Date", "Room", "User", "Time", "Purpose", "Status", "Actions"]
    for header in headers:
        CTkLabel(
            headers_frame,
            text=header,
            font=("Inter", 14, "bold"),
            text_color="white"
        ).pack(side="left", padx=20)

    try:
        # Get pending reservations
        reservations = db.collection('reservations').where('status', '==', 'pending').get()

        for reservation in reservations:
            data = reservation.to_dict()

            # Create frame for each reservation
            reservation_frame = CTkFrame(reservations_frame, fg_color="#333333")
            reservation_frame.pack(fill="x", padx=10, pady=5)

            # Add reservation details
            CTkLabel(reservation_frame, text=data['date']).pack(side="left", padx=20)
            CTkLabel(reservation_frame, text=data['room_name']).pack(side="left", padx=20)

            # Get user name
            user_doc = db.collection('users').document(data['user_id']).get()
            user_name = user_doc.to_dict()['full_name'] if user_doc.exists else "Unknown"
            CTkLabel(reservation_frame, text=user_name).pack(side="left", padx=20)

            time_text = f"{data['start_time']} - {data['end_time']}"
            CTkLabel(reservation_frame, text=time_text).pack(side="left", padx=20)
            CTkLabel(reservation_frame, text=data['purpose']).pack(side="left", padx=20)
            CTkLabel(reservation_frame, text=data['status'].capitalize()).pack(side="left", padx=20)

            # Action buttons
            actions_frame = CTkFrame(reservation_frame, fg_color="transparent")
            actions_frame.pack(side="right", padx=20)

            def approve_reservation(res_id=reservation.id, res_data=data):
                try:
                    # Update reservation status
                    db.collection('reservations').document(res_id).update({
                        'status': 'approved'
                    })
                    # Update room status
                    db.collection('rooms').document(res_data['room_id']).update({
                        'status': 'occupied'
                    })
                    show_message("Success", "Reservation approved!")
                    show_admin_dashboard(admin_id, admin_name)  # Refresh dashboard
                except Exception as e:
                    show_message("Error", f"Failed to approve: {str(e)}")

            def reject_reservation(res_id=reservation.id, res_data=data):
                try:
                    db.collection('reservations').document(res_id).update({
                        'status': 'rejected'
                    })
                    show_message("Success", "Reservation rejected!")
                    show_admin_dashboard(admin_id, admin_name)  # Refresh dashboard
                except Exception as e:
                    show_message("Error", f"Failed to reject: {str(e)}")

            CTkButton(
                actions_frame,
                text="Approve",
                command=lambda r=reservation.id, d=data: approve_reservation(r, d),
                fg_color="#28a745",
                hover_color="#218838",
                width=80
            ).pack(side="left", padx=5)

            CTkButton(
                actions_frame,
                text="Reject",
                command=lambda r=reservation.id, d=data: reject_reservation(r, d),
                fg_color="#dc3545",
                hover_color="#c82333",
                width=80
            ).pack(side="left", padx=5)

    except Exception as e:
        show_message("Error", f"Failed to load reservations: {str(e)}")


# Add these new functions after the existing imports
def create_admin_data(admin_id, password, full_name, role="admin"):
    return {
        'admin_id': admin_id,
        'password': password,
        'full_name': full_name,
        'role': role,
        'created_at': datetime.now(),
        'last_login': datetime.now()
    }


def show_message(title, message):
    """Utility function to show messages to the user"""
    dialog = CTkToplevel()
    dialog.title(title)
    dialog.geometry("300x150")

    CTkLabel(dialog, text=message, wraplength=250).pack(pady=20)
    CTkButton(dialog, text="OK", command=dialog.destroy).pack()

    # Make dialog modal
    dialog.transient(app)
    dialog.grab_set()
    app.wait_window(dialog)


def show_admin(admin_id, admin_name):
    if hasattr(app, 'current_frame'):
        app.current_frame.destroy()

    # Main admin frame
    admin_frame = CTkFrame(
        app,
        width=app.winfo_width(),
        height=app.winfo_height(),
        fg_color="#1a1a1a"
    )
    admin_frame.pack(fill="both", expand=True)
    admin_frame.pack_propagate(False)
    app.current_frame = admin_frame

    # Header
    header_frame = CTkFrame(admin_frame, fg_color="#333333", height=60)
    header_frame.pack(fill="x", side="top")
    header_frame.pack_propagate(False)

    # Title
    title_label = CTkLabel(
        header_frame,
        text="Admin Dashboard",
        font=("Inter", 22, "bold"),
        text_color="white"
    )
    title_label.place(relx=0.5, rely=0.5, anchor=CENTER)

    # Admin info
    admin_label = CTkLabel(
        header_frame,
        text=f"Admin: {admin_name}",
        font=("Inter", 14),
        text_color="white"
    )
    admin_label.place(relx=0.05, rely=0.5, anchor=W)

    # Manage Admins button
    manage_admins_button = CTkButton(
        header_frame,
        text="Manage Admins",
        width=120,
        height=30,
        font=("Inter", 14),
        command=show_admin_management,
        fg_color="#2b5d8c",
        hover_color="#1c4c7d"
    )
    manage_admins_button.place(relx=0.85, rely=0.5, anchor=E)

    # Logout button
    logout_button = CTkButton(
        header_frame,
        text="Logout",
        width=100,
        height=30,
        font=("Inter", 14),
        command=lambda: [admin_frame.destroy(), show_login_frame()],
        fg_color="#444444",
        hover_color="#666666"
    )
    logout_button.place(relx=0.95, rely=0.5, anchor=E)

    # Content container
    content_container = CTkFrame(admin_frame, fg_color="#1a1a1a")
    content_container.pack(fill="both", expand=True, padx=20, pady=(20, 0))

    # Create content frames
    reservations_frame = CTkFrame(content_container, fg_color="#242424")
    rooms_frame = CTkFrame(content_container, fg_color="#242424")
    users_frame = CTkFrame(content_container, fg_color="#242424")

    # Tabs frame with distinct styling
    tabs_frame = CTkFrame(content_container, fg_color="transparent", height=40)
    tabs_frame.pack(fill="x", pady=(0, 20))

    def reject_reservation(reservation_id, reservation_data):
        try:
            # Update reservation status
            db.collection('reservations').document(reservation_id).update({
                'status': 'rejected'
            })

            # Update room status back to available
            db.collection('rooms').document(reservation_data['room_id']).update({
                'status': 'available'
            })

            show_message("Success", "Reservation rejected successfully!")
            load_reservations()  # Refresh the reservations list
        except Exception as e:
            show_message("Error", f"Failed to reject reservation: {str(e)}")

    def approve_reservation(reservation_id, reservation_data):
        try:
            # Update reservation status
            db.collection('reservations').document(reservation_id).update({
                'status': 'approved'
            })

            # Update room status
            db.collection('rooms').document(str(reservation_data['room_id'])).update({
                'status': 'occupied'
            })

            show_message("Success", "Reservation approved successfully!")
            load_reservations()  # Refresh the reservations list
        except Exception as e:
            show_message("Error", f"Failed to approve reservation: {str(e)}")

    def switch_tab(tab_name):
        # Hide all content frames
        reservations_frame.pack_forget()
        rooms_frame.pack_forget()
        users_frame.pack_forget()

        # Update button colors
        for btn in tab_buttons:
            btn.configure(fg_color="#333333")
        tab_buttons[tabs.index(tab_name.capitalize())].configure(fg_color="#2b5d8c")

        # Show selected frame
        if tab_name == "reservations":
            reservations_frame.pack(fill="both", expand=True)
            load_reservations()
        elif tab_name == "rooms":
            rooms_frame.pack(fill="both", expand=True)
            load_rooms()
        elif tab_name == "users":
            users_frame.pack(fill="both", expand=True)
            load_users()

    # Create tab buttons with improved styling
    tabs = ["Reservations", "Rooms", "Users"]
    tab_buttons = []
    for i, tab in enumerate(tabs):
        btn = CTkButton(
            tabs_frame,
            text=tab,
            width=150,
            height=35,
            font=("Inter", 14),
            command=lambda t=tab.lower(): switch_tab(t),
            fg_color="#333333",
            text_color="white",
            hover_color="#2b5d8c"
        )
        btn.pack(side="left", padx=(0 if i == 0 else 20, 0))
        tab_buttons.append(btn)

    def load_reservations():
        for widget in reservations_frame.winfo_children():
            widget.destroy()

        reservations_scroll = CTkScrollableFrame(
            reservations_frame,
            fg_color="#242424"
        )
        reservations_scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # Headers with improved styling
        headers = ["Date", "Room", "User", "Time", "Email", "Status", "Actions"]
        for i, header in enumerate(headers):
            CTkLabel(
                reservations_scroll,
                text=header,
                font=("Inter", 14, "bold"),
                text_color="#ffffff"
            ).grid(row=0, column=i, padx=10, pady=5, sticky="w")

        try:
            reservations = db.collection('reservations').order_by(
                'created_at', direction=firestore.Query.DESCENDING
            ).get()

            if not reservations:
                CTkLabel(
                    reservations_scroll,
                    text="No reservations found",
                    font=("Inter", 14),
                    text_color="#888888"
                ).grid(row=1, column=0, columnspan=7, pady=20)
                return

            for idx, res in enumerate(reservations, 1):
                data = res.to_dict()

                # Create a frame for each reservation row
                row_frame = CTkFrame(reservations_scroll, fg_color="#2a2a2a")
                row_frame.grid(row=idx, column=0, columnspan=7, sticky="ew", pady=2)

                # Date
                CTkLabel(
                    row_frame,
                    text=data['date'],
                    font=("Inter", 12)
                ).grid(row=0, column=0, padx=10, pady=5)

                # Room
                CTkLabel(
                    row_frame,
                    text=data['room_name'],
                    font=("Inter", 12)
                ).grid(row=0, column=1, padx=10, pady=5)

                # User
                user_doc = db.collection('users').document(data['user_id']).get()
                user_name = user_doc.to_dict()['full_name'] if user_doc.exists else "Unknown"
                CTkLabel(
                    row_frame,
                    text=user_name,
                    font=("Inter", 12)
                ).grid(row=0, column=2, padx=10, pady=5)

                # Time
                time_text = f"{data['start_time']} - {data['end_time']}"
                CTkLabel(
                    row_frame,
                    text=time_text,
                    font=("Inter", 12)
                ).grid(row=0, column=3, padx=10, pady=5)

                # Purpose
                CTkLabel(
                    row_frame,
                    text=data['purpose'],
                    font=("Inter", 12)
                ).grid(row=0, column=4, padx=10, pady=5)

                # Status with color coding
                status_colors = {
                    'pending': "#FFD700",
                    'approved': "#00FF00",
                    'rejected': "#FF0000"
                }
                CTkLabel(
                    row_frame,
                    text=data['status'].capitalize(),
                    font=("Inter", 12),
                    text_color=status_colors.get(data['status'], "white")
                ).grid(row=0, column=5, padx=10, pady=5)

                # Actions
                if data['status'] == 'pending':
                    actions_frame = CTkFrame(row_frame, fg_color="transparent")
                    actions_frame.grid(row=0, column=6, padx=10, pady=5)

                    CTkButton(
                        actions_frame,
                        text="Approve",
                        width=80,
                        command=lambda r=res.id, d=data: approve_reservation(r, d),
                        fg_color="#28a745",
                        hover_color="#218838"
                    ).pack(side=LEFT, padx=2)

                    CTkButton(
                        actions_frame,
                        text="Reject",
                        width=80,
                        command=lambda r=res.id, d=data: reject_reservation(r, d),
                        fg_color="#dc3545",
                        hover_color="#c82333"
                    ).pack(side=LEFT, padx=2)

        except Exception as e:
            CTkLabel(
                reservations_scroll,
                text=f"Error loading reservations: {str(e)}",
                text_color="#ff0000"
            ).grid(row=1, column=0, columnspan=7, pady=20)

    def load_rooms():
        for widget in rooms_frame.winfo_children():
            widget.destroy()

        rooms_scroll = CTkScrollableFrame(rooms_frame, fg_color="#242424")
        rooms_scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # Add "Add Room" button
        add_room_btn = CTkButton(
            rooms_scroll,
            text="+ Add New Room",
            fg_color="#2b5d8c",
            hover_color="#1c4c7d"
        )
        add_room_btn.pack(pady=(0, 20), anchor="w")

        # Headers
        headers = ["Room Name", "Capacity", "Status", "Actions"]
        for i, header in enumerate(headers):
            CTkLabel(
                rooms_scroll,
                text=header,
                font=("Inter", 14, "bold"),
                text_color="white"
            ).grid(row=1, column=i, padx=10, pady=5, sticky="w")

        try:
            rooms = db.collection('rooms').get()
            for idx, room in enumerate(rooms, 2):
                data = room.to_dict()

                CTkLabel(rooms_scroll, text=data['name']).grid(row=idx, column=0, padx=10, pady=5)
                CTkLabel(rooms_scroll, text=data['capacity']).grid(row=idx, column=1, padx=10, pady=5)
                CTkLabel(rooms_scroll, text=data['status']).grid(row=idx, column=2, padx=10, pady=5)

                actions_frame = CTkFrame(rooms_scroll, fg_color="transparent")
                actions_frame.grid(row=idx, column=3, padx=10, pady=5)

                CTkButton(
                    actions_frame,
                    text="Edit",
                    width=60,
                    fg_color="#2b5d8c"
                ).pack(side=LEFT, padx=2)

                CTkButton(
                    actions_frame,
                    text="Delete",
                    width=60,
                    fg_color="#dc3545"
                ).pack(side=LEFT, padx=2)

        except Exception as e:
            CTkLabel(
                rooms_scroll,
                text=f"Error loading rooms: {str(e)}",
                text_color="#ff0000"
            ).grid(row=2, column=0, columnspan=4, pady=20)

    def load_users():
        for widget in users_frame.winfo_children():
            widget.destroy()

        users_scroll = CTkScrollableFrame(users_frame, fg_color="#242424")
        users_scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # Headers
        headers = ["Name", "Email", "Role", "Status", "Actions"]
        for i, header in enumerate(headers):
            CTkLabel(
                users_scroll,
                text=header,
                font=("Inter", 14, "bold"),
                text_color="white"
            ).grid(row=0, column=i, padx=10, pady=5, sticky="w")

        try:
            users = db.collection('users').get()
            for idx, user in enumerate(users, 1):
                data = user.to_dict()

                CTkLabel(users_scroll, text=data.get('full_name', 'N/A')).grid(row=idx, column=0, padx=10, pady=5)
                CTkLabel(users_scroll, text=data.get('email', 'N/A')).grid(row=idx, column=1, padx=10, pady=5)
                CTkLabel(users_scroll, text=data.get('role', 'User')).grid(row=idx, column=2, padx=10, pady=5)
                CTkLabel(users_scroll, text=data.get('status', 'Active')).grid(row=idx, column=3, padx=10, pady=5)

                actions_frame = CTkFrame(users_scroll, fg_color="transparent")
                actions_frame.grid(row=idx, column=4, padx=10, pady=5)

                CTkButton(
                    actions_frame,
                    text="Edit",
                    width=60,
                    fg_color="#2b5d8c"
                ).pack(side=LEFT, padx=2)

                CTkButton(
                    actions_frame,
                    text="Disable",
                    width=60,
                    fg_color="#dc3545"
                ).pack(side=LEFT, padx=2)

        except Exception as e:
            CTkLabel(
                users_scroll,
                text=f"Error loading users: {str(e)}",
                text_color="#ff0000"
            ).grid(row=1, column=0, columnspan=5, pady=20)

    # Initialize with reservations tab
    switch_tab("reservations")


# Modify the show_login_frame function to add admin login button

def show_login_frame():
    if hasattr(app, 'current_frame'):
        app.current_frame.destroy()

    login_frame = CTkFrame(
        app,
        width=300,
        height=460,
        corner_radius=15,
        fg_color="#1a1a1a",
        border_width=2,
        border_color="#ffffff"
    )
    login_frame.place(relx=0.5, rely=0.5, anchor=CENTER)
    login_frame.pack_propagate(False)
    app.current_frame = login_frame


def show_admin_login_frame():
    # Clean up any existing frames
    for widget in app.winfo_children():
        if isinstance(widget, CTkFrame):
            widget.destroy()

    # Create new frame
    admin_login_frame = CTkFrame(
        app,
        width=380,
        height=320,
        corner_radius=15,
        fg_color="#1a1a1a",
        border_width=2,
        border_color="white"
    )
    admin_login_frame.place(relx=0.5, rely=0.5, anchor="center")
    admin_login_frame.pack_propagate(False)
    app.current_frame = admin_login_frame

    # Return button
    return_button = CTkButton(
        admin_login_frame,
        text="←",
        width=20,
        height=15,
        font=("Inter", 18, "bold"),
        command=show_login_frame,
        fg_color="#333333",
        text_color="white",
        hover_color="#4d4d4d",
        corner_radius=10,
        border_width=1,
        border_color="#ffffff"
    )
    return_button.place(x=15, y=10)

    # Title Label
    CTkLabel(admin_login_frame, text="Admin Login", font=("Inter", 20, "bold"), text_color="white").pack(pady=(30, 15))

    # Admin ID
    CTkLabel(admin_login_frame, text="Admin ID:", font=("Inter", 16), text_color="white").pack(pady=(5, 5))
    admin_id_entry = CTkEntry(admin_login_frame, width=200, height=30)
    admin_id_entry.pack(pady=(0, 10))

    # Password
    CTkLabel(admin_login_frame, text="Password:", font=("Inter", 16), text_color="white").pack(pady=(5, 5))
    admin_password_entry = CTkEntry(admin_login_frame, width=200, height=30, show="*")
    admin_password_entry.pack(pady=(0, 10))

    def admin_login():
        admin_id = admin_id_entry.get()
        password = admin_password_entry.get()

        if not admin_id or not password:
            show_message("Error", "Please fill in all fields")
            return

        try:
            admin_doc = db.collection('admins').document(admin_id).get()
            if admin_doc.exists and admin_doc.to_dict()['password'] == password:
                db.collection('admins').document(admin_id).update({'last_login': datetime.now()})
                show_admin_dashboard(admin_id, admin_doc.to_dict()['full_name'])
            else:
                show_message("Error", "Invalid Admin Credentials")
        except Exception as e:
            show_message("Error", f"Login failed: {str(e)}")

    # Login button
    CTkButton(
        admin_login_frame,
        text="Login",
        width=200,
        height=40,
        font=("Inter", 14),
        command=admin_login,
        fg_color="#333333",
        text_color="white",
        hover_color="#4d4d4d",
        corner_radius=10,
        border_width=1,
        border_color="#ffffff"
    ).pack(pady=20)


# Initialize Firebase
cred = credentials.Certificate(
    "C:/Users/justi/Desktop/Jan/CPOOP Project/nu-arf-firebase-adminsdk-fbsvc-ccc7de169a.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

admin_doc = db.collection('admins').document("admin123").get()


def create_user_data(id_number, password, full_name, program):
    return {
        'id_number': id_number,
        'password': password,
        'full_name': full_name,
        'program': program,
        'created_at': datetime.now(),
        'last_login': datetime.now()
    }


def create_room_data(room_id, room_name, capacity, status):
    return {
        'room_id': room_id,
        'room_name': room_name,
        'capacity': capacity,
        'status': status,
        'created_at': datetime.now()
    }


# Theme settings
customtkinter.set_appearance_mode("system")
customtkinter.set_default_color_theme("blue")

# Create the main app window
app = CTk()
app.geometry('1200x650')
app.resizable(False, False)
app.title("NU - ARF")

# Set window icon using tk root window
app.wm_iconbitmap("C:/Users/justi/Desktop/Jan/CPOOP Project/nu_logo.ico")

# Load and set the background image
bg_image = customtkinter.CTkImage(
    light_image=Image.open("C:/Users/justi/Desktop/Jan/CPOOP Project/nu_jhocson.png"),
    dark_image=Image.open("C:/Users/justi/Desktop/Jan/CPOOP Project/nu_jhocson.png"),
    size=(1200, 650)
)
bg_label = CTkLabel(app, image=bg_image, text="")
bg_label.place(x=0, y=0)

# Admin login button
admin_button = CTkButton(
    app,
    text="Admin Login",
    width=120,
    height=35,
    font=("Inter", 14),
    command=show_admin_login_frame,
    fg_color="#761a24",
    text_color="white",
    hover_color="#b92938",
    corner_radius=10
)
admin_button.place(x=10, y=10)
admin_button.lift()

# Center the window
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()
x = int(screen_width // 2) - (1200 // 2)
y = int(screen_height // 2) - (650 // 2)
app.geometry(f'1200x650+{x}+{y}')


def show_message(title, message):
    messagebox.showinfo(title, message)


def show_floor_selection(user_id=None, user_name=None):
    if hasattr(app, 'current_frame'):
        app.current_frame.destroy()

    # Create main frame with the same dimensions as the app
    floor_frame = CTkFrame(
        app,
        width=1200,
        height=650,
        fg_color="#1a1a1a",
    )
    floor_frame.place(x=0, y=0)
    app.current_frame = floor_frame

    # Header
    header_frame = CTkFrame(floor_frame, fg_color="#333333", height=60, width=1200)
    header_frame.place(x=0, y=0)

    # Title
    title_label = CTkLabel(
        header_frame,
        text="NU Room Reservation System",
        font=("Inter", 22, "bold"),
        text_color="white"
    )
    title_label.place(relx=0.5, rely=0.5, anchor=CENTER)

    # User info
    if user_name:
        user_label = CTkLabel(
            header_frame,
            text=f"User: {user_name}",
            font=("Inter", 14),
            text_color="white"
        )
        user_label.place(relx=0.05, rely=0.5, anchor=W)

    # Logout button
    logout_button = CTkButton(
        header_frame,
        text="Logout",
        width=100,
        height=30,
        font=("Inter", 14),
        command=lambda: [app.current_frame.destroy(), show_login_frame()],
        fg_color="#444444",
        text_color="white",
        hover_color="#666666",
        corner_radius=8
    )
    logout_button.place(relx=0.95, rely=0.5, anchor=E)

    # Main content area with title
    main_content = CTkFrame(floor_frame, fg_color="transparent", width=700, height=400)
    main_content.place(relx=0.5, rely=0.55, anchor=CENTER)

    # Title for floor selection
    floor_title = CTkLabel(
        main_content,
        text="Select a Floor",
        font=("Inter", 28, "bold"),
        text_color="white"
    )
    floor_title.place(relx=0.5, rely=0.1, anchor=CENTER)

    # Floor selection buttons
    floor_buttons_frame = CTkFrame(main_content, fg_color="transparent", width=800, height=400)
    floor_buttons_frame.place(relx=0.5, rely=0.5, anchor=CENTER)

    floors = [2, 3, 4, 5]
    floor_buttons = []

    # Adjust these parameters
    btn_width, btn_height = 200, 150
    spacing_x, spacing_y = 100, 80

    row, col = 0, 0
    max_cols = 2

    # Grid layout for floor buttons - adjust vertical positioning
    for floor in floors:
        # Calculate position - add more padding/margin
        x = col * (btn_width + spacing_x) + (700 - (max_cols * (btn_width + spacing_x) - spacing_x)) / 2
        y = row * (btn_height + spacing_y) + 30

        # Create button with slightly smaller size but same text size
        floor_button = CTkButton(
            floor_buttons_frame,
            text=f"{floor}{'nd' if floor == 2 else 'rd' if floor == 3 else 'th'} Floor",
            width=btn_width - 20,
            height=btn_height - 20,
            font=("Inter", 18, "bold"),
            fg_color="#1a5276",
            text_color="white",
            hover_color="#2980b9",
            corner_radius=15,
            border_width=2,
            border_color="#ffffff",
            command=lambda f=floor: show_room_selection(user_id, user_name, f)
        )
        floor_button.place(x=x, y=y)
        floor_buttons.append(floor_button)

        # Update grid position
        col += 1
        if col >= max_cols:
            col = 0
            row += 1


def get_floor_rooms(floor):
    # Room data mapping by floor
    if floor == 2:
        return [
            {"id": "202", "name": "Room 202", "capacity": 30, "status": "available"},
            {"id": "203", "name": "Room 203", "capacity": 40, "status": "available"},
            {"id": "204", "name": "Room 204", "capacity": 20, "status": "SDAO"},
            {"id": "205", "name": "Room 205", "capacity": 25, "status": "available"},
            {"id": "206", "name": "Room 206", "capacity": 45, "status": "maintenance"},
            {"id": "207", "name": "Room 207", "capacity": 30, "status": "available"},
            {"id": "208", "name": "Room 208", "capacity": 35, "status": "available"},
            {"id": "209", "name": "Room 209", "capacity": 30, "status": "available"},
            {"id": "210", "name": "Room 210", "capacity": 20, "status": "Guidance Office"},
            {"id": "211", "name": "Room 211", "capacity": 25, "status": "NSTP"},
            {"id": "212", "name": "Room 212", "capacity": 35, "status": "maintenance"},
            {"id": "213", "name": "Room 213", "capacity": 40, "status": "available"},
            {"id": "214", "name": "Room 214", "capacity": 30, "status": "available"},
            {"id": "215", "name": "Room 215", "capacity": 45, "status": "available"},
            {"id": "216", "name": "Room 216", "capacity": 30, "status": "available"},
            {"id": "217", "name": "Room 217", "capacity": 35, "status": "available"},
            {"id": "218", "name": "Room 218", "capacity": 40, "status": "maintenance"},
            {"id": "219", "name": "Room 219", "capacity": 30, "status": "available"},
            {"id": "220", "name": "Room 220", "capacity": 45, "status": "available"},
            {"id": "221", "name": "Room 221", "capacity": 35, "status": "available"},
            {"id": "222", "name": "Room 222", "capacity": 30, "status": "available"},
            {"id": "223", "name": "Room 223", "capacity": 40, "status": "available"},
            {"id": "224", "name": "Room 224", "capacity": 35, "status": "available"},
        ]
    # [Other floor data remains unchanged]
    elif floor == 3:
        return [
            {"id": "302", "name": "Room 302", "capacity": 35, "status": "Faculty"},
            {"id": "303", "name": "Room 303", "capacity": 30, "status": "available"},
            {"id": "304", "name": "Room 304", "capacity": 40, "status": "Faculty"},
            {"id": "305", "name": "Room 305", "capacity": 25, "status": "available"},
            {"id": "306", "name": "Room 306", "capacity": 50, "status": "Board Room"},
            {"id": "307", "name": "Room 307", "capacity": 45, "status": "HR Office"},
            {"id": "308", "name": "Room 308", "capacity": 20, "status": "Auditing Office"},
            {"id": "309", "name": "Room 309", "capacity": 38, "status": "available"},
            {"id": "310", "name": "Room 310", "capacity": 42, "status": "available"},
            {"id": "311", "name": "Room 311", "capacity": 28, "status": "available"},
            {"id": "312", "name": "Room 312", "capacity": 37, "status": "available"},
            {"id": "313", "name": "Room 313", "capacity": 40, "status": "available"},
            {"id": "314", "name": "Room 314", "capacity": 40, "status": "available"},
            {"id": "315", "name": "Room 315", "capacity": 40, "status": "available"},
            {"id": "316", "name": "Room 316", "capacity": 40, "status": "available"},
            {"id": "317", "name": "Room 317", "capacity": 40, "status": "available"},
            {"id": "318", "name": "Room 318", "capacity": 40, "status": "available"},
            {"id": "319", "name": "Room 319", "capacity": 40, "status": "available"},
            {"id": "320", "name": "Room 320", "capacity": 33, "status": "Chapel"},
            {"id": "321", "name": "Room 321", "capacity": 45, "status": "available"},
            {"id": "322", "name": "Room 322", "capacity": 40, "status": "available"},
            {"id": "323", "name": "Room 323", "capacity": 40, "status": "available"},
            {"id": "324", "name": "Room 324", "capacity": 35, "status": "available"},
        ]
    elif floor == 4:
        return [
            {"id": "402", "name": "Room 402", "capacity": 40, "status": "available"},
            {"id": "404", "name": "Room 404", "capacity": 20, "status": "maintenance"},
            {"id": "405", "name": "Room 405", "capacity": 25, "status": "available"},
            {"id": "406", "name": "Room 406", "capacity": 45, "status": "available"},
            {"id": "407", "name": "Room 407", "capacity": 30, "status": "available"},
            {"id": "408", "name": "Room 408", "capacity": 35, "status": "Storage"},
            {"id": "409", "name": "Room 409", "capacity": 30, "status": "available"},
            {"id": "410", "name": "Room 410", "capacity": 20, "status": "available"},
            {"id": "412", "name": "Room 412", "capacity": 25, "status": "available"},
            {"id": "413", "name": "Room 413", "capacity": 35, "status": "available"},
            {"id": "414", "name": "Room 414", "capacity": 40, "status": "available"},
            {"id": "415", "name": "Room 415", "capacity": 45, "status": "available"},
            {"id": "416", "name": "Room 416", "capacity": 40, "status": "available"},
            {"id": "417", "name": "Room 417", "capacity": 35, "status": "available"},
            {"id": "418", "name": "Room 418", "capacity": 40, "status": "available"},
            {"id": "419", "name": "Room 419", "capacity": 30, "status": "available"},
            {"id": "420", "name": "Room 420", "capacity": 45, "status": "available"},
            {"id": "421", "name": "Room 421", "capacity": 35, "status": "available"},
            {"id": "422", "name": "Room 422", "capacity": 30, "status": "available"},
            {"id": "423", "name": "Room 423", "capacity": 40, "status": "available"},
            {"id": "424", "name": "Room 424", "capacity": 35, "status": "available"},
            {"id": "425", "name": "Room 425", "capacity": 50, "status": "available"},
        ]
    elif floor == 5:
        return [
            {"id": "501", "name": "502 (Classroom 01)", "capacity": 40, "status": "available"},
            {"id": "502", "name": "504 (Classroom 02)", "capacity": 40, "status": "occupied"},
            {"id": "503", "name": "506 (Lab 01)", "capacity": 46, "status": "available"},
            {"id": "504", "name": "508 (Lab 02)", "capacity": 46, "status": "maintenance"},
            {"id": "505", "name": "512 (Cold Kitchen)", "capacity": 30, "status": "available"},
            {"id": "506", "name": "513 (Baking Kitchen)", "capacity": 30, "status": "available"},
            {"id": "507", "name": "515 (Hot Kitchen 04)", "capacity": 30, "status": "occupied"},
            {"id": "508", "name": "517 (Hot Kitchen 03)", "capacity": 30, "status": "available"},
            {"id": "509", "name": "519 (Hot Kitchen 02)", "capacity": 30, "status": "available"},
            {"id": "510", "name": "521 (Hot Kitchen 01)", "capacity": 30, "status": "available"},
            {"id": "511", "name": "522 (Demo Kitchen)", "capacity": 30, "status": "available"},
            {"id": "512", "name": "Restaurant Bar Cafe", "capacity": 40, "status": "available"},
            {"id": "513", "name": "Function Room", "capacity": 144, "status": "available"},
        ]
    else:
        return []


# Function to upload rooms to Firestore
def upload_rooms():
    floors = [2, 3, 4, 5]
    for floor in floors:
        rooms = get_floor_rooms(floor)
        for room in rooms:
            room_id = room["id"]
            room["floor"] = floor
            db.collection("rooms").document(room_id).set(room)


# Run function to upload rooms
upload_rooms()


def show_room_selection(user_id=None, user_name=None, floor=2):
    if hasattr(app, 'current_frame'):
        app.current_frame.destroy()

    # Create main frame with the same dimensions as the app
    room_frame = CTkFrame(
        app,
        width=1200,
        height=650,
        fg_color="#1a1a1a",
    )
    room_frame.place(x=0, y=0)
    app.current_frame = room_frame

    # Header
    header_frame = CTkFrame(room_frame, fg_color="#333333", height=60, width=1200)
    header_frame.place(x=0, y=0)

    # Title
    title_label = CTkLabel(
        header_frame,
        text="NU Room Reservation System",
        font=("Inter", 22, "bold"),
        text_color="white"
    )
    title_label.place(relx=0.5, rely=0.5, anchor=CENTER)

    # User info
    if user_name:
        user_label = CTkLabel(
            header_frame,
            text=f"User: {user_name}",
            font=("Inter", 14),
            text_color="white"
        )
        user_label.place(relx=0.05, rely=0.5, anchor=W)

    # Logout button
    logout_button = CTkButton(
        header_frame,
        text="Logout",
        width=100,
        height=30,
        font=("Inter", 14),
        command=lambda: [app.current_frame.destroy(), show_login_frame()],
        fg_color="#444444",
        text_color="white",
        hover_color="#666666",
        corner_radius=8
    )
    logout_button.place(relx=0.95, rely=0.5, anchor=E)

    # Back button to return to floor selection
    back_button = CTkButton(
        room_frame,
        text="← Back to Floors",
        width=150,
        height=30,
        font=("Inter", 14),
        command=lambda: [app.current_frame.destroy(), show_floor_selection(user_id, user_name)],
        fg_color="#444444",
        text_color="white",
        hover_color="#666666",
        corner_radius=8
    )
    back_button.place(x=20, y=70)

    # Floor title
    floor_title = CTkLabel(
        room_frame,
        text=f"{floor}{'nd' if floor == 2 else 'rd' if floor == 3 else 'th'} Floor Rooms",
        font=("Inter", 24, "bold"),
        text_color="white"
    )
    floor_title.place(relx=0.5, rely=0.13, anchor=CENTER)

    # Room grid layout with scrollable frame
    rooms_container = CTkScrollableFrame(
        room_frame,
        width=1100,
        height=450,
        fg_color="#1a1a1a"
    )
    rooms_container.place(relx=0.5, rely=0.55, anchor=CENTER)

    # Get rooms for the selected floor
    rooms = get_floor_rooms(floor)

    # Current highlighted room
    current_highlight = None

    # Function to create room tiles with hover effect (cursor indicator)
    def create_room_tile(parent, room_data, row, col):
        # Determine color based on status
        if room_data["status"] == "available":
            color = "#1a5276"
        elif room_data["status"] == "occupied":
            color = "#7b241c"
        elif room_data["status"] == "SDAO":
            color = "#5E4C14"
        elif room_data["status"] == "Guidance Office":
            color = "#5E4C14"
        elif room_data["status"] == "NSTP":
            color = "#5E4C14"
        elif room_data["status"] == "Capstone":
            color = "#5E4C14"
        elif room_data["status"] == "HR Office":
            color = "#5E4C14"
        elif room_data["status"] == "Chapel":
            color = "#5E4C14"
        elif room_data["status"] == "Faculty":
            color = "#5E4C14"
        elif room_data["status"] == "Board Room":
            color = "#5E4C14"
        elif room_data["status"] == "Auditing Office":
            color = "#5E4C14"
        elif room_data["status"] == "Storage":
            color = "#5E4C14"
        else:
            color = "#626567"

        # Create room frame
        room_frame = CTkFrame(
            parent,
            width=180,
            height=130,
            corner_radius=10,
            fg_color=color,
            border_width=2,
            border_color="#ffffff"
        )
        room_frame.grid(row=row, column=col, padx=15, pady=15)
        room_frame.grid_propagate(False)

        # Room info
        CTkLabel(
            room_frame,
            text=room_data["name"],
            font=("Inter", 16, "bold"),
            text_color="white"
        ).place(relx=0.5, rely=0.3, anchor=CENTER)

        CTkLabel(
            room_frame,
            text=f"Capacity: {room_data['capacity']}",
            font=("Inter", 12),
            text_color="white"
        ).place(relx=0.5, rely=0.5, anchor=CENTER)

        status_label = CTkLabel(
            room_frame,
            text=f"Status: {room_data['status'].capitalize()}",
            font=("Inter", 12),
            text_color="white"
        )
        status_label.place(relx=0.5, rely=0.7, anchor=CENTER)

        # Hover effect (cursor indicator)
        def on_enter(event):
            nonlocal current_highlight
            current_highlight = room_data["id"]
            room_frame.configure(border_color="#ffd700", border_width=4)

            # Show room details in info panel
            info_title.configure(text=f"Room {room_data['id']} Details")
            info_details.configure(text=f"""
Name: {room_data['name']}
Capacity: {room_data['capacity']} people
Status: {room_data['status'].capitalize()}
            """)

        def on_leave(event):
            nonlocal current_highlight
            current_highlight = None
            room_frame.configure(border_color="#ffffff", border_width=2)

            # Clear info panel
            info_title.configure(text="Room Information")
            info_details.configure(text="Hover over a room to see details")

        def on_click(event):
            if room_data["status"] == "available":
                show_reservation_form(room_data, user_id, user_name, floor)
            else:
                show_message("Not Available", f"Room {room_data['name']} is currently {room_data['status']}.")

        room_frame.bind("<Enter>", on_enter)
        room_frame.bind("<Leave>", on_leave)
        room_frame.bind("<Button-1>", on_click)

    # Create room grid
    row, col = 0, 0
    max_cols = 4
    for i, room in enumerate(rooms):
        create_room_tile(rooms_container, room, row, col)
        col += 1
        if col >= max_cols:
            col = 0
            row += 1

    # Info panel on the right
    info_panel = CTkFrame(
        room_frame,
        width=250,
        height=400,
        corner_radius=15,
        fg_color="#333333",
        border_width=2,
        border_color="#ffffff"
    )
    info_panel.place(relx=.95, rely=0.5, anchor=E)

    info_title = CTkLabel(
        info_panel,
        text="Room Information",
        font=("Inter", 18, "bold"),
        text_color="white"
    )
    info_title.place(relx=0.5, rely=0.1, anchor=CENTER)

    info_details = CTkLabel(
        info_panel,
        text="Hover over a room to see details",
        font=("Inter", 14),
        text_color="white",
        justify="left",
        wraplength=220
    )
    info_details.place(relx=0.5, rely=0.3, anchor=CENTER)

    # Room statistics
    available_count = sum(1 for room in rooms if room["status"] == "available")
    occupied_count = sum(1 for room in rooms if room["status"] == "occupied")
    maintenance_count = sum(1 for room in rooms if room["status"] == "maintenance")

    stats_frame = CTkFrame(
        info_panel,
        width=220,
        height=200,
        corner_radius=10,
        fg_color="#444444",
    )
    stats_frame.place(relx=0.5, rely=0.7, anchor=CENTER)

    CTkLabel(
        stats_frame,
        text="Floor Statistics",
        font=("Inter", 16, "bold"),
        text_color="white"
    ).place(relx=0.5, rely=0.15, anchor=CENTER)

    CTkLabel(
        stats_frame,
        text=f"Total Rooms: {len(rooms)}",
        font=("Inter", 14),
        text_color="white"
    ).place(relx=0.5, rely=0.35, anchor=CENTER)

    CTkLabel(
        stats_frame,
        text=f"Available: {available_count}",
        font=("Inter", 14),
        text_color="#8cffb4"
    ).place(relx=0.5, rely=0.5, anchor=CENTER)

    CTkLabel(
        stats_frame,
        text=f"Occupied: {occupied_count}",
        font=("Inter", 14),
        text_color="#ff9e9e"
    ).place(relx=0.5, rely=0.65, anchor=CENTER)

    CTkLabel(
        stats_frame,
        text=f"Maintenance: {maintenance_count}",
        font=("Inter", 14),
        text_color="#626567"
    ).place(relx=0.5, rely=0.8, anchor=CENTER)


def show_reservation_form(room_data, user_id, user_name, floor):
    if hasattr(app, 'current_frame'):
        app.current_frame.destroy()

    reservation_frame = CTkFrame(
        app,
        width=500,
        height=500,
        corner_radius=15,
        fg_color="#1a1a1a",
        border_width=2,
        border_color="#ffffff"
    )
    reservation_frame.place(relx=0.5, rely=0.5, anchor=CENTER)
    reservation_frame.pack_propagate(False)
    app.current_frame = reservation_frame

    # Return button in top-left corner
    return_button = CTkButton(
        reservation_frame,
        text="←",
        width=30,
        height=30,
        font=("Inter", 16, "bold"),
        command=lambda: show_room_selection(user_id, user_name, floor),
        fg_color="#333333",
        text_color="white",
        hover_color="#4d4d4d",
        corner_radius=10,
        border_width=1,
        border_color="#ffffff"
    )
    return_button.place(x=10, y=10)

    # Title
    CTkLabel(
        reservation_frame,
        text=f"Reserve {room_data['name']}",
        font=("Inter", 24, "bold"),
        text_color="white"
    ).pack(pady=(20, 30))

    # Room info
    room_info_frame = CTkFrame(
        reservation_frame,
        width=400,
        height=80,
        corner_radius=10,
        fg_color="#333333",
        border_width=1,
        border_color="#ffffff"
    )
    room_info_frame.pack(pady=(0, 20))
    room_info_frame.pack_propagate(False)

    CTkLabel(
        room_info_frame,
        text=f"Room: {room_data['name']} | Capacity: {room_data['capacity']} | Status: {room_data['status'].capitalize()}",
        font=("Inter", 14),
        text_color="white"
    ).pack(expand=True)

    # Form fields
    # Create form frame
    form_frame = CTkFrame(reservation_frame, fg_color="#242424")
    form_frame.pack(pady=10)

    # Create canvas and scrollbar
    canvas = CTkCanvas(form_frame, bg='#242424', highlightthickness=0, width=500)
    scrollbar = CTkScrollbar(form_frame, orientation="vertical", command=canvas.yview)
    scrollable_frame = CTkFrame(canvas, fg_color="#242424", width=500)

    canvas.configure(yscrollcommand=scrollbar.set)

    # Pack scrollbar and canvas
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    # Create window in canvas for content
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    # Date selection
    CTkLabel(scrollable_frame, text="Date:", font=("Inter", 16), text_color="white").pack(anchor=W, pady=(10, 5))
    date_entry = CTkEntry(
        scrollable_frame,
        width=380,
        height=35,
        font=("Inter", 14),
        fg_color="#333333",
        text_color="white",
        corner_radius=10,
        border_width=1,
        border_color="#ffffff",
        placeholder_text="MM-DD-YYYY"
    )
    date_entry.pack(pady=(0, 10))

    # Time selection
    time_frame = CTkFrame(scrollable_frame, fg_color="transparent")
    time_frame.pack(fill=X, pady=10)

    # Start time
    start_frame = CTkFrame(time_frame, fg_color="transparent", width=180)
    start_frame.pack(side=LEFT)
    CTkLabel(start_frame, text="Start Time:", font=("Inter", 16), text_color="white").pack(anchor=W)
    start_time = CTkEntry(
        start_frame,
        width=180,
        height=35,
        font=("Inter", 14),
        fg_color="#333333",
        text_color="white",
        corner_radius=10,
        border_width=1,
        border_color="#ffffff",
        placeholder_text="HH:MM"
    )
    start_time.pack(pady=5)

    # End time
    end_frame = CTkFrame(time_frame, fg_color="transparent", width=180)
    end_frame.pack(side=RIGHT)
    CTkLabel(end_frame, text="End Time:", font=("Inter", 16), text_color="white").pack(anchor=W)
    end_time = CTkEntry(
        end_frame,
        width=180,
        height=35,
        font=("Inter", 14),
        fg_color="#333333",
        text_color="white",
        corner_radius=10,
        border_width=1,
        border_color="#ffffff",
        placeholder_text="HH:MM"
    )
    end_time.pack(pady=5)

    # Purpose
    CTkLabel(scrollable_frame, text="Purpose:", font=("Inter", 16), text_color="white").pack(anchor=W, pady=(10, 5))
    purpose_entry = CTkEntry(
        scrollable_frame,
        width=380,
        height=35,
        font=("Inter", 14),
        fg_color="#333333",
        text_color="white",
        corner_radius=10,
        border_width=1,
        border_color="#ffffff",
        placeholder_text="Enter purpose of reservation"
    )
    purpose_entry.pack(pady=(0, 10))

    # NUIS Email
    CTkLabel(scrollable_frame, text="Outlook Email:", font=("Inter", 16), text_color="white").pack(anchor=W,
                                                                                                   pady=(10, 5))
    nuisemail_entry = CTkEntry(
        scrollable_frame,
        width=380,
        height=35,
        font=("Inter", 14),
        fg_color="#333333",
        text_color="white",
        corner_radius=10,
        border_width=1,
        border_color="#ffffff",
        placeholder_text="Enter Outlook Email"
    )
    nuisemail_entry.pack(pady=(0, 20))

    def submit_reservation():
        date = date_entry.get()
        start = start_time.get()
        end = end_time.get()
        purpose = purpose_entry.get()
        nuisemail = nuisemail_entry.get()

        if not all([date, start, end, purpose, nuisemail]):
            show_message("Error", "Please fill in all fields")
            return

        try:
            # Validate inputs
            # (Add validation logic here)

            # Create reservation data
            reservation_data = {
                'room_id': room_data['id'],
                'room_name': room_data['name'],
                'floor': floor,
                'user_id': user_id,
                'date': date,
                'start_time': start,
                'end_time': end,
                'purpose': purpose,
                'nuisemail': nuisemail,
                'status': 'pending',
                'created_at': datetime.now()
            }

            # Add to Firebase
            db.collection('reservations').add(reservation_data)

            show_message("Success", f"Reservation for {room_data['name']} submitted successfully!")
            show_room_selection(user_id, user_name, floor)

        except Exception as e:
            show_message("Error", f"Reservation failed: {str(e)}")

    # Submit button
    submit_button = CTkButton(
        reservation_frame,
        text="Submit Reservation",
        width=380,
        height=40,
        font=("Inter", 16),
        command=submit_reservation,
        fg_color="#1a5276",
        text_color="white",
        hover_color="#2980b9",
        corner_radius=10,
        border_width=1,
        border_color="#ffffff"
    )
    submit_button.pack(pady=20)

    # Configure the scroll region after all widgets are added
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))


def show_login_frame():
    if hasattr(app, 'current_frame'):
        app.current_frame.destroy()

    login_frame = CTkFrame(
        app,
        width=300,
        height=420,
        corner_radius=15,
        fg_color="#1a1a1a",
        border_width=2,
        border_color="#ffffff"
    )
    login_frame.place(relx=0.5, rely=0.5, anchor=CENTER)
    login_frame.pack_propagate(False)
    app.current_frame = login_frame

    # Title
    title_label = CTkLabel(
        login_frame,
        text="Welcome",
        font=("Inter", 24, "bold"),
        text_color="white"
    )
    title_label.pack(pady=(20, 10))

    # ID Number
    CTkLabel(login_frame, text="ID - Number:", font=("Inter", 20), text_color="white").pack(pady=(20, 5))
    id_entry = CTkEntry(
        login_frame,
        width=200,
        height=25,
        font=("Inter", 16),
        fg_color="#333333",
        text_color="white",
        corner_radius=10,
        justify="center",
        border_width=1,
        border_color="#ffffff"
    )
    id_entry.pack(pady=5)

    # Password
    CTkLabel(login_frame, text="Password:", font=("Inter", 20), text_color="white").pack(pady=(20, 5))
    password_entry = CTkEntry(
        login_frame,
        width=200,
        height=35,
        font=("Inter", 16),
        show="*",
        fg_color="#333333",
        text_color="white",
        corner_radius=10,
        justify="center",
        border_width=1,
        border_color="#ffffff"
    )
    password_entry.pack(pady=5)

    # Password toggle button
    def toggle_password():
        if password_entry.cget('show') == '':
            password_entry.configure(show='*')
            show_password_button.configure(text='👁️')
        else:
            password_entry.configure(show='')
            show_password_button.configure(text='🔒')

    show_password_button = CTkButton(
        password_entry,
        text='👁️',
        width=20,
        height=20,
        font=("Inter", 12),
        fg_color="transparent",
        text_color="white",
        hover_color="#4d4d4d",
        corner_radius=0,
        border_width=0,
        command=toggle_password
    )
    show_password_button.place(relx=0.9, rely=0.5, anchor=CENTER)

    def login_user():
        id_num = id_entry.get()
        pwd = password_entry.get()

        if not id_num or not pwd:
            show_message("Error", "Please fill in all fields")
            return

        try:
            user_doc = db.collection('users').document(id_num).get()

            if not user_doc.exists:
                show_message("Error", "User not found")
                return

            user_data = user_doc.to_dict()
            if user_data['password'] == pwd:
                show_message("Success", "Login successful!")
                db.collection('users').document(id_num).update({
                    'last_login': datetime.now()
                })
                # Navigate to floor selection screen
                show_floor_selection(id_num, user_data['full_name'])
            else:
                show_message("Error", "Invalid password")

        except Exception as e:
            show_message("Error", f"Login failed: {str(e)}")

    # Login button
    login_button = CTkButton(
        login_frame,
        text="Login",
        width=200,
        height=40,
        font=("Inter", 16),
        command=login_user,
        fg_color="#333333",
        text_color="white",
        hover_color="#4d4d4d",
        corner_radius=10,
        border_width=1,
        border_color="#ffffff"
    )
    login_button.pack(pady=30)

    # Register button
    register_button = CTkButton(
        login_frame,
        text="Register",
        width=200,
        height=40,
        font=("Inter", 16),
        command=show_register_frame,
        fg_color="#333333",
        text_color="white",
        hover_color="#4d4d4d",
        corner_radius=10,
        border_width=1,
        border_color="#ffffff"
    )
    register_button.pack(pady=(0, 30))


def show_register_frame():
    if hasattr(app, 'current_frame'):
        app.current_frame.destroy()

    register_frame = CTkFrame(
        app,
        width=350,
        height=400,
        corner_radius=15,
        fg_color="#1a1a1a",
        border_width=2,
        border_color="#ffffff"
    )
    register_frame.place(relx=0.5, rely=0.5, anchor=CENTER)
    register_frame.pack_propagate(False)
    app.current_frame = register_frame

    # Return button in top-left corner
    return_button = CTkButton(
        register_frame,
        text="←",
        width=30,
        height=30,
        font=("Inter", 16, "bold"),
        command=show_login_frame,
        fg_color="#333333",
        text_color="white",
        hover_color="#4d4d4d",
        corner_radius=10,
        border_width=1,
        border_color="#ffffff"
    )
    return_button.place(x=10, y=10)

    # Title
    CTkLabel(
        register_frame,
        text="Create Account",
        font=("Inter", 24, "bold"),
        text_color="white"
    ).pack(pady=(10, 5))

    # Entry fields with consistent styling
    fields = [
        ("ID-Number:", "reg_id_entry"),
        ("Full Name:", "name_entry"),
        ("Program:", "program_entry", "e.g., CpE - 2nd year"),
        ("Password:", "reg_password_entry", None, "*"),
    ]

    entries = {}
    for field_info in fields:
        field_name = field_info[0]
        entry_name = field_info[1]
        placeholder = field_info[2] if len(field_info) > 2 else None
        show = field_info[3] if len(field_info) > 3 else None

        CTkLabel(register_frame, text=field_name, font=("Inter", 14), text_color="white").pack(
            pady=(5, 2))
        entry = CTkEntry(
            register_frame,
            width=250,
            height=30,
            font=("Inter", 14),
            fg_color="#333333",
            text_color="white",
            corner_radius=10,
            border_width=1,
            border_color="#ffffff",
            placeholder_text=placeholder,
            show=show
        )
        entry.pack(pady=2)
        entries[entry_name] = entry

        # Add show/hide password button for password field
        if entry_name == "reg_password_entry":
            def toggle_password():
                if entries['reg_password_entry'].cget('show') == '':
                    entries['reg_password_entry'].configure(show='*')
                    show_password_button.configure(text='👁️')
                else:
                    entries['reg_password_entry'].configure(show='')
                    show_password_button.configure(text='🔒')

            show_password_button = CTkButton(
                entries['reg_password_entry'],
                text='👁️',
                width=20,
                height=20,
                font=("Inter", 12),
                fg_color="transparent",
                text_color="white",
                hover_color="#4d4d4d",
                corner_radius=0,
                border_width=0,
                command=toggle_password
            )
            show_password_button.place(relx=0.9, rely=0.5, anchor=CENTER)

    def submit_registration():
        id_num = entries['reg_id_entry'].get()
        full_name = entries['name_entry'].get()
        program = entries['program_entry'].get()
        password = entries['reg_password_entry'].get()

        if not all([id_num, full_name, program, password]):
            show_message("Error", "Please fill in all fields")
            return

        try:
            users_ref = db.collection('users')
            if users_ref.document(id_num).get().exists:
                show_message("Error", "ID Number already registered")
                return

            user_data = create_user_data(id_num, password, full_name, program)
            users_ref.document(id_num).set(user_data)

            show_message("Success", "Registration successful!")
            show_login_frame()

        except Exception as e:
            show_message("Error", f"Registration failed: {str(e)}")

    # Submit button with consistent styling
    submit_button = CTkButton(
        register_frame,
        text="Register",
        width=250,
        height=35,
        font=("Inter", 14),
        command=submit_registration,
        fg_color="#333333",
        text_color="white",
        hover_color="#4d4d4d",
        corner_radius=10,
        border_width=1,
        border_color="#ffffff"
    )
    submit_button.pack(pady=15)


# Set window transparency
app.attributes('-alpha', 0.95)

# Show initial login frame
show_login_frame()
create_initial_admin()
app.mainloop()