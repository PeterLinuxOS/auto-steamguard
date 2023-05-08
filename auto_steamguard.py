import json
import os
import re
import pyautogui
import time 
from PIL import Image
import win32gui
import win32con
from steam import guard
from base64 import b64decode
from termcolor import colored,cprint
from fuzzywuzzy import process
from tabulate import tabulate
import sys
import ctypes

import numpy as np

import easyocr

accounts = dict()
if getattr(sys, 'frozen', False):
    script_dir = os.path.dirname(sys.executable)
else:
    script_dir = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.dirname(os.path.realpath(__file__))
maFiles_dir = os.path.join(script_dir,"maFiles")

ignore_list = dict()
login_place = Image.open(PATH + "/signin_button.png")


reader = easyocr.Reader(['en'], )
# Set up the client



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
            cprint("PeterLinuxOS#1111", "blue")
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
    """if not os.path.isfile(os.path.join(script_dir,"VertigoBoostPanel.exe")) or not os.path.isfile(os.path.join(os.path.abspath(os.path.join(script_dir, os.pardir)),"VertigoBoostPanel.exe")):
        cprint("Please place file in to VertigoBoostPanel path","red")
        input()
        return"""
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
            
            try:    
                win32gui.SetForegroundWindow(hwnd)
            except:
                continue
            
            if hwnd in ignore_list and ignore_list[hwnd] >= 3:
                continue
            
            
           
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            region=(left, top, right-left, bottom-top)
            button_location = pyautogui.locateOnScreen(login_place, region=region, confidence=0.8,)
            if button_location:
                
                screenshot = np.array(pyautogui.screenshot(region=region))
                results = reader.readtext(screenshot)
                string_list = [elem[1] for elem in results if type(elem[1]) == str]
                print(string_list)
                account_name = (string_list[2] if not "Enter the" in string_list[2] else str(string_list[1]).split(" ")[1])
                print(account_name)
                if not account_name in accounts:
                    string_list.remove("Use backup code")
                    string_list.remove("Hel_Lno londer have access to mV Steam Mobile_An_")
                    string_list.remove("STEAM GUARD")
                    string_list.remove("Enter the code from your Steam Mobile App")
                    split_accounts = [word for string in string_list for word in string.split()]
                    for s in split_accounts:
                        if s in accounts:
                            account_name = s
                            break
                
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
                        ignore_list[hwnd] +=1 
                        time.sleep(0.5)  
                        continue
                else:
                    
                    best_match, score = process.extractOne(account_name, accounts.keys())
                    
                    if score > 25:
                        cprint(f"Recognized: {account_name} but it is not in the list. Did you mean {best_match}?", "yellow")
                        code = guard.generate_twofactor_code(b64decode(accounts[best_match]))
                        if code:
                            x, y = pyautogui.center(button_location)
                            pyautogui.click(x, y)
                            time.sleep(0.5)
                            pyautogui.write(code)
                            time.sleep(3)
                        else:
                            cprint(f"shared_secret is incorrect for {account_name}","red")
                            ignore_list[hwnd] +=1  
                            time.sleep(0.5)  
                            continue
                        
                    else:
                    
                        cprint(f"I cant find account: {account_name} in maFiles.","red")
                        ignore_list[hwnd] +=1  
                        time.sleep(0.5)  
                        continue
                        
          
        
    
    
if "__main__" == __name__:
        main()
    
        