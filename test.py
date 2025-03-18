import keyboard

flag = False
def on_press(event):
    if event.name == 'shift':
        flag = True

if flag:
    print("Нажата!")

keyboard.on_press(on_press)
keyboard.wait('esc')