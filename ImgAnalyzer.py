import tkinter as tk

class DragDropWidget(tk.Canvas):
    def __init__(self, master, width, height):
        super().__init__(master, width=width, height=height)
        self.bind("<Button-1>", self.drag_start)

    def drag_start(self, event):
        self.drag_data = {"x": event.x, "y": event.y}

        # Initiate drag and drop operation
        self.configure(cursor="move")
        self.bind("<B1-Motion>", self.drag_motion)
        self.bind("<ButtonRelease-1>", self.drag_drop)

    def drag_motion(self, event):
        # Update the drag and drop operation
        x, y = event.x, event.y
        self.move(tk.CURRENT, x - self.drag_data["x"], y - self.drag_data["y"])
        self.drag_data["x"], self.drag_data["y"] = x, y

    def drag_drop(self, event):
        # End the drag and drop operation
        self.configure(cursor="")
        self.unbind("<B1-Motion>")
        self.unbind("<ButtonRelease-1>")
        self.master.drag_drop_handler(self)

class DropTargetWidget(tk.Label):
    def __init__(self, master):
        super().__init__(master, text="Drop items here", font=("Arial", 16),
                         width=20, height=5, bg="white", bd=2, relief=tk.SUNKEN)
        self.pack(fill=tk.BOTH, expand=True)
        self.bind("DragEnter", self.drag_enter)
        self.bind("DragLeave", self.drag_leave)
        self.bind("DragOver", self.drag_over)
        self.bind("Drop", self.drop)

    def drag_enter(self, event):
        # Highlight the drop target when an item is dragged over it
        self.configure(bg="light blue")

    def drag_leave(self, event):
        # Remove the highlight when the item is dragged away from the drop target
        self.configure(bg="white")

    def drag_over(self, event):
        # Allow the item to be dropped onto the drop target
        event.action = tk.DND_ACTION_COPY
        tk.dnd.status(tk.DND_STATUS_COPY)

    def drop(self, event):
        # Handle the dropped item
        self.configure(bg="white")
        item = event.data.strip()
        self.master.add_item_to_queue(item)

class QueueListbox(tk.Listbox):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

    def add_item(self, item):
        # Add an item to the listbox
        self.insert(tk.END, item)

    def get_items(self):
        # Get all the items in the listbox
        return self.get(0, tk.END)

class MainWindow(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()

        # Create a drag and drop widget
        self.drag_drop_widget = DragDropWidget(self, width=200, height=200)
        self.drag_drop_widget.create_rectangle(50, 50, 150, 150, fill="red")

        # Create a drop target widget
        self.drop_target_widget = DropTargetWidget(self)

        # Create a queue listbox
        self.queue_listbox = QueueListbox(self)
        self.queue_listbox.pack(fill=tk.BOTH, expand=True)

        # Create a play button
        # self.play_button = tk.Button(self, text="Play", command=self.process_queue)
        self

def main():
    root = tk.Tk()
    root.geometry("400x400")
    root.title("Drag and Drop Example")

    # Create the main window
    main_window = MainWindow(root)

    # Start the main event loop
    root.mainloop()

if __name__ == '__main__':
    main()