import time
import tkinter as tk
from tkinter import ttk

from selenium.common import NoSuchElementException
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By

import config

chromeDriver: Chrome
guiRoot: tk


def initDriver() -> Chrome:
    # driverManager = ChromeDriverManager()
    # driverPath = driverManager.install()
    # driverService = ChromeOptions()
    # options = Options()
    driver = Chrome()  # options=options, service=driverService
    return driver


def clickElement(element):
    chromeDriver.execute_script("arguments[0].click();", element)


def homeButton():
    if chromeDriver:
        chromeDriver.get(config.DESTINY_URL)


def closeButton():
    if chromeDriver:
        chromeDriver.close()

    exit(0)


def setText(guiElement, text):
    guiElement.configure(text=text)
    guiElement.update()
    guiRoot.update()


def destinySendKeys(text):
    try:
        inputBox = chromeDriver.find_element(By.NAME, "searchString")
    except NoSuchElementException:
        inputBox = chromeDriver.find_element(By.NAME, "barcode")
    inputBox.send_keys(text)


# Auto Fill Button (abbreviated)
def aFB(textEntry, status, shouldMarkLost):
    text = textEntry.get()
    textParts = text.split(",")

    for i, part in enumerate(textParts):
        try:
            if (messageBox := chromeDriver.find_element(By.ID, "messageBox")) is not None:
                messageText = messageBox.find_element(By.TAG_NAME, "li").get_property("textContent")
                setText(status, f"Status: Message Box - {messageText}")

                if messageText in ["Item is already available."]:
                    setText(status, "Status: Message Box Ignored.")  # Can Skip Message Box
                    safeToIgnore = True
                else:
                    setText(status, "Status: Stopped on Message Box!")  # User Input Required
                    safeToIgnore = False

                if not safeToIgnore:
                    textEntry.delete(0, tk.END)
                    textEntry.insert(0, ", ".join(textParts[i:len(textParts)]))
                    return
        except NoSuchElementException:
            pass  # No Message Box present

        part = part.strip()
        setText(status, f"Status: Sending Barcode {part}")
        destinySendKeys(part)

        clickElement(chromeDriver.find_element(By.NAME, "go"))

        time.sleep(1)  # Constant sleep time to avoid spamming

        if shouldMarkLost:
            try:
                clickElement(chromeDriver.find_element(By.NAME, "markLost"))
                setText(status, f"Status: Marking {part} lost.")
            except NoSuchElementException:
                setText(status, f"Status: No Mark Lost Button on {part}!")
                textEntry.delete(0, tk.END)
                textEntry.insert(0, ", ".join(textParts[i:len(textParts)]))

            time.sleep(1)

            try:
                clickElement(chromeDriver.find_element(By.NAME, "markLostOK"))
                setText(status, f"Status: Confirming {part} is lost.")
            except NoSuchElementException:
                setText(status, f"Status: No Mark Lost conformation for {part}!")
                textEntry.delete(0, tk.END)
                textEntry.insert(0, ", ".join(textParts[i:len(textParts)]))

            time.sleep(1)

    setText(status, "Status: Auto Fill Done")


def processMatrix(entry, status):
    text = entry.get()
    serialNumber = text.split(",")[0]

    setText(status, f"Status: Sending Barcode {serialNumber}")

    destinySendKeys(serialNumber)
    clickElement(chromeDriver.find_element(By.NAME, "go"))


def seperatorBar(root):
    ttk.Separator(root, orient='horizontal').pack(fill='x')


def initGui():
    root = tk.Tk()

    # INFO BAR
    tk.Label(root, text="Destiny Helper v0.0.3").pack()

    # NAVIGATION

    tk.Label(root, text="Navigation").pack()
    seperatorBar(root)

    tk.Button(root, text="Home", command=homeButton).pack()
    tk.Button(root, text="Exit", command=closeButton).pack()

    # DATA MATRIX

    tk.Label(root, text="Data Matrix Processor").pack()
    seperatorBar(root)

    matrixStatus = tk.Label(root, text="Scan a QR Code...")
    matrixStatus.pack()

    matrixEntry = tk.Entry(root, width=40)
    matrixEntry.pack()

    tk.Button(root, text="Process Matrix", command=lambda: processMatrix(matrixEntry, matrixStatus)).pack()

    # AUTO FILL

    tk.Label(root, text="Auto-Fill").pack()
    seperatorBar(root)

    autoFillStatus = tk.Label(root, text="Status: Waiting...")
    autoFillStatus.pack()

    autoFillEntry = tk.Entry(root, width=40)
    autoFillEntry.pack()

    bulkLostBool = tk.BooleanVar()
    bulkLost = tk.Checkbutton(root, text="Mark Lost?", var=bulkLostBool)
    bulkLost.pack()

    tk.Button(root, text="Auto-Fill", command=lambda: aFB(autoFillEntry, autoFillStatus, bulkLostBool.get())).pack()

    return root


def Main():
    global chromeDriver, guiRoot

    chromeDriver = initDriver()
    chromeDriver.set_window_size(900, 700)
    chromeDriver.get(config.DESTINY_URL_LOGIN)
    clickElement(chromeDriver.find_element(By.ID, "Login"))

    guiRoot = initGui()
    guiRoot.winfo_toplevel().wm_title("Destiny Helper")

    guiRoot.focus_force()
    guiRoot.mainloop()


if __name__ == "__main__":
    Main()
