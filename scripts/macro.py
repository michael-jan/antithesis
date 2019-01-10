import pyautogui
import time

pyautogui.PAUSE = 0.18
pyautogui.FAILSAFE = True

# 2 seconds to open FL Studio
time.sleep(2)

counter_start = 0
num_iters = 20000
for i in range(counter_start, counter_start + num_iters):

    start_time = time.monotonic()

    # click Presets and select Randomize
    pyautogui.click(1150, 290)
    pyautogui.keyDown('r')
    pyautogui.keyUp('r')
    pyautogui.click(426, 314)
    pyautogui.click(426, 603)

    # save preset txt
    pyautogui.click(426, 314)
    pyautogui.click(480, 524)
    pyautogui.typewrite("preset" + str(i) + ".txt")
    if i == 0:
        pyautogui.doubleClick(700, 465)
    pyautogui.click(1126, 804)

    pyautogui.click(768, 254)
    # file explorer to save as wav
    pyautogui.hotkey('ctrl', 'r')
    pyautogui.typewrite("audio" + str(i) + ".wav")

    # select 'wav' folder
    # pyautogui.doubleClick(300, 200)
    time.sleep(0.1)

    # click save
    pyautogui.click(750, 515)
    time.sleep(0.1)

    pyautogui.keyDown('\n')
    pyautogui.keyUp('\n')

    time.sleep(4.5)

    print('iter#:', i, 'of', num_iters, '| s:', time.monotonic() - start_time)

print('done')
