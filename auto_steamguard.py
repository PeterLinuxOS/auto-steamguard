import json
import os
import re
import pyautogui
import time 
from PIL import Image
import win32gui
import pytesseract
from steam import guard
from base64 import b64decode
from termcolor import colored,cprint
from fuzzywuzzy import process
from tabulate import tabulate
import sys
import ctypes
accounts = dict()
if getattr(sys, 'frozen', False):
    script_dir = os.path.dirname(sys.executable)
else:
    script_dir = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.dirname(os.path.realpath(__file__))
maFiles_dir = os.path.join(script_dir,"maFiles")
pytesseract.pytesseract.tesseract_cmd =  os.path.join(PATH,"Tesseract-OCR","tesseract.exe")
ignore_list = list()
login_place = Image.open(PATH + "/signin_button.png")


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def load_accounts():
    

    # Extract the shared secret
    

    for filename in os.listdir(maFiles_dir):
        # Check if the file is a JSON file
        if filename.endswith('.maFile'):
            
            with open(os.path.join(maFiles_dir, filename), 'r') as f:
                data = json.load(f)
            if "account_name" in data and "shared_secret" in data:
                accounts[data['account_name']] = data['shared_secret']
                
            elif "shared_secret" in data and not "account_name" in data and "uri" in data:
                match = re.search(r':(\w+)\?', data['uri'])
                if match:
                    username = match.group(1)
                    accounts[username] = data['shared_secret']
                
                    
    cprint(f"Loaded {len(accounts)} accounts","green")
             
def main_menu() :
    while True:
        cprint("============================================", "green")
        cprint("       Welcome to Auto-SteamGuard Bot       ", "green")
        cprint("============================================", "green")
        cprint("[1] Start Bot", "yellow")
        cprint("[2] Reload mafiles", "yellow")
        cprint("[3] Show loaded accounts", "yellow")
        cprint("[4] Credits", "yellow")
        cprint("[5] Exit", "red")
        choice = input("Enter your choice (1-5): ")
        if choice == "1":
            print("Starting bot...")
            break
        elif choice == "2":
            load_accounts()
            input(colored("Press Enter to continue...", "cyan"))
        elif choice == "3":
            table = []
            for i, account in enumerate(accounts.keys(), 1):
                table.append([i, account])

            print(tabulate(table, headers=["No.", "Account Name"], tablefmt="fancy_grid"))
            input(colored("\nPress Enter to continue...", "cyan"))
                
            
        elif choice == "4":
            cprint("Auto-SteamGuard for vertigoboost panel was created by:\n", "cyan")
            cprint("[STT_Esports] PeterLinuxOS#1111", "blue")
            cprint("https://gameboosting.top", "green")
            input(colored("\nPress Enter to continue...", "cyan"))
        elif choice == "5":
            print("Exiting...")
            os._exit(1)
        else:
            cprint("Invalid choice. ","magenta")
            input(colored("Press Enter to continue...", "cyan"))
def main():
    if not is_admin():
        cprint("Please run the file as an administrator.","red")
        input()
        return
    if not os.path.isfile(os.path.join(script_dir,"VertigoBoostPanel.exe")):
        cprint("Please place file in to VertigoBoostPanel path","red")
        input()
        return
    if not os.path.isdir(maFiles_dir):
        cprint("Please create Mafiles folder and place in to your .maFile/s ","red")
        input()
        return
    load_accounts() # laod all accounts in mafile/s
    main_menu()
    cprint("Please start starting your steam account/s...","cyan")
    while True:
        # Get a list of all open windows
        windows = pyautogui.getWindowsWithTitle("Steam Sign In")

        # Check if any windows have the title "Steam Sign In"
        for window in windows:
            
            hwnd = window._hWnd
            if hwnd in ignore_list:
                continue
            
            try:
                window.activate()
            except :
                try:
                    win32gui.SetForegroundWindow(hwnd)
                except:
                    continue
           
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            region=(left, top, right-left, bottom-top)
            button_location = pyautogui.locateOnScreen(login_place, region=region, confidence=0.8,)
            if button_location:
                
                screenshot = pyautogui.screenshot(region=region)
                
                text:str = pytesseract.image_to_string(screenshot, lang='eng')
                
                account_name = text.split("\n")[2].split(" ")[1].strip()
                
                if account_name in accounts:
                    code = guard.generate_twofactor_code(b64decode(accounts[account_name]))
                    if code:
                        
                        x, y = pyautogui.center(button_location)
                        
                        pyautogui.click(x, y)
                        time.sleep(0.5)
                        pyautogui.write(code)
                        time.sleep(2)
                    else:
                        cprint(f"shared_secret is incorrect for {account_name}","red")
                        ignore_list.append(hwnd)    
                        time.sleep(0.5)  
                        continue
                else:
                    
                    best_match, score = process.extractOne(account_name, accounts.keys())
                    
                    if score > 80:
                        cprint(f"Recognized: {account_name} but it is not in the list. Did you mean {best_match}?", "yellow")
                        code = guard.generate_twofactor_code(b64decode(accounts[best_match]))
                        if code:
                            x, y = pyautogui.center(button_location)
                            pyautogui.click(x, y)
                            time.sleep(0.5)
                            pyautogui.write(code)
                        else:
                            cprint(f"shared_secret is incorrect for {account_name}","red")
                            ignore_list.append(hwnd)    
                            time.sleep(0.5)  
                            continue
                        
                    else:
                    
                        cprint(f"I cant find account: {account_name} in maFiles.","red")
                        ignore_list.append(hwnd)    
                        time.sleep(0.5)  
                        continue
                        
          
        time.sleep(2)
    
    
if "__main__" == __name__:
    try:
        main()
    except Exception as E:
        print(E) 
        input()