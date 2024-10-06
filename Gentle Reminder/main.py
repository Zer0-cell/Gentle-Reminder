import tkinter as tk
from tkinter import messagebox
from plyer import notification
import threading
import time
import json
from datetime import datetime

# File to store tasks
TASK_FILE = 'tasks.json'


# Function to load tasks from a file
def load_tasks():
    try:
        with open(TASK_FILE, 'r') as file:
            tasks = json.load(file)
    except FileNotFoundError:
        tasks = []
    return tasks


# Function to save tasks to a file
def save_tasks(tasks):
    with open(TASK_FILE, 'w') as file:
        json.dump(tasks, file)


# Function to send notifications
def send_notification(task_name):
    notification.notify(
        title="Gentle Reminder",
        message=f"Task: {task_name}",
        timeout=10
    )


# Function to convert 12-hour format to 24-hour format
def convert_to_24_hour(time_str):
    try:
        return datetime.strptime(time_str, "%I:%M %p").strftime("%H:%M")
    except ValueError:
        messagebox.showerror("Invalid Time", "Please enter time in HH:MM AM/PM format.")
        return None


# Function to check reminders
def reminder_check():
    while True:
        tasks = load_tasks()
        current_time = time.strftime("%H:%M")
        for task in tasks:
            if task['time'] == current_time:
                send_notification(task['name'])
                tasks.remove(task)
                save_tasks(tasks)
        time.sleep(60)


# Function to add a new task from the input fields
def add_task_from_input():
    task_name = task_name_entry.get()
    task_time = task_time_entry.get()

    if task_name and task_time:
        converted_time = convert_to_24_hour(task_time)
        if converted_time:
            task = {'name': task_name, 'time': converted_time}
            tasks = load_tasks()
            tasks.append(task)
            save_tasks(tasks)
            update_task_list()
            task_name_entry.delete(0, tk.END)  # Clear input field
            task_time_entry.delete(0, tk.END)  # Clear input field
        else:
            messagebox.showerror("Error", "Invalid time format")
    else:
        messagebox.showwarning("Missing Input", "Please enter both task name and time")


# Function to edit a task
def edit_task():
    selected_task = task_listbox.curselection()
    if selected_task:
        task_index = selected_task[0]
        tasks = load_tasks()

        task_name_entry.delete(0, tk.END)
        task_time_entry.delete(0, tk.END)

        task_name_entry.insert(0, tasks[task_index]['name'])
        task_time_entry.insert(0, tasks[task_index]['time'])

        def save_edited_task():
            new_task_name = task_name_entry.get()
            new_task_time = task_time_entry.get()
            converted_time = convert_to_24_hour(new_task_time)

            if new_task_name and converted_time:
                tasks[task_index] = {'name': new_task_name, 'time': converted_time}
                save_tasks(tasks)
                update_task_list()
                task_name_entry.delete(0, tk.END)  # Clear input field
                task_time_entry.delete(0, tk.END)  # Clear input field
            else:
                messagebox.showwarning("Invalid Input", "Please enter valid task details")

        save_button.config(text="Save", command=save_edited_task)
    else:
        messagebox.showwarning("No selection", "Please select a task to edit.")


def delete_task():
    selected_task = task_listbox.curselection()
    tasks = load_tasks()

    if selected_task:
        task_index = selected_task[0]

        if 0 <= task_index < len(tasks):  # Ensure the index is within range
            print(f"Attempting to delete task at index {task_index}: {tasks[task_index]}")  # Debug print
            del tasks[task_index]
            save_tasks(tasks)
            update_task_list()
        else:
            print(f"Error: Task index {task_index} is out of range. Tasks list length: {len(tasks)}")
            messagebox.showwarning("Error", "Task index is out of range.")
    else:
        print("No task selected for deletion")  # Debug print
        messagebox.showwarning("No selection", "Please select a task to delete.")


# Function to update the task list display
def update_task_list():
    task_listbox.delete(0, tk.END)
    tasks = load_tasks()
    for task in tasks:
        task_listbox.insert(tk.END, f"{task['name']} at {task['time']}")


# Create the main window
root = tk.Tk()
root.title("Gentle Reminder")
root.geometry("500x400")

# Set the background color of the window to black
root.config(bg="black")

# Task input section
input_frame = tk.Frame(root, bg="black")
input_frame.pack(pady=20)

tk.Label(input_frame, text="Task Name:", bg="black", fg="white").grid(row=0, column=0, padx=5, pady=5)
task_name_entry = tk.Entry(input_frame, width=30)
task_name_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(input_frame, text="Task Time (HH:MM AM/PM):", bg="black", fg="white").grid(row=1, column=0, padx=5, pady=5)
task_time_entry = tk.Entry(input_frame, width=30)
task_time_entry.grid(row=1, column=1, padx=5, pady=5)

# Add Task Button with specified color
save_button = tk.Button(input_frame, text="Add Task", command=add_task_from_input, bg="lime", fg="black")
save_button.grid(row=2, columnspan=2, pady=10)

# Task listbox with white text on black background
task_listbox = tk.Listbox(root, width=50, height=10, bg="black", fg="white")
task_listbox.pack(pady=10)

# Edit and Delete buttons with specified colors
button_frame = tk.Frame(root, bg="black")
button_frame.pack(pady=10)

edit_button = tk.Button(button_frame, text="Edit Task", command=edit_task, width=15, bg="yellow", fg="black")
edit_button.grid(row=0, column=0, padx=5)

delete_button = tk.Button(button_frame, text="Delete Task", command=delete_task, width=15, bg="red", fg="white")
delete_button.grid(row=0, column=1, padx=5)

# Load tasks and start reminder thread
update_task_list()
threading.Thread(target=reminder_check, daemon=True).start()

# Start the Tkinter event loop
root.mainloop()
