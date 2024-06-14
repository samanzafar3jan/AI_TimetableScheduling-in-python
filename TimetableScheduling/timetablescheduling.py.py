import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import random


class Room:
    def _init_(self, number, capacity):
        self.number = number
        self.capacity = capacity


class Course:
    def _init_(self, name, duration, professor, students_enrolled):
        self.name = name
        self.duration = duration
        self.professor = professor
        self.students_enrolled = students_enrolled
        self.timeslots = [None] * duration
        self.assigned_room = None


class TimeTable:
    def _init_(self, courses, rooms, num_timeslots):
        self.courses = courses
        self.rooms = rooms
        self.num_timeslots = num_timeslots


def generate_initial_timetable(courses, rooms, num_timeslots):
    timetable = TimeTable(courses, rooms, num_timeslots)
    for course in timetable.courses:
        course.timeslots = [None] * course.duration
    return timetable

def assign_timeslots(timetable):
    available_slots = [(ts, room) for ts in range(1, timetable.num_timeslots + 1) for room in
                       range(1, len(timetable.rooms) + 1)]

    # Sort courses by students_enrolled in descending order
    sorted_courses = sorted(timetable.courses, key=lambda x: x.students_enrolled, reverse=True)

    for course in sorted_courses:
        assigned_slots = None
        assigned_room = None

        # Use a copy of available_slots to avoid modifying the original list
        slots_copy = available_slots.copy()

        for slot in slots_copy:
            consecutive_slots = [(slot[0] + i, slot[1]) for i in range(course.duration)]

            # Check if consecutive_slots are available for the course
            if all(consecutive_slot not in [(c_timeslot[0], c_timeslot[1]) for c_timeslot in
                                             course.timeslots if c_timeslot]
                   for consecutive_slot in consecutive_slots):

                # Check if the assigned room has sufficient capacity
                if timetable.rooms[slot[1] - 1].capacity >= course.students_enrolled:
                    # Check if the professor is available during the consecutive_slots
                    professor_available = all(consecutive_slot not in [(c_timeslot[0], c_timeslot[1]) for other_course in
                                                                        timetable.courses if other_course.professor == course.professor
                                                                        for c_timeslot in other_course.timeslots if c_timeslot]
                                              for consecutive_slot in consecutive_slots)

                    if professor_available:
                        assigned_slots = consecutive_slots
                        assigned_room = timetable.rooms[slot[1] - 1]
                        break

        if assigned_slots and assigned_room:
            course.timeslots = assigned_slots
            course.assigned_room = assigned_room

            # Remove assigned slots from available_slots
            for slot in assigned_slots:
                available_slots.remove(slot)


def objective_function(timetable):
    conflicts = 0
    room_timeslots = {(ts, room): set() for ts in range(1, timetable.num_timeslots + 1) for room in
                      range(1, len(timetable.rooms) + 1)}

    for course in timetable.courses:
        for timeslot in course.timeslots:
            if timeslot is not None:
                if timeslot in room_timeslots and course.professor in room_timeslots[timeslot]:
                    conflicts += 1
                room_timeslots[timeslot].add(course.professor)

    return conflicts


def display_timetable(timetable):
    root = tk.Tk()
    root.title("University Timetable Scheduler")

    tree = ttk.Treeview(root)
    tree["columns"] = ("Course", "Professor", "Students Enrolled", "Duration", "Timeslots", "Assigned Room")
    tree.heading("#0", text="Slot")
    tree.column("#0", anchor="center", width=50)
    tree.heading("Course", text="Course")
    tree.column("Course", anchor="w", width=150)
    tree.heading("Professor", text="Professor")
    tree.column("Professor", anchor="w", width=150)
    tree.heading("Students Enrolled", text="Students Enrolled")
    tree.column("Students Enrolled", anchor="center", width=150)
    tree.heading("Duration", text="Duration")
    tree.column("Duration", anchor="center", width=100)
    tree.heading("Timeslots", text="Timeslots")
    tree.column("Timeslots", anchor="center", width=150)
    tree.heading("Assigned Room", text="Assigned Room")
    tree.column("Assigned Room", anchor="center", width=150)
    tree.grid(row=0, column=0, padx=10, pady=10, columnspan=3)

    for i, course in enumerate(timetable.courses, start=1):
        # Check if timeslots are not None before generating the string representation
        timeslots_str = ', '.join([f"{ts[0]}, Room {ts[1]}" if ts is not None else "Not Assigned" for ts in course.timeslots])
        assigned_room_str = f"Room {course.assigned_room.number}" if course.assigned_room else "Not Assigned"
        tree.insert("", "end", iid=i,
                    values=(course.name, course.professor, course.students_enrolled,
                            course.duration, timeslots_str, assigned_room_str))

    def modify_timetable():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showinfo("Error", "Please select a course.")
            return

        selected_course_index = int(selected_item[0]) - 1
        selected_course = timetable.courses[selected_course_index]

        new_timeslot = prompt_for_timeslot(selected_course.name)
        if not check_conflict(selected_course, new_timeslot, timetable):
            selected_course.timeslots = [(new_timeslot[0] + i, new_timeslot[1]) for i in range(selected_course.duration)]
            update_treeview()
        else:
            messagebox.showerror("Conflict", "There is a conflict with the selected timeslot.")

    def update_treeview():
        for item in tree.get_children():
            tree.delete(item)
        for i, course in enumerate(timetable.courses, start=1):
            # Check if timeslots are not None before generating the string representation
            timeslots_str = ', '.join([f"{ts[0]}, Room {ts[1]}" if ts is not None else "Not Assigned" for ts in course.timeslots])
            assigned_room_str = f"Room {course.assigned_room.number}" if course.assigned_room else "Not Assigned"
            tree.insert("", "end", iid=i,
                        values=(course.name, course.professor, course.students_enrolled,
                                course.duration, timeslots_str, assigned_room_str))

    ttk.Button(root, text="Modify Timetable", command=modify_timetable).grid(row=1, column=0, columnspan=3, pady=10)

    root.mainloop()


def create_timetable():
    num_courses = int(input("Enter the number of courses: "))
    num_rooms = int(input("Enter the number of rooms: "))
    num_timeslots = int(input("Enter the number of time slots: "))

    rooms = []
    for i in range(1, num_rooms + 1):
        capacity = int(input(f"Enter the capacity of Room {i}: "))
        rooms.append(Room(i, capacity))

    courses = []
    for i in range(1, num_courses + 1):
        name = input(f"Enter the name of course {i}: ")
        duration = int(input(f"Enter the duration of course {name}: "))
        professor = input(f"Enter the professor for course {name}: ")
        students_enrolled = int(input(f"Enter the number of students enrolled for course {name}: "))
        courses.append(Course(name, duration, professor, students_enrolled))

    initial_timetable = generate_initial_timetable(courses, rooms, num_timeslots)
    assign_timeslots(initial_timetable)
    return initial_timetable


def prompt_for_timeslot(course_name):
    new_timeslot_str = simpledialog.askstring("Input", f"Enter the new timeslot for {course_name} (e.g., 2, 3): ")
    try:
        new_timeslot = tuple(map(int, new_timeslot_str.split(',')))
        return new_timeslot
    except ValueError:
        messagebox.showerror("Error", "Invalid input. Please enter timeslot as comma-separated integers.")
        return prompt_for_timeslot(course_name)


def check_conflict(course, new_timeslot, timetable):
    # Check if the new timeslot has enough slots for the duration of the course
    if new_timeslot[0] + course.duration > timetable.num_timeslots + 1:
        messagebox.showerror("Error", "Invalid timeslot. Not enough slots for the duration of the course.")
        return True

    consecutive_slots = [(new_timeslot[0] + i, new_timeslot[1]) for i in range(course.duration)]
    assigned_slots = [(ts[0], ts[1]) for other_course in timetable.courses for ts in other_course.timeslots if ts is not None]

    return any(slot in assigned_slots for slot in consecutive_slots)



if _name_ == "_main_":
    initial_timetable = create_timetable()
    display_timetable(initial_timetable)
    messagebox.showinfo("Finished", "Timetable generation completed.")
