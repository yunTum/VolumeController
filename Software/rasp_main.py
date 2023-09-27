"""
SimpleVolumeController.
raspberry pi pico
"""
#!/usr/bin/env python
import time
import pyautogui
import math
import threading
from pycaw.pycaw import AudioUtilities
from pystray import Icon,Menu,MenuItem
from PIL import Image
import socket

class AudioController:
  def __init__(self, process_name):
    self.process_name = process_name
    self.volume = self.process_volume()

  def mute(self):
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
      interface = session.SimpleAudioVolume
      if session.Process and session.Process.name() == self.process_name:
        interface.SetMute(1, None)
        print(self.process_name, "has been muted.")  # debug

  def unmute(self):
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
      interface = session.SimpleAudioVolume
      if session.Process and session.Process.name() == self.process_name:
        interface.SetMute(0, None)
        print(self.process_name, "has been unmuted.")  # debug

  def process_volume(self):
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
      interface = session.SimpleAudioVolume
      if session.Process and session.Process.name() == self.process_name:
        print("Volume:", interface.GetMasterVolume())  # debug
        return interface.GetMasterVolume()

  def set_volume(self, decibels):
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
      interface = session.SimpleAudioVolume
      if session.Process and session.Process.name() == self.process_name:
        # only set volume in the range 0.0 to 1.0
        self.volume = min(1.0, max(0.0, decibels))
        interface.SetMasterVolume(self.volume, None)
        print("Volume set to", self.volume)  # debug

  def decrease_volume(self, decibels):
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
      interface = session.SimpleAudioVolume
      if session.Process and session.Process.name() == self.process_name:
        # 0.0 is the min value, reduce by decibels
        self.volume = max(0.0, self.volume - decibels)
        interface.SetMasterVolume(self.volume, None)
        print("Volume reduced to", self.volume)  # debug

  def increase_volume(self, decibels):
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
      interface = session.SimpleAudioVolume
      if session.Process and session.Process.name() == self.process_name:
        # 1.0 is the max value, raise by decibels
        self.volume = min(1.0, self.volume + decibels)
        interface.SetMasterVolume(self.volume, None)
        print("Volume raised to", self.volume)  # debug

class SystemTrayIcon:
  def __init__(self):
    self.icon = None
    self.thread = threading.Thread(target=self.tasktray_create)
    self.thread.start()
    self.com_hard = CommicationHard()
    self.com_hard.connect()
  
  def tasktray_create(self):
    try:
      item=[]
      options_map = {'Test': lambda: self.tasktray_test(),'Quit': lambda: self.tasktray_abort()}

      for option,callback in options_map.items():
        item.append( MenuItem(option,callback,default=True if option == 'Show' else False ) )
        
      menu = Menu(*item)

      image = Image.open("app.ico")
      self.icon = Icon("name",image,"My System Tray Icon", menu)
      self.icon.run()
    finally:
      self.tasktray_abort()

  def tasktray_test(self):
      print("TaskTray Test")
      
  def tasktray_abort(self):
    if self.icon != 0:
      self.icon.stop()
      self.com_hard.set_end_status(False)

class SocketClient:
  IPADDR = "192.168.40.60"
  PORT = 8080
  def __init__(self):
    self.sock = socket.socket(socket.AF_INET)
    
  def connect(self):
    status = True
    timeout_count = 0
    while status:
      try:
        print("Connecting...")
        self.sock.connect((self.IPADDR, self.PORT))
        self.recv()
        status = False
        return True
      except:
        print("Connect error")
        time.sleep(1)
        if timeout_count > 5:
          print("Timeout error")
          status = False
          return False
        timeout_count += 1
        
    
  def recv(self):
    # ソケットから byte 形式でデータ受信
    data = self.sock.recv(128)
    return data

class CommicationHard:
  def __init__(self):
    self.chrome_audio_controller = AudioController("chrome.exe")
    self.firefox_audio_controller = AudioController("firefox.exe")
    self.action = ""
    self.vlm_val = 0
    self.pre_vlm_val = 0
    self.delta_vlm = 1/1023
    self.end_status = True
    self.theard = threading.Thread(target=self.run)
    self.switch = ""
    self.socket_client = SocketClient()
  
  def connect(self):
    if(self.socket_client.connect()):
      self.theard.start()

  def get_signal(self):
    tmp_val = 0
    val_rasp = self.socket_client.recv()
    val_rasp = val_rasp.decode('utf-8')
    split_val = val_rasp.split(',')
    if(len(split_val) > 1):
      # ボリュームの初期値を取得
      self.action = split_val[0]
      self.pre_vlm_val = self.vlm_val
      # ボリューム値を取得
      tmp_val = split_val[1].replace('\r\n', '')
      self.switch, self.vlm_val = tmp_val.split(':')
      self.vlm_val = int(self.vlm_val)
      self.vlm_val = math.floor(self.vlm_val * self.delta_vlm * 100) / 100
          
  def run(self):
    while(self.end_status):
      try:
        self.get_signal()
        if self.action == '#tct1':
          print("tct1ボタンが押されました")
          pyautogui.hotkey("ctrl", "shift", "l")
        if self.action == '#tct2':
          print("tct2ボタンが押されました")
          pyautogui.hotkey("win", "tab")
        if self.action == '#tct3':
          print("tct3ボタンが押されました")
          pyautogui.keyDown('playpause')
        if self.action == '#tct4':
          print("tct4ボタンが押されました")
        if self.action == '#tct5':
          print("tct5ボタンが押されました")     
        if self.action == '#tct6':
          print("tct6ボタンが押されました")
        # vlm_valの変更があった場合、処理を実行
        if self.vlm_val != self.pre_vlm_val:
          if self.switch == '#sw1':
            self.chrome_audio_controller.set_volume(self.vlm_val)
          elif self.switch == '#sw2':
            self.firefox_audio_controller.set_volume(self.vlm_val)
          # 待機時間: 0.05秒
        time.sleep(0.05)
      except KeyboardInterrupt:
        print("例外'KeyboardInterrupt'")
        self.theard.join()
    print("処理を終了します")
  
  def set_end_status(self, status):
    self.end_status = status

def main():
  tray = SystemTrayIcon()

if __name__ == "__main__":
  main()