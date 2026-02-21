import tkinter as tk
from tkinter import simpledialog
from PIL import Image, ImageTk
import cv2
import numpy as np

from engine.embedder import get_embedding
from engine.recognizer import recognize
from engine.database import add_person, remove_person, list_people

CAM_INDEX = 1
SAMPLES_REQUIRED = 20

class BiometricApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Biometric Face Recognition System")
        self.root.geometry("900x720")
        self.root.configure(bg="#1e1e1e")

        # ---------- TITLE ----------
        tk.Label(root, text="Face Recognition Terminal",
                 font=("Segoe UI",20,"bold"),
                 fg="white", bg="#1e1e1e").pack(pady=10)

        # ---------- VIDEO ----------
        self.video_container = tk.Frame(root, width=800, height=520, bg="black")
        self.video_container.pack(pady=10)
        self.video_container.pack_propagate(False)

        self.video_label = tk.Label(self.video_container, bg="black")
        self.video_label.pack(expand=True)

        # ---------- BUTTONS ----------
        btn_frame = tk.Frame(root, bg="#1e1e1e")
        btn_frame.pack(pady=10)

        self.start_btn = tk.Button(btn_frame,text="Start Recognition",
                                   command=self.start_camera,
                                   width=16,bg="#007acc",fg="white",
                                   font=("Segoe UI",11,"bold"))
        self.start_btn.grid(row=0,column=0,padx=6)

        self.stop_btn = tk.Button(btn_frame,text="Stop",
                                  command=self.stop_camera,
                                  width=16,bg="#444444",fg="white",
                                  font=("Segoe UI",11,"bold"))
        self.stop_btn.grid(row=0,column=1,padx=6)

        self.enroll_btn = tk.Button(btn_frame,text="Enroll Person",
                                    command=self.start_enroll,
                                    width=16,bg="#28a745",fg="white",
                                    font=("Segoe UI",11,"bold"))
        self.enroll_btn.grid(row=0,column=2,padx=6)

        self.manage_btn = tk.Button(btn_frame,text="Manage Users",
                                    command=self.open_manager,
                                    width=16,bg="#aa7733",fg="white",
                                    font=("Segoe UI",11,"bold"))
        self.manage_btn.grid(row=0,column=3,padx=6)

        # ---------- STATUS ----------
        self.status = tk.Label(root,text="Idle",
                               bg="#2d2d2d",fg="white",
                               anchor="w",font=("Segoe UI",10))
        self.status.pack(fill="x",side="bottom")

        # ---------- CAMERA ----------
        self.cap = cv2.VideoCapture(CAM_INDEX, cv2.CAP_DSHOW)
        self.running = False

        # recognition memory
        self.frame_count = 0
        self.last_box = None
        self.last_label = "Unknown"
        self.last_color = (0,0,255)

        # enrollment state
        self.enrolling = False
        self.enroll_name = ""
        self.enroll_embeddings = []

    # ---------- CAMERA CONTROL ----------
    def start_camera(self):
        if not self.running:
            self.running = True
            self.status.config(text="Recognition running...")
            self.update_frame()

    def stop_camera(self):
        self.running = False
        self.status.config(text="Stopped")

    # ---------- ENROLL ----------
    def start_enroll(self):
        if not self.running:
            self.start_camera()

        name = simpledialog.askstring("Enrollment","Enter person's name:")
        if not name:
            return

        self.enrolling = True
        self.enroll_name = name
        self.enroll_embeddings = []
        self.status.config(text=f"Enrolling {name}... Look at camera")

    # ---------- USER MANAGER ----------
    def open_manager(self):
        win = tk.Toplevel(self.root)
        win.title("User Manager")
        win.geometry("300x400")
        win.configure(bg="#1e1e1e")

        tk.Label(win,text="Registered People",
                 bg="#1e1e1e",fg="white",
                 font=("Segoe UI",12,"bold")).pack(pady=10)

        listbox = tk.Listbox(win,font=("Segoe UI",11))
        listbox.pack(fill="both",expand=True,padx=10,pady=10)

        def refresh():
            listbox.delete(0,tk.END)
            for person in list_people():
                listbox.insert(tk.END,person)

        def delete_selected():
            sel = listbox.curselection()
            if not sel:
                return
            name = listbox.get(sel[0])
            remove_person(name)
            refresh()

        btn_frame=tk.Frame(win,bg="#1e1e1e")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame,text="Delete Selected",
                  command=delete_selected,
                  bg="#cc4444",fg="white").grid(row=0,column=0,padx=5)

        tk.Button(btn_frame,text="Refresh",
                  command=refresh,
                  bg="#444444",fg="white").grid(row=0,column=1,padx=5)

        refresh()

    # ---------- MAIN LOOP ----------
    def update_frame(self):
        if not self.running:
            return

        ret, frame = self.cap.read()
        if not ret:
            self.root.after(10,self.update_frame)
            return

        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        frame = cv2.flip(frame,1)

        # ================= ENROLLMENT MODE =================
        if self.enrolling:

            embedding, box = get_embedding(frame)

            if embedding is not None:
                self.enroll_embeddings.append(embedding)
                self.status.config(
                    text=f"Capturing {self.enroll_name}: {len(self.enroll_embeddings)}/{SAMPLES_REQUIRED}"
                )

            if box is not None:
                x,y,w,h = box
                cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,255),2)
                cv2.putText(frame,"ENROLLING",(x,y-10),
                            cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,255),2)

            if len(self.enroll_embeddings) >= SAMPLES_REQUIRED:
                avg_embedding = np.mean(self.enroll_embeddings, axis=0)
                add_person(self.enroll_name, avg_embedding, len(self.enroll_embeddings))
                self.enrolling = False
                self.status.config(text=f"{self.enroll_name} enrolled successfully!")

        # ================= RECOGNITION MODE =================
        else:
            self.frame_count += 1

            if self.frame_count % 15 == 0:
                embedding, box = get_embedding(frame)

                label = "Unknown"
                color = (0,0,255)

                if embedding is not None:
                    state,name,conf = recognize(embedding)
                    if state == "CONFIRMED":
                        label = f"{name} ({conf:.2f})"
                        color = (0,200,0)

                self.last_label = label
                self.last_box = box
                self.last_color = color

            if self.last_box is not None:
                x,y,w,h = self.last_box
                cv2.rectangle(frame,(x,y),(x+w,y+h),self.last_color,2)
                cv2.putText(frame,self.last_label,(x,y-10),
                            cv2.FONT_HERSHEY_SIMPLEX,0.7,self.last_color,2)

        # ================= DISPLAY =================
        max_w, max_h = 800, 520
        h,w = frame.shape[:2]
        scale = min(max_w/w, max_h/h)
        new_w,new_h = int(w*scale),int(h*scale)
        frame = cv2.resize(frame,(new_w,new_h))

        rgb = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)
        imgtk = ImageTk.PhotoImage(img)

        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)

        self.root.after(10,self.update_frame)


root=tk.Tk()
app=BiometricApp(root)
root.mainloop()
