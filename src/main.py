import tkinter as tk
from PIL import ImageTk, Image
import modifiedTransitions as MT
from tkinter import filedialog as fd
from aux_functions import read_xml, is_hierarchical
from mc_algorithm import *
import json


class mcGUI(object):

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("EdMo")
        self.root.config(bg="darkgrey")

        self.window_width= self.root.winfo_screenwidth()
        self.window_height = self.root.winfo_screenheight()
        self.root.geometry(f"{self.window_width}x{self.window_height}")

        self.root.columnconfigure(index=0,weight=1)
        self.root.columnconfigure(index=1,weight=3)
        self.root.rowconfigure(index=[0,1],weight=1)

        # create top menu
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        filemenu = tk.Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="Import", command=self.import_kts)
        filemenu.add_command(label="Save as", command=self.save_as)
        filemenu.add_command(label="Save", command=self.save_progress)
        filemenu.add_command(label="Load", command=self.load)
        self.menubar.add_cascade(label="File", menu=filemenu)

        self.saveasPath = ''

        helpmenu = tk.Menu(self.menubar, tearoff=0)
        helpmenu.add_command(label="About")
        self.menubar.add_cascade(label="Help", menu=helpmenu)

        layoutmenu = tk.Menu(self.menubar, tearoff=0)
        layoutmenu.add_command(label="LeftRight", command= lambda: self.change_layout("LR"))
        layoutmenu.add_command(label="TopBottom", command= lambda: self.change_layout("TB"))
        self.menubar.add_cascade(label="Layout", menu=layoutmenu)
        self.menubar.entryconfig("Layout", state="disabled")

        # initialize kripke transition system
        self.states = []
        self.transitions = []
        self.kts = MT.GraphKTS_model()
        self.machine = MT.GraphKTS(model=self.kts, title="", show_state_attributes=True)

        self.ctlFormulas = []

        # frame for atomic propositions
        self.create_ap_frame()
        self.ap_frame.grid(column=0,row=0,sticky="nsew", padx=5, pady=5)

        # frame for CTL Formulas
        self.create_ctl_frame()
        self.ctl_frame.grid(column=0,row=1,sticky="nsew", padx=5, pady=5)

        # frame for displaying the graph
        self.original_image = None
        self.create_graph_frame()
        self.graph_frame.grid(column=1,row=0,rowspan=2, sticky="nsew", padx=5, pady=5)

        self.root.state('zoomed')

        self.root.mainloop()


    def create_ap_frame(self):
        w = int(self.window_width/3)
        h = int(self.window_height/2)
        self.ap_frame = tk.Frame(self.root, width=w, height=h)

        self.ap_frame.columnconfigure(index=[0,1], weight=1)
        self.ap_frame.rowconfigure(index=[0,1,2], weight=1)
        self.ap_frame.rowconfigure(index=[0,1], minsize=25)

        ap_headline = tk.Label(self.ap_frame, text="Manage APs", borderwidth=2, relief="groove")
        ap_headline.grid(column=0,row=0,columnspan=2,sticky="nsew")

        self.editAP_button = tk.Button(master=self.ap_frame, text="Edit", command=self.editAP)
        self.editAP_button.grid(column=0,row=1,sticky="nw")

        self.ap_canvas = tk.Canvas(self.ap_frame, width=w-20, height=int(h/1.5))
        self.ap_canvas.grid(column=0, row=2, columnspan=2, sticky="nws")

        self.table_frame = tk.Frame(self.ap_canvas)
        self.ap_canvas.create_window((0,0), window=self.table_frame, anchor="nw", tags="table_frame")

        self.ap_scrollbar = tk.Scrollbar(self.ap_frame, orient="vertical", command=self.ap_canvas.yview)
        self.ap_scrollbar.grid(column=1, row=2, sticky="nse")

        states_table = tk.Label(self.table_frame, text="State", borderwidth=1, relief="solid")
        states_table.grid(column=0,row=0,sticky="nsew")

        ap_table = tk.Label(self.table_frame, text="Atomic Proposition", borderwidth=1, relief="solid")
        ap_table.grid(column=1,row=0,sticky="nsew")

        self.ap_labels = []
        self.ap_entrys = []
        self.state_labels = []
        state_count = 0

        for s in range(5): # see update_ap_frame()
            self.state_labels.append(tk.Label(self.table_frame, text="", borderwidth=1, relief="solid"))
            self.state_labels[state_count].grid(column=0,row=1+state_count,sticky="nsew")

            self.ap_labels.append(tk.Label(self.table_frame, text="", borderwidth=1, relief="solid"))
            self.ap_labels[state_count].grid(column=1,row=1+state_count,sticky="nsew")

            state_count += 1
        
        row_count = self.table_frame.grid_size()[1]
        self.table_frame.columnconfigure(index=[0,1], minsize=int((w-40)/2))
        self.table_frame.rowconfigure(index=list(range(row_count)), minsize=25)

        self.table_frame.update_idletasks()
        self.ap_canvas.configure(yscrollcommand=self.ap_scrollbar.set, scrollregion=self.ap_canvas.bbox("all"))


    def create_ctl_frame(self):
        w = int(self.window_width/3)
        h = int(self.window_height/2)
        self.ctl_frame = tk.Frame(self.root, width=w, height=h)

        self.ctl_frame.columnconfigure(index=[0,1,2,3,4],weight=1)
        self.ctl_frame.columnconfigure(index=[0,1,2,3],minsize=int(w/5))
        self.ctl_frame.rowconfigure(index=[0,1,2,3],weight=2)
        self.ctl_frame.rowconfigure(index=[0,1], minsize=25)

        ctl_label = tk.Label(self.ctl_frame, text="Manage CTL-Formulas", borderwidth=2, relief="groove")
        ctl_label.grid(column=0,row=0,columnspan=5,sticky="nsew")

        self.defaultbg = ctl_label.cget('bg')

        addCTL_button = tk.Button(master=self.ctl_frame, text="Add", command=lambda: self.openCTLwindow())
        addCTL_button.grid(column=0,row=1,sticky="nw")

        editCTL_button = tk.Button(master=self.ctl_frame, text="Edit", command=self.openEditWindow)
        editCTL_button.grid(column=1, row=1, sticky="nw")

        self.delete_button = tk.Button(master=self.ctl_frame, text="Delete", command=self.openDelWindow)
        self.delete_button.grid(column=2,row=1,sticky="nw")

        self.description_button = tk.Button(master=self.ctl_frame, text="Description", command=self.showDescription)
        self.description_button.grid(column=3,row=1,sticky="nw")

        check_button = tk.Button(master=self.ctl_frame, text="Check", command=self.checkModel)
        check_button.grid(column=4,row=1,sticky="ne")

        self.formula_canvas = tk.Canvas(self.ctl_frame, width=w-50, height=int(h/1.5))
        self.formula_canvas.grid(column=0, row=2, columnspan=4, sticky="nws")

        self.formula_frame = tk.Frame(self.formula_canvas)
        self.formula_canvas.create_window((0,0), window=self.formula_frame, anchor="nw", tags="formula_frame")

        self.formula_frame.columnconfigure(index=[1], minsize=400)

        self.formula_scrollbar = tk.Scrollbar(self.ctl_frame, orient="vertical", command=self.formula_canvas.yview)
        self.formula_scrollbar.grid(column=4, row=2, sticky="nse")

        self.formula_frame.update_idletasks()
        self.formula_canvas.configure(yscrollcommand=self.formula_scrollbar.set, scrollregion=self.formula_canvas.bbox("all"))

        self.number_formulas = 0
        self.ctl_Checkboxes = []
        self.ctl_states = []
        self.check_results = []
        self.ctl_backgrounds = []


    def create_graph_frame(self):
        w = int(2*self.window_width/3)
        h = self.window_height
        self.graph_frame = tk.Frame(self.root, height=h, width=w)

        self.graph_frame.columnconfigure(index=[0],weight=1)
        self.graph_frame.rowconfigure(index=[0,1,2],weight=2)
        self.graph_frame.rowconfigure(index=[0,1], minsize=25)

        graph_label = tk.Label(self.graph_frame, text="Model", borderwidth=2, relief="groove")
        graph_label.grid(column=0,row=0,sticky="nsew")

        button_frame = tk.Frame(self.graph_frame)
        button_frame.grid(column=0, row=1, sticky="we")

        zoomIN_button = tk.Button(button_frame, text="+", command=lambda: self.zoom(zoom_value=1))
        zoomIN_button.pack(side="left")

        zoomOUT_button = tk.Button(button_frame, text="-", command=lambda: self.zoom(zoom_value=-1))
        zoomOUT_button.pack(side="left")

        reset_button = tk.Button(button_frame, text="Reset", command=self.reset_markings)
        reset_button.pack(side="right")

        self.graph_canvas = tk.Canvas(self.graph_frame, width=w, height=int(h/1.25))
        self.graph_canvas.grid(column=0,row=2,sticky="nw")

        self.graph_canvas.bind('<ButtonPress-1>', self.move_from)
        self.graph_canvas.bind('<B1-Motion>', self.move_to)

        self.graph_canvas.bind('<MouseWheel>', self.zoom) # windows, MacOS
        self.graph_canvas.bind('<Button-4>', self.zoom) # Linux
        self.graph_canvas.bind('<Button-5>', self.zoom)


    def import_kts(self):

        diagramPath = fd.askopenfilename(title='Select a State Machine Diagram', initialdir='./examples', filetypes=[('XML files', '*.xml')])

        try:
            self.states, self.transitions = read_xml(diagramPath)
        except FileNotFoundError:
            return

        self.clear_aplabels()
        self.clear_statelabels()
        self.clear_apentrys()
        self.clear_ctl_frame()

        self.ctlFormulas.clear()

        self.kts = MT.GraphKTS_model()
        if is_hierarchical(self.states):
            self.machine = MT.HierarchicalKTS(model=self.kts, title="", initial=list(self.states[0].values())[0], states=self.states,
                                transitions=self.transitions, show_state_attributes=True)
        else:
            self.machine = MT.GraphKTS(model=self.kts, title="", initial=list(self.states[0].values())[0], states=self.states,
                                transitions=self.transitions, show_state_attributes=True)
            
        self.menubar.entryconfig("Layout", state="normal")
        self.machine.generate_image(self.kts)
        self.set_new_image()
        self.update_ap_frame()
        self.update_ctl_frame()

        self.saveasPath = ''
        self.root.title(f"EdMo")

        self.table_frame.update_idletasks()
        self.ap_canvas.configure(yscrollcommand=self.ap_scrollbar.set, scrollregion=self.ap_canvas.bbox("all"))


    def set_new_image(self):
        self.original_image = Image.open("src/kts.png")
        self.image = self.original_image
        self.original_width, self.original_height = self.image.size
        if self.original_width > self.original_height:
            self.width = self.graph_canvas.winfo_width()
            self.height = int(self.original_height * self.width // self.original_width)
        else:
            self.height = self.graph_canvas.winfo_height()
            self.width = int(self.original_width * self.height // self.original_height)
        self.image = self.original_image.resize((self.width, self.height))
        self.graph_image = ImageTk.PhotoImage(self.image)
        self.graph_canvas.create_image(500, 225, image=self.graph_image, anchor="center")
        container_x = self.graph_canvas.winfo_width() // 2 - self.width // 2
        container_y = self.graph_canvas.winfo_height() // 2 - self.height // 2
        self.container = self.graph_canvas.create_rectangle(container_x, container_y, self.width, self.height, width=0)
        self.graph_canvas.configure(scrollregion=self.graph_canvas.bbox(self.container)) 


    def update_image(self):
        self.original_image = Image.open("src/kts.png")
        self.image = self.original_image
        self.original_width, self.original_height = self.image.size
        self.image = self.original_image.resize((self.width, self.height))
        self.graph_image = ImageTk.PhotoImage(self.image)
        self.graph_canvas.create_image(500, 225, image=self.graph_image, anchor="center")
        container_x = self.graph_canvas.winfo_width() // 2 - self.width // 2
        container_y = self.graph_canvas.winfo_height() // 2 - self.height // 2
        self.container = self.graph_canvas.create_rectangle(container_x, container_y, self.width, self.height, width=0)
        self.graph_canvas.configure(scrollregion=self.graph_canvas.bbox(self.container))

    
    def change_layout(self, direction):
        self.machine.get_graph().graph_attr.update({'rankdir': direction})
        self.machine.generate_image(self.kts)
        self.set_new_image()
        
    
    def reset_markings(self):
        if is_hierarchical(self.states):
            state_dicts = self.machine.get_unnested_dicts()
        else:
            state_dicts = self.states
        for s in state_dicts:
            self.machine.model_graphs[id(self.kts)].set_node_style(s['name'], 'default')

        self.machine.generate_image(self.kts)
        self.update_image()

        for i in range(len(self.ctlFormulas)):
            self.ctl_backgrounds[i].config(bg=self.defaultbg)
            self.ctl_Checkboxes[i].config(bg=self.defaultbg)
            self.ctl_states[i].config(bg=self.defaultbg)
            self.check_results[i].config(text='')
            
        self.formula_frame.update_idletasks()
        self.formula_canvas.configure(yscrollcommand=self.formula_scrollbar.set, scrollregion=self.formula_canvas.bbox("all"))

        
    def move_from(self, event):
        self.graph_canvas.scan_mark(event.x, event.y)


    def move_to(self, event):
        self.graph_canvas.scan_dragto(event.x, event.y, gain=1)
        self.update_image()

    
    def zoom(self, event=None, zoom_value=None):
        try:
            if event != None:
                if event.delta == -120 or event.delta == -1 or event.num == 5:
                    zoom_value=-1
                if event.delta == 120 or event.delta == 1 or event.num == 4:
                    zoom_value=1

            if zoom_value == -1:
                if self.width / self.original_width < 0.4: # boundary for zoom out
                    return
                self.width = int(self.width * 0.9)
                self.height = int(self.height * 0.9)
                self.image = self.original_image.resize((self.width, self.height))
            
            if zoom_value == 1:
                if self.width / self.original_width > 1.6: # boundary for zoom in
                    return
                self.width = int(self.width * 1.1)
                self.height = int(self.height * 1.1)
                self.image = self.original_image.resize((self.width, self.height))
            
            self.update_image()
        
        except AttributeError as e:
            if self.original_image:
                print(e)
            else:
                pass


    def update_ap_frame(self):
        self.clear_aplabels()
        self.clear_statelabels()
        self.clear_apentrys()

        state_dict = self.machine.get_all_states()

        state_count = 0

        for s in state_dict.items():
            current_name = s[0]
            self.state_labels.append(tk.Label(self.table_frame, text=f"{current_name}", borderwidth=1, relief="solid"))
            self.state_labels[state_count].grid(column=0,row=1+state_count,sticky="nsew")

            current_ap = s[1].tags
            ap_tags = ', '.join(current_ap)
            self.ap_labels.append(tk.Label(self.table_frame, text=ap_tags, borderwidth=1, relief="solid"))
            self.ap_labels[state_count].grid(column=1,row=1+state_count,sticky="nsew")

            state_count += 1

        row_count = self.table_frame.grid_size()[1]
        self.table_frame.rowconfigure(index=list(range(row_count)), minsize=25)

        self.table_frame.update_idletasks()
        self.ap_canvas.configure(yscrollcommand=self.ap_scrollbar.set, scrollregion=self.ap_canvas.bbox("all"))

    def clear_aplabels(self):
        for i in range(len(self.ap_labels)):
            self.ap_labels[i].destroy()
        
        self.ap_labels.clear()


    def clear_statelabels(self):
        for i in range(len(self.state_labels)):
            self.state_labels[i].destroy()
        
        self.state_labels.clear()


    def clear_apentrys(self):
        for i in range(len(self.ap_entrys)):
            self.ap_entrys[i].destroy()
        
        self.ap_entrys.clear()


    def editAP(self):
        self.editAP_button.destroy()
        self.doneAP_button = tk.Button(master=self.ap_frame, text="Done", command=self.doneAP)
        self.doneAP_button.grid(column=0,row=1,sticky="nw")

        state_count = 0

        self.clear_aplabels()

        state_dict = self.machine.get_all_states()

        for s in state_dict.items():
            ap_tags = ""

            if s[1].tags != []:
                current_ap = s[1].tags
                ap_tags = ', '.join(current_ap)

            self.ap_entrys.append(tk.Entry(self.table_frame, borderwidth=1, relief="solid"))
            self.ap_entrys[state_count].insert(10,ap_tags)
            self.ap_entrys[state_count].grid(column=1,row=1+state_count,sticky="nsew")

            state_count += 1


    def doneAP(self):
        self.doneAP_button.destroy()
        self.editAP_button = tk.Button(master=self.ap_frame, text="Edit", command=self.editAP)
        self.editAP_button.grid(column=0,row=1,sticky="nw")

        state_count = 0

        state_dict = self.machine.get_all_states()

        for s in state_dict.items():
            current_ap = self.ap_entrys[state_count].get()
            self.ap_entrys[state_count].destroy()
            self.ap_labels.append(tk.Label(self.table_frame, text=current_ap, borderwidth=1, relief="solid", wraplength=150))
            self.ap_labels[state_count].grid(column=1,row=1+state_count,sticky="nsew")

            s[1].tags = current_ap.split(", ")

            state_count += 1

        self.states = self.machine.get_updated_dicts(self.states)
        self.clear_apentrys()
        self.kts = MT.GraphKTS_model()
        if is_hierarchical(self.states):
            self.machine = MT.HierarchicalKTS(model=self.kts, title="", initial=list(self.states[0].values())[0], states=self.states,
                                transitions=self.transitions, show_state_attributes=True)
        else:
            self.machine = MT.GraphKTS(model=self.kts, title="", initial=list(self.states[0].values())[0], states=self.states,
                                transitions=self.transitions, show_state_attributes=True)
            
        self.machine.update_labels(self.states)
        self.machine.generate_image(self.kts)
        self.update_image()
        self.reset_markings()

        self.table_frame.update_idletasks()
        self.ap_canvas.configure(yscrollcommand=self.ap_scrollbar.set, scrollregion=self.ap_canvas.bbox("all"))


    def showDescription(self):
        self.description_button.destroy()
        self.formula_button = tk.Button(master=self.ctl_frame, text="Formula", command=self.showFormula)
        self.formula_button.grid(column=3,row=1,sticky="nw")

        for i in range(len(self.ctlFormulas)):
            self.ctl_Checkboxes[i].config(text=self.ctlFormulas[i]['description'])


    def showFormula(self):
        self.formula_button.destroy()
        self.description_button = tk.Button(master=self.ctl_frame, text="Description", command=self.showDescription)
        self.description_button.grid(column=3,row=1,sticky="nw")

        for i in range(len(self.ctlFormulas)):
            self.ctl_Checkboxes[i].config(text=self.ctlFormulas[i]['formula'])


    def checkModel(self):
        if is_hierarchical(self.states):
            states, transitions = self.machine.expanded_structure(self.states, self.transitions)
        else:
            states = self.states
            transitions = self.transitions
        current_kts = KripkeTransitionSystem(states=states, transitions=transitions, initial=self.states[0]['name'])
        self.failed_states = set() # set of failed states accross all formulas
        self.passed_states = set() # set of passed states accross all formulas

        for element in self.ctlFormulas:
            element['failed'] = []
            if element['variable'].get() == 1:
                result = check_formula(mc_parse(element['formula']), current_kts)
                for state in element['states']:
                    if state not in result:
                        element['failed'].append(state)
                        self.failed_states.add(state)
                    else:
                        self.passed_states.add(state)
        
        self.display_results()

    
    def display_results(self):

        for s in self.machine.get_all_states().items():
            if s[0] in self.machine.get_composite_states(self.states):
                continue
            elif s[0] in self.failed_states:
                self.machine.model_graphs[id(self.kts)].set_node_style(s[0], 'unsat')
            elif s[0] in self.passed_states:
                self.machine.model_graphs[id(self.kts)].set_node_style(s[0], 'sat')
            else:
                self.machine.model_graphs[id(self.kts)].set_node_style(s[0], 'default')

        self.machine.generate_image(self.kts)
        self.update_image()

        for i in range(len(self.ctlFormulas)):
            if self.ctlFormulas[i]['variable'].get() == 0: # base color if formula not checked
                self.ctl_backgrounds[i].config(bg=self.defaultbg)
                self.ctl_Checkboxes[i].config(bg=self.defaultbg)
                self.ctl_states[i].config(bg=self.defaultbg)
                self.check_results[i].config(text='')
            elif self.ctlFormulas[i]['failed'] == []:
                self.ctl_backgrounds[i].config(bg='lightgreen')
                self.ctl_Checkboxes[i].config(bg='lightgreen')
                self.ctl_states[i].config(bg='lightgreen')
                self.check_results[i].config(text='passed')
            else:
                self.ctl_backgrounds[i].config(bg='darksalmon')
                self.ctl_Checkboxes[i].config(bg='darksalmon')
                self.ctl_states[i].config(bg='darksalmon')
                self.check_results[i].config(text=f"failed for: {str(self.ctlFormulas[i]['failed'])}")

        self.formula_frame.update_idletasks()
        self.formula_canvas.configure(yscrollcommand=self.formula_scrollbar.set, scrollregion=self.formula_canvas.bbox("all"))


    def openCTLwindow(self, formula_number=None):

        self.ctlWindow = tk.Toplevel(self.root)
        self.ctlWindow.title("Create CTL Formula")
        self.ctlWindow.geometry("600x400")
        self.ctlWindow.rowconfigure(index=[0,1,2,3,4],weight=1)
        self.ctlWindow.columnconfigure(index=[0,1,2],weight=1)

        formula_label = tk.Label(self.ctlWindow, text="Enter CTL Formula:")     
        formula_label.grid(column=0, row=0, sticky="e")

        self.formula_entry = tk.Entry(self.ctlWindow)
        if formula_number != None:
            self.formula_entry.insert(10, self.ctlFormulas[formula_number]['formula'])
        self.formula_entry.grid(column=1, row=0, sticky="w")

        self.ctlError_label = tk.Label(self.ctlWindow, text="", fg='red')
        self.ctlError_label.grid(column=1, row=1)

        description_label = tk.Label(self.ctlWindow, text="Enter description (optional):")     
        description_label.grid(column=0, row=2, sticky="e")

        self.description_entry = tk.Entry(self.ctlWindow)
        if formula_number != None:
            self.description_entry.insert(10, self.ctlFormulas[formula_number]['description'])
        self.description_entry.grid(column=1, row=2, sticky="w")

        states_label = tk.Label(self.ctlWindow, text="Pick states for the formula:")
        states_label.grid(column=0, row=3, sticky="ne")

        if formula_number != None:
            done_CTLwindow = tk.Button(self.ctlWindow, text="Done", command=self.saveEdit)
        else:
            done_CTLwindow = tk.Button(self.ctlWindow, text="Done", command=self.saveCTL)
        done_CTLwindow.grid(column=0, row=4, columnspan=3)

        self.canvas = tk.Canvas(self.ctlWindow, width=150, height=150) # canvas to add scrollbar
        self.canvas.grid(column=1, row=3, sticky="w")
        frame = tk.Frame(self.canvas)

        self.canvas.create_window((0,0), window=frame, anchor="nw", tags="frame")

        # create checkboxes for all states
        state_count = 0

        self.check_vars = []
        if is_hierarchical(self.states):
            state_dicts = self.machine.get_unnested_dicts()
        else:
            state_dicts = self.states
        for s in state_dicts:
            if s['name'] not in self.machine.get_composite_states(self.states):
                if formula_number == None:
                    self.check_vars.append(tk.IntVar(value=1))
                else:
                    if s['name'] in self.ctlFormulas[formula_number]['states']:
                        self.check_vars.append(tk.IntVar(value=1))
                    else:
                        self.check_vars.append(tk.IntVar(value=0))
            
                current_state = s['name']
                tk.Checkbutton(master=frame, text=current_state, variable=self.check_vars[state_count]).grid(column=0, row=state_count, sticky="w")
                state_count += 1
        
        # create scrollbar for states
        self.state_scrollbar = tk.Scrollbar(self.ctlWindow, orient="vertical", command=self.canvas.yview)
        self.state_scrollbar.grid(column=2, row=3, sticky="ns")

        frame.update_idletasks()
        self.canvas.configure(yscrollcommand=self.state_scrollbar.set, scrollregion=self.canvas.bbox("all"))


    def saveCTL(self):

        try:
            mc_parse(self.formula_entry.get())
        except Exception as error:
            self.ctlError_label.config(text=error)
        else:
            checked_states = []
            states = self.machine.non_composite_states(self.states)

            for i in range(len(states)):
                if self.check_vars[i].get() == 1:
                    checked_states.append(states[i]['name'])

            new_var = tk.IntVar()

            self.ctlFormulas.append({'formula': self.formula_entry.get(), 'description': self.description_entry.get(),
                                    'states': checked_states, 'active': False, 'failed': [], 'variable': new_var})

            self.ctl_backgrounds.append(tk.Label(self.formula_frame))
            self.ctl_backgrounds[self.number_formulas].grid(column=0, row=self.number_formulas*2, columnspan=2, sticky="nwes")

            self.ctl_Checkboxes.append(tk.Checkbutton(master=self.formula_frame, text=self.formula_entry.get(), variable=new_var, wraplength=190))
            self.ctl_Checkboxes[self.number_formulas].grid(column=0, row=self.number_formulas*2, sticky="w")

            self.check_results.append(tk.Label(master=self.formula_frame, text='', wraplength=400))
            self.check_results[self.number_formulas].grid(column=0, row=self.number_formulas*2 + 1, columnspan=2, sticky='w')

            if len(checked_states) == (len(states)):
                self.ctl_states.append(tk.Label(self.formula_frame, text=str(['All'])))
            else:
                self.ctl_states.append(tk.Label(self.formula_frame, text=str(checked_states), wraplength=190))
            self.ctl_states[self.number_formulas].grid(column=1,row=self.number_formulas*2,sticky="w")

            self.number_formulas += 1
            
            self.formula_frame.update_idletasks()
            self.formula_canvas.configure(yscrollcommand=self.formula_scrollbar.set, scrollregion=self.formula_canvas.bbox("all"))

            self.ctlWindow.destroy()


    def openEditWindow(self):
        self.editWindow = tk.Toplevel(self.root)
        self.editWindow.title("Edit CTL Formula")
        self.editWindow.geometry("600x400")
        self.editWindow.rowconfigure(index=[0],weight=1)
        self.editWindow.columnconfigure(index=[0],weight=1)

        formula_label = tk.Label(self.editWindow, text="Choose Formula to be edited:")     
        formula_label.grid(column=0, row=0, sticky="nw")

        con_editWindow = tk.Button(self.editWindow, text="Continue", command=self.editFormula)
        con_editWindow.grid(column=0, row=2)

        editCanvas = tk.Canvas(self.editWindow, height=250, width=100)
        editCanvas.grid(column=0, row=1, sticky="nsew")
        editFrame = tk.Frame(editCanvas)

        editCanvas.create_window((0,0), window=editFrame, anchor="nw", tags="editFrame")

        self.chosen_variable = tk.IntVar()

        for i in range(len(self.ctlFormulas)):
            formula_radio = tk.Radiobutton(master=editFrame, text=self.ctlFormulas[i]['formula'], variable=self.chosen_variable, value=i)
            formula_radio.grid(column=0, row=i, sticky="nw")

        editScrollbar = tk.Scrollbar(self.editWindow, orient="vertical", command=editCanvas.yview)
        editScrollbar.grid(column=1, row=1, sticky="ns")
        editFrame.update_idletasks()
        editCanvas.configure(yscrollcommand=editScrollbar.set, scrollregion=editCanvas.bbox("all"))
    
    def editFormula(self):
        self.formula_number = self.chosen_variable.get()
        self.editWindow.destroy()
        self.openCTLwindow(formula_number=self.formula_number)
    
    
    def saveEdit(self):
        try:
            mc_parse(self.formula_entry.get())
        except Exception as error:
            self.ctlError_label.config(text=error)
        else:
            checked_states = []
            states = self.machine.non_composite_states(self.states)

            for i in range(len(states)):
                if self.check_vars[i].get() == 1:
                    checked_states.append(states[i]['name'])
            
            self.ctlFormulas[self.formula_number]['formula'] = self.formula_entry.get()
            self.ctlFormulas[self.formula_number]['description'] = self.description_entry.get()
            self.ctlFormulas[self.formula_number]['states'] = checked_states

            self.ctl_Checkboxes[self.formula_number].config(text=self.formula_entry.get())

            if len(checked_states) == len(states):
                self.ctl_states[self.formula_number].config(text=str(['All']))
            else:
                self.ctl_states[self.formula_number].config(text=str(checked_states))

            self.reset_markings()
            self.formula_frame.update_idletasks()
            self.formula_canvas.configure(yscrollcommand=self.formula_scrollbar.set, scrollregion=self.formula_canvas.bbox("all"))

            self.ctlWindow.destroy()


    def openDelWindow(self):
        self.delWindow = tk.Toplevel(self.root)
        self.delWindow.title("Delete CTL Formulas")
        self.delWindow.geometry("400x300")
        self.delWindow.rowconfigure(index=[0],weight=1)
        self.delWindow.columnconfigure(index=[0],weight=1)

        formula_label = tk.Label(self.delWindow, text="Choose Formulas to be deleted:")     
        formula_label.grid(column=0, row=0, sticky="nw")

        done_delWindow = tk.Button(self.delWindow, text="Done", command=self.deleteCTL)
        done_delWindow.grid(column=0, row=2)

        delCanvas = tk.Canvas(self.delWindow, height=250, width=100)
        delCanvas.grid(column=0, row=1, sticky="nsew")
        delFrame = tk.Frame(delCanvas)

        delCanvas.create_window((0,0), window=delFrame, anchor="nw", tags="delFrame")

        self.del_vars = []
        del_boxes = []

        for i in range(len(self.ctlFormulas)):
            self.del_vars.append(tk.IntVar())
            del_boxes.append(tk.Checkbutton(master=delFrame, text=self.ctlFormulas[i]['formula'], variable=self.del_vars[i]))
            del_boxes[i].grid(column=0, row=i, sticky="nw")

        delScrollbar = tk.Scrollbar(self.delWindow, orient="vertical", command=delCanvas.yview)
        delScrollbar.grid(column=1, row=1, sticky="ns")
        delFrame.update_idletasks()
        delCanvas.configure(yscrollcommand=delScrollbar.set, scrollregion=delCanvas.bbox("all"))


    def deleteCTL(self):
        
        self.delWindow.destroy()

        del_items = []

        for i in range(len(self.ctlFormulas)):
            if self.del_vars[i].get() == 1:
                del_items.append(self.ctlFormulas[i])

        temp = []
        for element in self.ctlFormulas:
            if element not in del_items:
                temp.append(element)

        self.ctlFormulas = temp

        self.update_ctl_frame()
        self.reset_markings()


    def clear_ctl_frame(self):
        for i in range(len(self.ctl_Checkboxes)):
            self.ctl_backgrounds[i].destroy()
            self.ctl_Checkboxes[i].destroy()
            self.ctl_states[i].destroy()
            self.check_results[i].destroy()
        
        self.ctl_backgrounds.clear()
        self.ctl_Checkboxes.clear()
        self.ctl_states.clear()
        self.check_results.clear()


    def update_ctl_frame(self):
        self.clear_ctl_frame()

        self.number_formulas = 0

        for i in range(len(self.ctlFormulas)):
            self.ctl_backgrounds.append(tk.Label(self.formula_frame))
            self.ctl_backgrounds[self.number_formulas].grid(column=0, row=self.number_formulas*2, columnspan=2, sticky="nwes")

            self.ctl_Checkboxes.append(tk.Checkbutton(master=self.formula_frame, text=self.ctlFormulas[i]['formula'],
                                                      variable=self.ctlFormulas[i]['variable'], wraplength=190))
            self.ctl_Checkboxes[self.number_formulas].grid(column=0, row=self.number_formulas*2, sticky="w")

            self.check_results.append(tk.Label(master=self.formula_frame, text='', wraplength=400))
            self.check_results[self.number_formulas].grid(column=0, row=self.number_formulas*2 + 1, columnspan=2, sticky='w')

            if len(self.ctlFormulas[i]['states']) == len(self.machine.non_composite_states(self.states)):
                self.ctl_states.append(tk.Label(self.formula_frame, text=str(['All'])))
            else:
                self.ctl_states.append(tk.Label(self.formula_frame, text=str(self.ctlFormulas[i]['states']), wraplength=190))
            self.ctl_states[self.number_formulas].grid(column=1,row=self.number_formulas*2,sticky="w")

            self.number_formulas += 1


    def save_as(self):
        self.saveasPath = fd.asksaveasfilename(title='Select a file to save the model', initialdir='./saves',
                                          filetypes=[('json', '*.json')], defaultextension='.json')

        for element in self.ctlFormulas:
            element['variable'] = element['variable'].get() # save value instead of IntVar Object

        data = {'states': self.states, 'transitions': self.transitions, 'formulas': self.ctlFormulas}

        try:
            with open(self.saveasPath, 'w+') as f:
                json.dump(data, f)
        except FileNotFoundError:
            pass

        for i in range(len(self.ctlFormulas)):
            self.ctlFormulas[i]['variable'] = tk.IntVar(value=int(element['variable'])) # transform back to IntVar
            self.ctl_Checkboxes[i].config(variable=self.ctlFormulas[i]['variable'])
        
        self.root.title(f"EdMo - {self.saveasPath}")


    def save_progress(self):

        if self.saveasPath == '':
            self.save_as()
        
        else:

            for element in self.ctlFormulas:
                element['variable'] = element['variable'].get() # save value instead of IntVar Object

            data = {'states': self.states, 'transitions': self.transitions, 'formulas': self.ctlFormulas}

            try:
                with open(self.saveasPath, 'w+') as f:
                    json.dump(data, f)
            except FileNotFoundError:
                pass

            for i in range(len(self.ctlFormulas)):
                self.ctlFormulas[i]['variable'] = tk.IntVar(value=int(element['variable'])) # transform back to IntVar
                self.ctl_Checkboxes[i].config(variable=self.ctlFormulas[i]['variable'])
    
    
    def load(self):

        self.saveasPath = fd.askopenfilename(title='Select a file to load a model', initialdir='./saves', filetypes=[('json', '*.json')])

        try:
            with open(self.saveasPath) as f:
                data = json.load(f)
                self.states = data['states']
                self.transitions = data['transitions']
                self.ctlFormulas = data['formulas']
        except FileNotFoundError:
            return
        
        self.kts = MT.GraphKTS_model()
        if is_hierarchical(self.states):
            self.machine = MT.HierarchicalKTS(model=self.kts, title="", initial=list(self.states[0].values())[0], states=self.states,
                                transitions=self.transitions, show_state_attributes=True)
        else:
            self.machine = MT.GraphKTS(model=self.kts, title="", initial=list(self.states[0].values())[0], states=self.states,
                                transitions=self.transitions, show_state_attributes=True)
        
        self.menubar.entryconfig("Layout", state="normal")
        self.machine.update_labels(self.states)
        self.machine.generate_image(self.kts)
        self.set_new_image()
        self.update_ap_frame()

        for element in self.ctlFormulas:
            element['variable'] = tk.IntVar(value=int(element['variable'])) # transform back to IntVar with saved value

        self.update_ctl_frame()

        self.root.title(f"EdMo - {self.saveasPath}")



if __name__ == "__main__":
    gui = mcGUI()