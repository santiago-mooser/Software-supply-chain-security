#!/bin/python
import os
from tabulate import tabulate
import time
from datetime import datetime

def view_data():
    # Clear the screen
    os.system('clear')
    prompt = "Available data files:\n"
    data_files = os.listdir("data/github_data")
    y = len(data_files)
    data_files += os.listdir("data/package_repo_data")
    # Get last moodified date of each file
    data_files_modified = []
    for file_ in data_files:
        if file_ in data_files[:y]:
            modified_time = os.path.getmtime(f"data/github_data/{file_}")
        else:
            modified_time = os.path.getmtime(f"data/package_repo_data/{file_}")
        # If the modified time is more than 7 days ago but less than 30, print it in yellow
        if modified_time < time.time() - 604800 and modified_time > time.time() - 2592000:
            data_files_modified.append(f"\033[0;33m{datetime.fromtimestamp(modified_time)}\033[0m")
        # If the modified time is more than 30 days ago, print it in red
        elif modified_time < time.time() - 2592000:
            data_files_modified.append(f"\033[0;31m{datetime.fromtimestamp(modified_time)}\033[0m")
        else:
            data_files_modified.append(f"\033[0;32m{datetime.fromtimestamp(modified_time)}\033[0m")

    # zip the two lists together
    data_files = list(zip(data_files, data_files_modified))
    headers = ["File", "Last modified"]
    prompt += tabulate(data_files, headers=headers, tablefmt="fancy_grid")

    print(prompt)
    return

def update_data():

    # Clear the screen
    os.system('clear')
    prompt= "\nAvailable Github-stars-based scripts:\n"

    # Get available pythong scripts from the scripts/scripts/retrieve_data/github_source and scripts/scripts/retrieve_data/package_repo_source folders and print them out withpout the .py extension
    x = 1
    files = os.listdir("scripts/retrieve_data/github_source")
    y = len(files)
    for file_ in files:
        prompt += f"{x}. {file_[:-3]}\n"
        x+=1
    files += os.listdir("scripts/retrieve_data/package_repo_source")
    prompt += "\nAvailable Package repo scripts:\n"
    for file_ in files[y:]:
        prompt += f"{x}. {file_[:-3]}\n"
        x+=1

    prompt += "\n11. Run all\n"
    prompt += "0. Return to menu\n"
    prompt += f"\nWhich update script would you like to run? [1-{x-1}]: "

    while True:
        script = input(prompt)
        script_number = int(script)
        if script_number == 0:
            break
        if script_number <= y:
            print(f"{files[script_number-1]}   \t[*]", end="", flush=True)
            os.system(f'python3 scripts/retrieve_data/github_source/{files[script_number-1]} -o data/github_data/ --quiet')
            print(f"\r{files[script_number-1]}   \t[\033[0;32m\u2714\033[0m]")
        elif script_number > y and script_number <= x-1:
            print(f"{files[script_number-1]}   \t[*]", end="", flush=True)
            os.system(f'python3 scripts/retrieve_data/package_repo_source/{files[script_number-1]} -o data/package_repo_data/ --quiet')
            print(f"\r{files[script_number-1]}   \t[\033[0;32m\u2714\033[0m]")
        elif script_number == x:
            print("Running all update scripts...")
            # Run all scripts
            for file_ in files:
                if file_ in files[:y]:
                    print(f"{file_}   \t[*]", end="", flush=True)
                    os.system(f'python3 scripts/retrieve_data/github_source/{file_} -o data/github_data/ --quiet')
                    # print an emoji tick
                    print(f"\r{file_}   \t[\033[0;32m\u2714\033[0m]")
                else:
                    print(f"{file_}   \t[*]", end="", flush=True)
                    os.system(f'python3 scripts/retrieve_data/package_repo_source/{file_} -o data/package_repo_data/ --quiet')
                    print(f"\r{file_}   \t[\033[0;32m\u2714\033[0m]")
        print("")
    return

if __name__ == "__main__":


    # clear the screen
    splash_screen='''
    ██╗    ██╗███████╗██╗      ██████╗ ██████╗ ███╗   ███╗███████╗
    ██║    ██║██╔════╝██║     ██╔════╝██╔═══██╗████╗ ████║██╔════╝
    ██║ █╗ ██║█████╗  ██║     ██║     ██║   ██║██╔████╔██║█████╗
    ██║███╗██║██╔══╝  ██║     ██║     ██║   ██║██║╚██╔╝██║██╔══╝
    ╚███╔███╔╝███████╗███████╗╚██████╗╚██████╔╝██║ ╚═╝ ██║███████╗
     ╚══╝╚══╝ ╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝

    This script aims to make the research more accessible to the public.
    It helps you to retrieve the data, view the data, and run the various anaylses.
    '''
    options='''
    1. Update data
    2. View data
    3. Run analysis

    0. Exit
    '''
    # Check whether the data directory exists. If it doesn't, create it.
    if not os.path.exists("data"):
        os.mkdir("data")
    if not os.path.exists("data/github_data"):
        os.mkdir("data/github_data")
    if not os.path.exists("data/package_repo_data"):
        os.mkdir("data/package_repo_data")

    print(splash_screen)
    print(options)
    while(True):
        choice = input("Enter your choice: ")
        if choice == '1':
            update_data()
            os.system('clear')
            print(splash_screen)
            print(options)
        elif choice == '2':
            view_data()
            print(options)
        elif choice == '3':
            print("Run analysis")
            os.system('clear')
            print(splash_screen)
            print(options)
        elif choice == '0':
            exit()
        else:
            print("Please enter a valid choice")