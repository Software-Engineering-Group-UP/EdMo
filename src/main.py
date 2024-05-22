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

        self.ctlFormulas = []

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

        self.ap_frame.columnconfigure(index=[0,1], weight=1)
        self.ap_frame.rowconfigure(index=[0,1,2], weight=2)

        ap_headline = tk.Label(self.ap_frame, text="Manage APs", borderwidth=2, relief="groove")
        ap_headline.grid(column=0,row=0,columnspan=2,sticky="nsew")

        self.editAP_button = tk.Button(master=self.ap_frame, text="Edit", command=self.editAP)
        self.editAP_button.grid(column=0,row=1,sticky="nw")

        self.ap_canvas = tk.Canvas(self.ap_frame, width=430, height=155)
        self.ap_canvas.grid(column=0, row=2, columnspan=2, sticky="nws")

        self.table_frame = tk.Frame(self.ap_canvas, bg='green')
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
            state_label = tk.Label(self.table_frame, text="", borderwidth=1, relief="solid")
            state_label.grid(column=0,row=1+state_count,sticky="nsew")

            self.ap_labels.append(tk.Label(self.table_frame, text="", borderwidth=1, relief="solid"))
            self.ap_labels[state_count].grid(column=1,row=1+state_count,sticky="nsew")

            state_count += 1
        
        row_count = self.table_frame.grid_size()[1]
        self.table_frame.columnconfigure(index=[0,1], minsize=215)
        self.table_frame.rowconfigure(index=list(range(row_count)), minsize=25)

        self.table_frame.update_idletasks()
        self.ap_canvas.configure(yscrollcommand=self.ap_scrollbar.set, scrollregion=self.ap_canvas.bbox("all"))


    def create_ctl_frame(self):
        self.ctl_frame = tk.Frame(self.root, width=450, height=250)
        self.ctl_frame.grid_propagate(0)

        self.ctl_frame.columnconfigure(index=[0,1,2,3],weight=1)
        self.ctl_frame.columnconfigure(index=[0,1,2],minsize=110)
        self.ctl_frame.rowconfigure(index=[0,1,2],weight=2)

        ctl_label = tk.Label(self.ctl_frame, text="Manage CTL-Formulas", borderwidth=2, relief="groove")
        ctl_label.grid(column=0,row=0,columnspan=4,sticky="nsew")

        self.defaultbg = ctl_label.cget('bg')

        editCTL_button = tk.Button(master=self.ctl_frame, text="Add", command=self.openCTLwindow)
        editCTL_button.grid(column=0,row=1,sticky="nw")

        self.delete_button = tk.Button(master=self.ctl_frame, text="Delete", command=self.openDelWindow)
        self.delete_button.grid(column=1,row=1,sticky="nw")

        self.description_button = tk.Button(master=self.ctl_frame, text="Description", command=self.showDescription)
        self.description_button.grid(column=2,row=1,sticky="nw")

        check_button = tk.Button(master=self.ctl_frame, text="Check", command=self.checkModel)
        check_button.grid(column=3,row=1,sticky="ne")

        self.formula_canvas = tk.Canvas(self.ctl_frame, width=400, height=155)
        self.formula_canvas.grid(column=0, row=2, columnspan=3, sticky="nws")

        self.formula_frame = tk.Frame(self.formula_canvas)
        self.formula_canvas.create_window((0,0), window=self.formula_frame, anchor="nw", tags="formula_frame")

        self.formula_frame.columnconfigure(index=[1], minsize=400)

        self.formula_scrollbar = tk.Scrollbar(self.ctl_frame, orient="vertical", command=self.formula_canvas.yview)
        self.formula_scrollbar.grid(column=3, row=2, sticky="nse")

        self.formula_frame.update_idletasks()
        self.formula_canvas.configure(yscrollcommand=self.formula_scrollbar.set, scrollregion=self.formula_canvas.bbox("all"))

        self.number_formulas = 0
        self.ctl_Checkboxes = []
        self.ctl_states = []
        self.check_results = []
        self.ctl_backgrounds = []


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

        state_count = 0

        for s in self.machine.states.items():
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

        for s in self.states:
            current_ap = self.ap_entrys[state_count].get()
            self.ap_entrys[state_count].destroy()
            self.ap_labels.append(tk.Label(self.table_frame, text=current_ap, borderwidth=1, relief="solid"))
            self.ap_labels[state_count].grid(column=1,row=1+state_count,sticky="nsew")

            s['tags'] = current_ap.split(", ")

            state_count += 1

        self.clear_apentrys()
        self.kts = MT.KTS_model()
        self.machine = MT.KTS(model=self.kts, title="", initial=list(self.states[0].values())[0], states=self.states, transitions=self.transitions, show_state_attributes=True)
        self.machine.generate_image(self.kts)
        self.update_image()


    def showDescription(self):
        self.description_button.destroy()
        self.formula_button = tk.Button(master=self.ctl_frame, text="Formula", command=self.showFormula)
        self.formula_button.grid(column=2,row=1,sticky="nw")

        for i in range(len(self.ctlFormulas)):
            self.ctl_Checkboxes[i].config(text=self.ctlFormulas[i]['description'])


    def showFormula(self):
        self.formula_button.destroy()
        self.description_button = tk.Button(master=self.ctl_frame, text="Description", command=self.showDescription)
        self.description_button.grid(column=2,row=1,sticky="nw")

        for i in range(len(self.ctlFormulas)):
            self.ctl_Checkboxes[i].config(text=self.ctlFormulas[i]['formula'])


    def checkModel(self):
        current_kts = KripkeTransitionSystem(states=self.states, transitions=self.transitions, initial=self.states[0]['name'])
        self.failed_states = set() # set of failed states accross all formulas

        for element in self.ctlFormulas:
            element['failed'] = []
            if element['variable'].get() == 1:
                result = check_formula(mc_parse(element['formula']), current_kts)
                for state in element['states']:
                    if state not in result:
                        element['failed'].append(state)
                        self.failed_states.add(state)
        
        self.display_results()

    
    def display_results(self):

        for s in self.states:
            if s['name'] in self.failed_states:
                self.machine.model_graphs[id(self.kts)].set_node_style(s['name'], 'unsat')
            else:
                self.machine.model_graphs[id(self.kts)].set_node_style(s['name'], 'sat')

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


    def openCTLwindow(self):

        self.ctlWindow = tk.Toplevel(self.root)
        self.ctlWindow.title("Create CTL Formula")
        self.ctlWindow.geometry("400x300")
        self.ctlWindow.rowconfigure(index=[0,1,2,3,4],weight=1)
        self.ctlWindow.columnconfigure(index=[0,1,2],weight=1)

        formula_label = tk.Label(self.ctlWindow, text="Enter CTL Formula:")     
        formula_label.grid(column=0, row=0, sticky="e")

        self.formula_entry = tk.Entry(self.ctlWindow)
        self.formula_entry.grid(column=1, row=0, sticky="w")

        self.ctlError_label = tk.Label(self.ctlWindow, text="")
        self.ctlError_label.grid(column=1, row=1)

        description_label = tk.Label(self.ctlWindow, text="Enter description (optional):")     
        description_label.grid(column=0, row=2, sticky="e")

        self.description_entry = tk.Entry(self.ctlWindow)
        self.description_entry.grid(column=1, row=2, sticky="w")

        states_label = tk.Label(self.ctlWindow, text="Pick states for the formula:")
        states_label.grid(column=0, row=3, sticky="ne")

        done_CTLwindow = tk.Button(self.ctlWindow, text="Done", command=self.saveCTL)
        done_CTLwindow.grid(column=0, row=4, columnspan=3)

        self.canvas = tk.Canvas(self.ctlWindow, width=150, height=150) # canvas to add scrollbar
        self.canvas.grid(column=1, row=3, sticky="w")
        frame = tk.Frame(self.canvas)

        self.canvas.create_window((0,0), window=frame, anchor="nw", tags="frame")

        # create checkboxes for all states
        state_count = 0

        self.check_vars = []
        for v in range(len(self.states)):
            self.check_vars.append(tk.IntVar(value=1))
        
        for s in self.states:
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

            for i in range(len(self.states)):
                if self.check_vars[i].get() == 1:
                    checked_states.append(self.states[i]['name'])

            new_var = tk.IntVar()

            self.ctlFormulas.append({'formula': self.formula_entry.get(), 'description': self.description_entry.get(),
                                    'states': checked_states, 'active': False, 'failed': [], 'variable': new_var})

            self.ctl_backgrounds.append(tk.Label(self.formula_frame))
            self.ctl_backgrounds[self.number_formulas].grid(column=0, row=self.number_formulas*2, columnspan=2, sticky="nwes")

            self.ctl_Checkboxes.append(tk.Checkbutton(master=self.formula_frame, text=self.formula_entry.get(), variable=new_var, wraplength=190))
            self.ctl_Checkboxes[self.number_formulas].grid(column=0, row=self.number_formulas*2, sticky="w")

            self.check_results.append(tk.Label(master=self.formula_frame, text='', wraplength=400))
            self.check_results[self.number_formulas].grid(column=0, row=self.number_formulas*2 + 1, columnspan=2, sticky='w')

            if len(checked_states) == len(self.states):
                self.ctl_states.append(tk.Label(self.formula_frame, text=str(['All'])))
            else:
                self.ctl_states.append(tk.Label(self.formula_frame, text=str(checked_states), wraplength=190))
            self.ctl_states[self.number_formulas].grid(column=1,row=self.number_formulas*2,sticky="w")

            self.number_formulas += 1
            
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

        for i in range(len(self.ctl_Checkboxes)):
            self.ctl_backgrounds[i].destroy()
            self.ctl_Checkboxes[i].destroy()
            self.ctl_states[i].destroy()
            self.check_results[i].destroy()
        
        self.ctl_backgrounds.clear()
        self.ctl_Checkboxes.clear()
        self.ctl_states.clear()
        self.check_results.clear()

        del_items = []

        for i in range(len(self.ctlFormulas)):
            if self.del_vars[i].get() == 1:
                del_items.append(self.ctlFormulas[i])

        temp = []
        for element in self.ctlFormulas:
            if element not in del_items:
                temp.append(element)

        self.ctlFormulas = temp

        self.number_formulas = 0

        for i in range(len(self.ctlFormulas)):
            self.ctl_backgrounds.append(tk.Label(self.formula_frame))
            self.ctl_backgrounds[self.number_formulas].grid(column=0, row=self.number_formulas*2, columnspan=2, sticky="nwes")

            self.ctl_Checkboxes.append(tk.Checkbutton(master=self.formula_frame, text=self.ctlFormulas[i]['formula'],
                                                      variable=self.ctlFormulas[i]['variable'], wraplength=190))
            self.ctl_Checkboxes[self.number_formulas].grid(column=0, row=self.number_formulas*2, sticky="w")

            self.check_results.append(tk.Label(master=self.formula_frame, text='', wraplength=400))
            self.check_results[self.number_formulas].grid(column=0, row=self.number_formulas*2 + 1, columnspan=2, sticky='w')

            if len(self.ctlFormulas[i]['states']) == len(self.states):
                self.ctl_states.append(tk.Label(self.formula_frame, text=str(['All'])))
            else:
                self.ctl_states.append(tk.Label(self.formula_frame, text=str(self.ctlFormulas[i]['states']), wraplength=190))
            self.ctl_states[self.number_formulas].grid(column=1,row=self.number_formulas*2,sticky="w")

            self.number_formulas += 1



if __name__ == "__main__":
    gui = mcGUI()