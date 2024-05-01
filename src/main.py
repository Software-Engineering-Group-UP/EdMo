import tkinter as tk
from PIL import ImageTk, Image
import modifiedTransitions as MT
from tkinter import filedialog as fd
from aux_functions import read_xml
from mc_algorithm import *


class mcGUI(object):

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Modelchecker")
        self.root.config(bg="darkgrey")

        self.root.columnconfigure(index=0,weight=1)
        self.root.columnconfigure(index=1,weight=3)
        self.root.rowconfigure(index=[0,1],weight=1)

        # create top menu
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Import", command=self.import_kts)
        filemenu.add_command(label="Save")
        filemenu.add_command(label="Load")
        menubar.add_cascade(label="File", menu=filemenu)

        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About")
        menubar.add_cascade(label="Help", menu=helpmenu)

        # initialize kripke transition system
        self.states = []
        self.transitions = []
        self.kts = MT.KTS_model()
        self.machine = MT.KTS(model=self.kts, title="", show_state_attributes=True)

        # frame for atomic propositions
        self.create_ap_frame()
        self.ap_frame.grid(column=0,row=0,sticky="nsew", padx=5, pady=5)

        # frame for CTL Formulas
        self.create_ctl_frame()
        self.ctl_frame.grid(column=0,row=1,sticky="nsew", padx=5, pady=5)

        # frame for displaying the graph
        self.create_graph_frame()
        self.graph_frame.grid(column=1,row=0,rowspan=2, sticky="nsew", padx=5, pady=5)

        self.root.mainloop()

    def create_ap_frame(self):
        self.ap_frame = tk.Frame(self.root, width=450, height=250)
        self.ap_frame.grid_propagate(0)

        rows_count = list(range(4+3)) # initially 3 empty rows of the AP table are loaded

        self.ap_frame.columnconfigure(index=[0,1],weight=1)
        self.ap_frame.rowconfigure(index=rows_count,weight=2)

        ap_headline = tk.Label(self.ap_frame, text="Manage APs", borderwidth=2, relief="groove")
        ap_headline.grid(column=0,row=0,columnspan=2,sticky="nsew")

        self.editAP_button = tk.Button(master=self.ap_frame, text="Edit", command=self.editAP)
        self.editAP_button.grid(column=0,row=1,sticky="nw")

        states_table = tk.Label(self.ap_frame, text="State", borderwidth=1, relief="solid")
        states_table.grid(column=0,row=2,sticky="nsew")

        ap_table = tk.Label(self.ap_frame, text="Atomic Proposition", borderwidth=1, relief="solid")
        ap_table.grid(column=1,row=2,sticky="nsew")

        self.ap_labels = []
        self.ap_entrys = []
        self.state_labels = []
        state_count = 0

        for s in range(4): # see update_ap_frame()
            state_label = tk.Label(self.ap_frame, text="", borderwidth=1, relief="solid")
            state_label.grid(column=0,row=3+state_count,sticky="nsew")

            self.ap_labels.append(tk.Label(self.ap_frame, text="", borderwidth=1, relief="solid"))
            self.ap_labels[state_count].grid(column=1,row=3+state_count,sticky="nsew")

            state_count += 1

    def create_ctl_frame(self):
        self.ctl_frame = tk.Frame(self.root, width=450, height=250)
        self.ctl_frame.grid_propagate(0)

        self.ctl_frame.columnconfigure(index=[0,1,2],weight=1)
        self.ctl_frame.columnconfigure(index=[0,1],minsize=166)
        self.ctl_frame.rowconfigure(index=[0,1,2,3,4],weight=2)

        ap_label = tk.Label(self.ctl_frame, text="Manage CTL-Formulas", borderwidth=2, relief="groove")
        ap_label.grid(column=0,row=0,columnspan=3,sticky="nsew")

        editCTL_button = tk.Button(master=self.ctl_frame, text="Edit")
        editCTL_button.grid(column=0,row=1,sticky="nw")

        self.description_button = tk.Button(master=self.ctl_frame, text="Description", command=self.showDescription)
        self.description_button.grid(column=0,row=1,sticky="ne")

        check_button = tk.Button(master=self.ctl_frame, text="Check", command=self.checkModel)
        check_button.grid(column=2,row=1,sticky="ne")

        self.ctl1bg = tk.Label(master=self.ctl_frame, height=2) # set background for checkboxes, colored when checked
        self.ctl1bg.grid(column=0,row=2,columnspan=3,sticky="ew")
        self.ctl2bg = tk.Label(master=self.ctl_frame, height=2)
        self.ctl2bg.grid(column=0,row=3,columnspan=3,sticky="ew")
        self.ctl3bg = tk.Label(master=self.ctl_frame, height=2)
        self.ctl3bg.grid(column=0,row=4,columnspan=3,sticky="ew")

        f1 = tk.IntVar()
        self.ctl1 = tk.Checkbutton(master=self.ctl_frame, text="AF(transferred)", variable=f1)
        self.ctl1.grid(column=0,row=2,columnspan=2,sticky="w")

        f2 = tk.IntVar()
        self.ctl2 = tk.Checkbutton(master=self.ctl_frame, text="AG(l_in)", variable=f2)
        self.ctl2.grid(column=0,row=3,columnspan=2,sticky="w")

        f3 = tk.IntVar()
        self.ctl3 = tk.Checkbutton(master=self.ctl_frame, text="EU(l_in,l_out)", variable=f3)
        self.ctl3.grid(column=0,row=4,columnspan=2,sticky="w")

        self.s1 = tk.Label(self.ctl_frame, text="[All]")
        self.s1.grid(column=2,row=2,sticky="w")

        self.s2 = tk.Label(self.ctl_frame, text="[Login]")
        self.s2.grid(column=2,row=3,sticky="w")

        self.s3 = tk.Label(self.ctl_frame, text="[Finance Overview]")
        self.s3.grid(column=2,row=4,sticky="w")

    def create_graph_frame(self):
        self.graph_frame = tk.Frame(self.root, height=500, width=1000)
        self.graph_frame.grid_propagate(0)

        self.graph_frame.columnconfigure(index=[0],weight=1)
        self.graph_frame.rowconfigure(index=[0,1],weight=2)

        graph_label = tk.Label(self.graph_frame, text="Model", borderwidth=2, relief="groove")
        graph_label.grid(column=0,row=0,sticky="nsew")

        self.graph_display = tk.Label(self.graph_frame, text="no diagram loaded", height=29)
        self.graph_display.grid(column=0,row=1,sticky="nsew")

    def import_kts(self):
        diagramPath = fd.askopenfilename(title='Select a State Machine Diagram', initialdir='./examples', filetypes=[('XML files', '*.xml')])

        self.states, self.transitions = read_xml(diagramPath)

        self.kts = MT.KTS_model()
        self.machine = MT.KTS(model=self.kts, title="", initial=list(self.states[0].values())[0], states=self.states, transitions=self.transitions, show_state_attributes=True)
        self.machine.generate_image(self.kts)
        self.update_image()
        self.clear_aplabels() # clear any existing labels of the table
        self.clear_statelabels()
        self.clear_apentrys()
        self.update_ap_frame()
        
    def update_image(self):
        img = Image.open("src/kts.png")
        width, height = img.size
        resized_img = img.resize((950,int(height*(950/width))))
        self.graph_image = ImageTk.PhotoImage(resized_img)
        self.graph_display = tk.Label(self.graph_frame, image=self.graph_image, height=250)
        self.graph_display.image = self.graph_image
        self.graph_display.grid(column=0,row=1,sticky="nsew")

    def update_ap_frame(self):
        rows_count = list(range(len(self.machine.states.items())+3))
        self.ap_frame.rowconfigure(index=rows_count,weight=2)

        state_count = 0

        for s in self.machine.states.items():
            current_name = s[0]
            self.state_labels.append(tk.Label(self.ap_frame, text=f"{current_name}", borderwidth=1, relief="solid"))
            self.state_labels[state_count].grid(column=0,row=3+state_count,sticky="nsew")

            current_ap = s[1].tags
            ap_tags = ', '.join(current_ap)
            self.ap_labels.append(tk.Label(self.ap_frame, text=ap_tags, borderwidth=1, relief="solid"))
            self.ap_labels[state_count].grid(column=1,row=3+state_count,sticky="nsew")

            state_count += 1

    def clear_aplabels(self):
        for i in range(len(self.ap_labels)):
            self.ap_labels[i].destroy
        
        self.ap_labels.clear()

    def clear_statelabels(self):
        for i in range(len(self.state_labels)):
            self.state_labels[i].destroy
        
        self.state_labels.clear()

    def clear_apentrys(self):
        for i in range(len(self.ap_entrys)):
            self.ap_entrys[i].destroy
        
        self.ap_entrys.clear()

    def editAP(self):
        self.editAP_button.destroy()
        self.doneAP_button = tk.Button(master=self.ap_frame, text="Done", command=self.doneAP)
        self.doneAP_button.grid(column=0,row=1,sticky="nw")

        state_count = 0

        self.clear_aplabels()

        for s in self.machine.states.items():
            ap_tags = ""

            if s[1].tags != []:
                current_ap = s[1].tags
                ap_tags = ','.join(current_ap)

            self.ap_entrys.append(tk.Entry(self.ap_frame, borderwidth=1, relief="solid"))
            self.ap_entrys[state_count].insert(10,ap_tags)
            self.ap_entrys[state_count].grid(column=1,row=3+state_count,sticky="nsew")

            state_count += 1


    def doneAP(self):
        self.doneAP_button.destroy()
        self.editAP_button = tk.Button(master=self.ap_frame, text="Edit", command=self.editAP)
        self.editAP_button.grid(column=0,row=1,sticky="nw")

        state_count = 0

        for s in self.states:
            current_ap = self.ap_entrys[state_count].get()
            self.ap_entrys[state_count].destroy()
            self.ap_labels.append(tk.Label(self.ap_frame, text=current_ap, borderwidth=1, relief="solid"))
            self.ap_labels[state_count].grid(column=1,row=3+state_count,sticky="nsew")

            s['tags'] = current_ap.split(",")

            state_count += 1

        self.clear_apentrys()
        self.kts = MT.KTS_model()
        self.machine = MT.KTS(model=self.kts, title="", initial=list(self.states[0].values())[0], states=self.states, transitions=self.transitions, show_state_attributes=True)
        self.machine.generate_image(self.kts)
        self.update_image()

    def showDescription(self):
        self.description_button.destroy()
        self.formula_button = tk.Button(master=self.ctl_frame, text="Formula", command=self.showFormula)
        self.formula_button.grid(column=0,row=1,sticky="ne")

        self.ctl1.config(text="eventually money must have been transferred")
        self.ctl2.config(text="the user must always be logged in")
        self.ctl3.config(text="the user must be logged in until they are logged out")

    def showFormula(self):
        self.formula_button.destroy()
        self.description_button = tk.Button(master=self.ctl_frame, text="Description", command=self.showDescription)
        self.description_button.grid(column=0,row=1,sticky="ne")

        self.ctl1.config(text="AF(transferred)")
        self.ctl2.config(text="AG(l_in)")
        self.ctl3.config(text="EU(l_in,l_out)")

    def checkModel(self):
        # to visualize what checking could look like, actual model checking algorithm not yet implemented
        for s in self.states:
            if s["name"] != "Login":
                self.machine.model_graphs[id(self.kts)].set_node_style(s["name"], 'sat')
            else:
                self.machine.model_graphs[id(self.kts)].set_node_style(s["name"], 'unsat')

        self.machine.generate_image(self.kts)
        self.update_image()

        self.ctl1.config(bg="lightgreen")
        self.ctl2.config(bg="darksalmon")
        self.ctl3.config(bg="lightgreen")

        self.s1.config(bg="lightgreen")
        self.s2.config(bg="darksalmon")
        self.s3.config(bg="lightgreen")

        self.ctl1bg.config(bg="lightgreen")
        self.ctl2bg.config(bg="darksalmon")
        self.ctl3bg.config(bg="lightgreen")


if __name__ == "__main__":
    gui = mcGUI()