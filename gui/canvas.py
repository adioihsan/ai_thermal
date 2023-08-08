import PySimpleGUI as sg
can=sg.Canvas(size=(700,500), background_color='grey', key='canvas')
layout = [[can]]
window = sg.Window('Canvas Example', layout, finalize=True)
tkc=can.TKCanvas
fig = [tkc.create_rectangle(100, 100, 600, 400, outline='white'),
   tkc.create_line(50, 50, 650, 450, fill='red', width=5),
   tkc.create_oval(150,150,550,350, fill='blue'),
   tkc.create_text(350, 250, text="Hello World",
   fill='white', font=('Arial Bold', 16)),
]
while True:
   event, values = window.read()
   if event == sg.WIN_CLOSED:
      break