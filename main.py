import cv2
import numpy as np
import pyautogui
import time
import keyboard
from pynput.mouse import Listener
import pyperclip
import json

class Player:
    def __init__(self, name=None, buff_type=None, init=False):
        self.name = name
        self.time_received = time.time()
        self.buff_type = buff_type
        if init:
            print(f"Initialized {buff_type} buff")
            self.time_received -= 60*10

class Buffs:
    def __init__(self,waiting_list):
        self.construction = Player(buff_type="construction", init=True)
        self.research = Player(buff_type="research", init=True)
        self.training = Player(buff_type="training", init=True)
        self.heal = Player(buff_type="heal", init=True)
        self.waiting_list = waiting_list
        self.positions = RolesPosition()

    def check(self):
        buffs_to_process = []
        if (time.time() - self.construction.time_received > 60*10) and len(self.waiting_list["construction"]) > 0:
            buffs_to_process.append(self.construction)
        if (time.time() - self.research.time_received > 60*10) and len(self.waiting_list["research"]) > 0:
            buffs_to_process.append(self.research)
        if (time.time() - self.training.time_received > 60*10) and len(self.waiting_list["training"]) > 0:
            buffs_to_process.append(self.training)
        if (time.time() - self.heal.time_received > 60*10) and len(self.waiting_list["heal"]) > 0:
            buffs_to_process.append(self.heal)
        return buffs_to_process


class RolesPosition:
    def __init__(self):
        self.construction = Position(1, coordinates=position_settings["construction"], info="construction")
        self.research = Position(1, coordinates=position_settings["research"], info="research")
        self.training = Position(1, coordinates=position_settings["training"], info="training")
        self.heal = Position(1, coordinates=position_settings["heal"], info="heal")


class Position:
    def __init__(self, dimension, coordinates=None, info=None):
        if coordinates is None:
            print(info)
            temp = []
            for i in range(dimension):
                coordinates = get_coordinates_of_mouse_click()
                temp.append(coordinates[0][0])
                temp.append(coordinates[0][1])
            self.pos = temp
            if dimension == 2:
                self.pos[3] = self.pos[3] - self.pos[1]
                self.pos[2] = self.pos[2] - self.pos[0]
            position_settings[info] = self.pos
        else:
            self.pos = coordinates


def find_and_click(image_path, coordinates, threshold=0.9):
    # Nehmen Sie einen Screenshot
    screenshot = pyautogui.screenshot(region=coordinates)
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    # Laden Sie das Bild, nach dem gesucht werden soll
    template = cv2.imread(image_path)
    w, h = template.shape[:-1]

    # Template Matching
    res = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)

    for pt in zip(*loc[::-1]):  # Wechseln Sie die Reihenfolge der Koordinaten
        # Klicken Sie auf die Mitte des gefundenen Bereichs
        center_point = (pt[0] + int(w/2), pt[1] + int(h/2))
        return center_point

    return False


def get_coordinates_of_mouse_click():
    coordinates = []
    def on_click(x, y, button, pressed):
        if pressed:
            coordinates.append((x, y))
            if len(coordinates) == 1:
                return False
    with Listener(on_click=on_click) as listener:
        listener.join()
    return coordinates


def check_for_command(bottom_area):
    #check for commands
    command_found = False

    status = find_and_click("./static/status.png", bottom_area, threshold=0.7)
    construction_buff = find_and_click("./static/buff_construction.png", bottom_area, threshold=0.9)
    construction_buff_korean = find_and_click("./static/buff_construction_korean.png", bottom_area, threshold=0.9)
    research_buff = find_and_click("./static/buff_research.png", bottom_area, threshold=0.9)
    research_buff_korean = find_and_click("./static/buff_research_korean.png", bottom_area, threshold=0.9)
    training_buff = find_and_click("./static/buff_training.png", bottom_area, threshold=0.9)
    training_buff_korean = find_and_click("./static/buff_training_korean.png", bottom_area, threshold=0.9)
    heal_buff = find_and_click("./static/buff_heal.png", bottom_area, threshold=0.9)
    heal_buff_korean = find_and_click("./static/buff_heal_korean.png", bottom_area, threshold=0.9)
    queue = find_and_click("./static/queue.png", bottom_area, threshold=0.7)
    
    if queue:
        command_found = "queue"
        return command_found, queue
    if status:
        command_found = "status"
        return command_found, None
    if construction_buff or construction_buff_korean:
        command_found = "construction_buff"
        return command_found, None
    if research_buff or research_buff_korean:
        command_found = "research_buff"
        return command_found, None
    if training_buff or training_buff_korean:
        command_found = "training_buff"
        return command_found, None
    if heal_buff or heal_buff_korean:
        command_found = "heal_buff"
        return command_found, None
    return command_found, None


def create_waiting_list(buffs):
    """
    Create a status display dictionary with display names and waiting times.
    :param waiting_list: Dictionary of activities and their lists
    :return: Dictionary mapping activities to display names and waiting times
    """
    # Define a basic mapping from the key to a more readable format
    waiting_list = buffs.waiting_list
    status_display = {}

    for key, value in waiting_list.items():
        waiting_time = 0 if len(value) == 0 else (len(value)-1) * 10
        status_display[key] = waiting_time

    if buffs.construction.name:
        time_passed = time.time() - buffs.construction.time_received
        status_display["construction"] += (10 - int(time_passed/60))
    if buffs.research.name:
        time_passed = time.time() - buffs.research.time_received
        status_display["research"] += (10 - int(time_passed/60))
    if buffs.training.name:
        time_passed = time.time() - buffs.training.time_received
        status_display["training"] += (10 - int(time_passed/60))
    if buffs.heal.name:
        time_passed = time.time() - buffs.heal.time_received
        status_display["heal"] += (10 - int(time_passed/60))

    for key, value in status_display.items():
        if value < 0:
            status_display[key] = 0
    return status_display


def status():
    status_display = create_waiting_list(buffs)
    result_str = "Status: "
    for key, names in buffs.waiting_list.items():
        # Get the display name and waiting time
        waiting_time = status_display[key]
        
        # Append the status and waiting time
        result_str += f"[{key}]: {waiting_time}min, "

    #move to chat input
    pyautogui.moveTo(chat_input[0], chat_input[1], duration=0.2)
    pyautogui.click()
    
    pyautogui.write(result_str)
    pyautogui.press('enter')


def correct_coordinates(coordinates, x=0, y=0):
    return (coordinates[0] + x, coordinates[1] + y)


def write_to_chat(string):
    pyautogui.moveTo(chat_input[0], chat_input[1], duration=0.2)
    pyautogui.click()
    time.sleep(0.2)
    pyautogui.mouseDown()
    time.sleep(1)
    pyautogui.mouseUp()
    pyperclip.copy(string)
    paste = find_and_click("./static/paste.png", screen, threshold=0.7)
    while not paste:
        time.sleep(0.3)
        paste = find_and_click("./static/paste.png", screen, threshold=0.7)
    absoulte_coordinates = (screen[0] + paste[0], screen[1] + paste[1]-20)
    pyautogui.moveTo(absoulte_coordinates, duration=0.2)
    pyautogui.click()
    pyautogui.press('enter')


def eval_buff(buff_name, area):
     #search for coordinates of the construction buff
    coordinates = None
    #make are 100 px bigger in height
    area[1] -= 100
    area[3] += 100
    time_stamp_buff_command = time.time()

    soh = find_and_click("./static/alliance/soh.png", area, threshold=0.8)
    twogr = find_and_click("./static/alliance/2gr.png", area, threshold=0.8)
    fym = find_and_click("./static/alliance/fym.png", area, threshold=0.8)
    tot = find_and_click("./static/alliance/tot.png", area, threshold=0.8)

    while not soh and not twogr and not fym and not tot:
        time.sleep(0.3)
        soh = find_and_click("./static/alliance/soh.png", area, threshold=0.8)
        twogr = find_and_click("./static/alliance/2gr.png", area, threshold=0.8)
        fym = find_and_click("./static/alliance/fym.png", area, threshold=0.8)
        tot = find_and_click("./static/alliance/tot.png", area, threshold=0.8)
        if time.time() - time_stamp_buff_command > 15:
            write_to_chat("No alliance found or alliance not allowed")
            break


    if soh:
        print("Alliance: SOH")
        alliance_name = "soh"
        alliance_priority = 1
    if twogr:
        print("Alliance: 2GR")
        alliance_name = "2gr"
        alliance_priority = 1
    if fym:
        print("Alliance: FYM")
        alliance_name = "fym"
        alliance_priority = 2
    if tot:
        print("Alliance: TOT")
        alliance_name = "tot"
        alliance_priority = 2

    while not coordinates:
        time.sleep(3)
        coordinates = find_and_click("./static/coordinates.png", area, threshold=0.7)
        #if more than 10 seconds passed break
        if time.time() - time_stamp_buff_command > 15:
            break
    if coordinates:
        absoulte_coordinates = (area[0] + coordinates[0], area[1] + coordinates[1])
        absoulte_coordinates = correct_coordinates(absoulte_coordinates, -50, -30)
        pyautogui.moveTo(absoulte_coordinates, duration=0.2)
        pyautogui.click()
        time.sleep(0.5)
        copy_name = find_and_click("./static/copy_name.png", screen, threshold=0.7)

        while not copy_name:
            copy_name = find_and_click("./static/copy_name.png", screen, threshold=0.7)
            time.sleep(0.5)

        absoulte_coordinates = (screen[0] + copy_name[0], screen[1] + copy_name[1])
        pyautogui.moveTo(absoulte_coordinates, duration=0.2)
        pyautogui.click()
        time.sleep(0.2)
        #get name frome clipboard
        name = pyperclip.paste()
        print(f"Name: {name}")
        buff_requested = getattr(buffs, buff_name)
        #check if name is already in the waiting list and not active in one of the buffs
        
        if name in buffs.waiting_list[buff_name]:
            string = f"{name} is already in the {buff_name} waiting line"
            write_to_chat(string)
        elif name == buff_requested.name:
            string = f"{name} has already {buff_name} buff"
            write_to_chat(string)
            
        if name not in buffs.waiting_list[buff_name]:
            if name != buff_requested.name:
                buffs.waiting_list[buff_name].append([name, alliance_priority])
                #sort the list by alliance priority but keep the order of the same alliance priority and append the name after the last name with the same alliance priority
                buffs.waiting_list[buff_name] = sorted(buffs.waiting_list[buff_name], key=lambda x: x[1])
             
                string = f"Added {name} to {buff_name} waiting line ({create_waiting_list(buffs)[buff_name]} min)"
                write_to_chat(string)
    else:
        write_to_chat("No coordinates found")
    time.sleep(0.3)


def queue(area, command_pos):
    absoulte_coordinates = (area[0] + command_pos[0], area[1] + command_pos[1])
    absoulte_coordinates = correct_coordinates(absoulte_coordinates, -70, -40)
    pyautogui.moveTo(absoulte_coordinates, duration=0.2)
    pyautogui.click()
    time.sleep(0.5)
    copy_name = None
    while not copy_name:
        copy_name = find_and_click("./static/copy_name.png", screen, threshold=0.7)
        time.sleep(0.3)
    absoulte_coordinates = (screen[0] + copy_name[0], screen[1] + copy_name[1])
    pyautogui.moveTo(absoulte_coordinates, duration=0.2)
    pyautogui.click()
    time.sleep(0.2)
    #get name frome clipboard
    name = pyperclip.paste()
    print(f"Name: {name}")

    #look for the name in the waiting list and get position and buff type
    # name can be in multiple waiting lists so i want the lowest position

    position = None
    buff_type = None

    for key, value in buffs.waiting_list.items():
        if name in value:
            if position is None or value.index(name) < position:
                position = value.index(name)
                buff_type = key

    if position is not None:
        #create_waiting_list creates the max waiting time so need to subract the time for the current position
        time_left = create_waiting_list(buffs)[buff_type]
        time_to_subtract = len(buffs.waiting_list[buff_type]) - (position+1)
        time_left -= time_to_subtract * 10
        string = f"{name} #{position+1} in {buff_type} waiting line ({time_left} min)"
        write_to_chat(string)
    else:
        write_to_chat(f"{name} is not in any waiting line")


def execute_command(command, area, command_pos=None):
    if command == "status":
        print("Detected status")
        status()
    
    if command == "queue":
        print("Detected queue")
        queue(area, command_pos)

    if command == "construction_buff":
        print("Detected construction_buff")
        eval_buff("construction", area)
    
    if command == "research_buff":
        print("Detected research_buff")
        eval_buff("research", area)

    if command == "training_buff":
        print("Detected training_buff")
        eval_buff("training", area)

    if command == "heal_buff":
        print("Detected heal_buff")
        eval_buff("heal", area)   


def handle_chat(screen):
    #starting from the bottom are of the chat looking for commands
    #get the chat area
    DELTA = 100
    bottom_area = [screen[0], screen[1] + screen[3] - DELTA, screen[2], DELTA]
    
    command_found, command_pos = check_for_command(bottom_area)
    while not command_found:
        time.sleep(0.3)
        #check for command
        # expand the area to check
        bottom_area[1] -= DELTA
        bottom_area[3] += DELTA
        #export bottom area for debugging
        #pyautogui.screenshot(region=bottom_area).save(f"./log/chat_{LOOP}.png")
        command_found, command_pos = check_for_command(bottom_area)

        
        if bottom_area[1] < screen[1]:
            break

    if command_found:
        execute_command(command_found, bottom_area, command_pos)
        #go back to chat overview
        pyautogui.moveTo(return_button[0], return_button[1], duration=0.2)
        pyautogui.click()
        time.sleep(0.3)
    else:
        print("No command found")
        return_back = find_and_click("./static/return_back.png", screen, threshold=0.8)
        while not return_back:
            time.sleep(0.1)
            return_back = find_and_click("./static/return_back.png", screen, threshold=0.8)
            if return_back:
                break
        absoulte_coordinates = (screen[0] + return_back[0], screen[1] + return_back[1])
        pyautogui.moveTo(absoulte_coordinates, duration=0.2)
        pyautogui.click()


def naviate_to_buffs():
    pyautogui.moveTo(return_button[0], return_button[1], duration=0.2)
    pyautogui.click()
    time.sleep(0.3)
    capitol = find_and_click("./static/7.png", screen, threshold=0.8)
    while not capitol:
        time.sleep(0.5)
        capitol = find_and_click("./static/7.png", screen, threshold=0.8)
        
    absoulte_coordinates = (screen[0] + capitol[0]+50, screen[1] + capitol[1] + 200)# press a bit lower
    pyautogui.moveTo(absoulte_coordinates, duration=0.2)
    pyautogui.click()
    time.sleep(0.3)

    configure = find_and_click("./static/configure.png", screen, threshold=0.8)
    while not configure:
        time.sleep(0.3)
        configure = find_and_click("./static/configure.png", screen, threshold=0.8)
        
    
    absoulte_coordinates = (screen[0] + configure[0], screen[1] + configure[1])
    absoulte_coordinates = correct_coordinates(absoulte_coordinates, 0, -20)
    pyautogui.moveTo(absoulte_coordinates, duration=0.2)
    pyautogui.click()
    time.sleep(0.3)

    positions = find_and_click("./static/positions.png", screen, threshold=0.8)
    while not positions:
        time.sleep(0.1)
        positions = find_and_click("./static/positions.png", screen, threshold=0.8)
        

    absoulte_coordinates = (screen[0] + positions[0], screen[1] + positions[1])
    pyautogui.moveTo(absoulte_coordinates, duration=0.2)
    pyautogui.click()
    time.sleep(0.3)


def appoint_buff(buff, timestamp_appoint):
    time.sleep(0.3)
    appoint = find_and_click("./static/appoint.png", screen, threshold=0.8)
    appoint2 = find_and_click("./static/appoint2.png", screen, threshold=0.8)
    while not appoint or not appoint2:
        time.sleep(0.3)
        appoint = find_and_click("./static/appoint.png", screen, threshold=0.8)
        appoint2 = find_and_click("./static/appoint2.png", screen, threshold=0.8)
        if appoint or appoint2:
            if appoint2:
                appoint = appoint2
            break
    
    absoulte_coordinates = (screen[0] + appoint[0], screen[1] + appoint[1])
    absoulte_coordinates = correct_coordinates(absoulte_coordinates, 20, -30)
    pyautogui.moveTo(absoulte_coordinates, duration=0.2)
    pyautogui.click()
    time.sleep(0.3)

    search = find_and_click("./static/search.png", screen, threshold=0.8)
    while not search:
        time.sleep(0.3)
        search = find_and_click("./static/search.png", screen, threshold=0.8)
    
    
    absoulte_coordinates = (screen[0] + search[0], screen[1] + search[1])
    absoulte_coordinates = correct_coordinates(absoulte_coordinates, -50, 0)
    pyautogui.moveTo(absoulte_coordinates, duration=0.2)
    #click on search
    pyautogui.click()
    time.sleep(0.3)
    pyautogui.shortcut('ctrl', 'a')
    time.sleep(0.2)
    pyautogui.press('backspace')
    time.sleep(0.2)
    #copy name to clipboard
    pyperclip.copy(buff.name)
    time.sleep(0.1)
    pyautogui.shortcut('ctrl', 'v')
    time.sleep(0.3)
    
    absoulte_coordinates = correct_coordinates(absoulte_coordinates, 50,0)
    pyautogui.moveTo(absoulte_coordinates, duration=0.2)
    pyautogui.press('enter')
    pyautogui.click()
    time.sleep(1)
    absoulte_coordinates = correct_coordinates(absoulte_coordinates, -380, 90)
    pyautogui.moveTo(absoulte_coordinates, duration=0.2)
    pyautogui.click()
    time.sleep(0.2)

    appoint_final = find_and_click("./static/appoint_final.png", screen, threshold=0.8)
    while not appoint_final:
        time.sleep(0.3)
        appoint_final = find_and_click("./static/appoint_final.png", screen, threshold=0.8)
     

    absoulte_coordinates = (screen[0] + appoint_final[0], screen[1] + appoint_final[1])
    absoulte_coordinates = correct_coordinates(absoulte_coordinates, 0, -40)
    pyautogui.moveTo(absoulte_coordinates, duration=0.2)
    pyautogui.click()
    time.sleep(0.3)

    confirm = find_and_click("./static/confirm.png", screen, threshold=0.8)
    while not confirm:
        time.sleep(0.3)
        confirm = find_and_click("./static/confirm.png", screen, threshold=0.8)
      
    
    absoulte_coordinates = (screen[0] + confirm[0], screen[1] + confirm[1])
    absoulte_coordinates = correct_coordinates(absoulte_coordinates, 0, -40)
    buff.time_received = buff.time_received + (time.time() - timestamp_appoint)
    pyautogui.moveTo(absoulte_coordinates, duration=0.2)
    if not dbg:
        pyautogui.click()
        time.sleep(0.5)
       
    close = find_and_click("./static/close.png", screen, threshold=0.8)
    while not close:
        time.sleep(0.3)
        close = find_and_click("./static/close.png", screen, threshold=0.8)
    
    absoulte_coordinates = (screen[0] + close[0], screen[1] + close[1])
    pyautogui.moveTo(absoulte_coordinates, duration=0.2)
    pyautogui.click()
    time.sleep(0.5)


def navigate_to_chat():
    return_back = find_and_click("./static/return_back2.png", screen, threshold=0.8)
    while not return_back:
        time.sleep(0.1)
        return_back = find_and_click("./static/return_back2.png", screen, threshold=0.8)
    absoulte_coordinates = (screen[0] + return_back[0], screen[1] + return_back[1])
    pyautogui.moveTo(absoulte_coordinates, duration=0.2)
    pyautogui.click()
    time.sleep(0.3)
    return_back = find_and_click("./static/return_back.png", screen, threshold=0.8)
    while not return_back:
        time.sleep(0.1)
        return_back = find_and_click("./static/return_back.png", screen, threshold=0.8)
        
    
    absoulte_coordinates = (screen[0] + return_back[0], screen[1] + return_back[1])
    pyautogui.moveTo(absoulte_coordinates, duration=0.2)
    pyautogui.click()
    time.sleep(0.3)
    pyautogui.moveTo(chat[0], chat[1], duration=0.2)
    pyautogui.click()
    time.sleep(0.3)

    private_chat = find_and_click("./static/private_chat.png", screen, threshold=0.8)
    while not private_chat:
        time.sleep(0.1)
        private_chat = find_and_click("./static/private_chat.png", screen, threshold=0.8)
        

    absoulte_coordinates = (screen[0] + private_chat[0], screen[1] + private_chat[1])
    absoulte_coordinates = correct_coordinates(absoulte_coordinates, 0, -40)
    pyautogui.moveTo(absoulte_coordinates, duration=0.2)
    pyautogui.click()
    time.sleep(0.3)


def handle_buffs(buffs_to_process):
    for buff in buffs_to_process:
        timestamp_appoint = time.time()
        new_player_name = buffs.waiting_list[buff.buff_type].pop(0)[0]
        #export json file
        json.dump(buffs.waiting_list, open("waiting_list.json", "w"))
        print(f"Processing {buff.buff_type} buff for {new_player_name}")

        print(f"Appointing {new_player_name} to {buff.buff_type} buff")
        if buff.buff_type == "construction":
            pyautogui.moveTo(buffs.positions.construction.pos, duration=0.2)
            pyautogui.click()
            buffs.construction = Player(name=new_player_name, buff_type=buff.buff_type)
            appoint_buff(buffs.construction, timestamp_appoint)
            time.sleep(1)
            pyautogui.moveTo(buffs.positions.construction.pos[0], buffs.positions.construction.pos[1]-50, duration=0.2)
            pyautogui.click()
            time.sleep(0.3)
        if buff.buff_type == "research":
            pyautogui.moveTo(buffs.positions.research.pos, duration=0.2)
            pyautogui.click()
            buffs.research = Player(name=new_player_name, buff_type=buff.buff_type)
            appoint_buff(buffs.research, timestamp_appoint)
            time.sleep(1)
            pyautogui.moveTo(buffs.positions.research.pos[0], buffs.positions.research.pos[1]-50, duration=0.2)
            pyautogui.click()
            time.sleep(0.3)
        if buff.buff_type == "training":
            pyautogui.moveTo(buffs.positions.training.pos, duration=0.2)
            pyautogui.click()
            buffs.training = Player(name=new_player_name, buff_type=buff.buff_type)
            appoint_buff(buffs.training, timestamp_appoint)
            time.sleep(1)
            pyautogui.moveTo(buffs.positions.training.pos[0], buffs.positions.training.pos[1]-50, duration=0.2)
            pyautogui.click()
            time.sleep(0.3)
        if buff.buff_type == "heal":
            pyautogui.moveTo(buffs.positions.heal.pos, duration=0.2)
            pyautogui.click()
            buffs.heal = Player(name=new_player_name, buff_type=buff.buff_type)
            appoint_buff(buffs.heal, timestamp_appoint)
            time.sleep(1)
            pyautogui.moveTo(buffs.positions.heal.pos[0], buffs.positions.heal.pos[1]-50, duration=0.2)
            pyautogui.click()
            time.sleep(0.3)
        
        chat = find_and_click("./static/chat.png", screen, threshold=0.8)
        while not chat:
            time.sleep(0.1)
            chat = find_and_click("./static/chat.png", screen, threshold=0.8)
        
        absoulte_coordinates = (screen[0] + chat[0], screen[1] + chat[1])
        absoulte_coordinates = correct_coordinates(absoulte_coordinates, 0, -40)
        pyautogui.moveTo(absoulte_coordinates, duration=0.2)
        pyautogui.click()
        time.sleep(0.3)
        write_to_chat(f"{new_player_name} GO!")
        time.sleep(0.3)
        #press on return button
        pyautogui.moveTo(return_button[0], return_button[1], duration=0.2)
        pyautogui.click()
        time.sleep(0.3)


def main(dbg=False):

    if dbg:
        print("Construction: ", buffs.positions.construction.pos)
        print("Research: ",  buffs.positions.research.pos)
        print("Training: ", buffs.positions.training.pos)
        print("Heal: ", buffs.positions.heal.pos)
    searching_switch = True
    while True:
        # Finden und Klicken Sie auf das Bild
        if searching_switch:
            print("Searching for new message")
            searching_switch = False
        new_message = find_and_click("./static/new_message.png", screen)
        if new_message:
            #mark found area
            absolute_coordinates = (screen[0] + new_message[0], screen[1] + new_message[1])
            pyautogui.moveTo(absolute_coordinates[0], absolute_coordinates[1], duration=0.2)
            #click on chat
            pyautogui.click()
            time.sleep(0.3)
            handle_chat(screen)
            #export json file
            json.dump(buffs.waiting_list, open("waiting_list.json", "w"))

        buffs_to_process = buffs.check()
        if len(buffs_to_process) > 0:
            naviate_to_buffs()
            handle_buffs(buffs_to_process)
            #navigate_to_chat()
            searching_switch = True
        
        time.sleep(3)
        if keyboard.is_pressed('q'):
            break      

if __name__ == "__main__":
    global dbg
    dbg = False

    #for dbg
    global chat_input
    global return_button
    global screen
    global chat
    global position_settings
    global buffs

    waiting_list = json.load(open("waiting_list.json", "r"))
    position_settings = json.load(open("position_settings.json", "r"))
    

    screen = Position(2, coordinates=position_settings["screen"], info="screen")
    screen = screen.pos
    print("Screen: ", screen)

    chat_input = Position(1, coordinates=position_settings["chat_input"], info="chat_input")
    chat_input = chat_input.pos
    print("Chat input: ", chat_input)

    return_button = Position(1, coordinates=position_settings["return_button"], info="return_button")
    return_button = return_button.pos
    print("Return button: ", return_button)

    chat = Position(1, coordinates=position_settings["chat"], info="chat")
    chat = chat.pos
    print("Chat: ", chat)
    print("Naviate to buffs overview if calibration is needed")
    time.sleep(5)
    buffs = Buffs(waiting_list)
    #export json file
    json.dump(position_settings, open("position_settings.json", "w"))
    main(dbg)