"""
SimpleVolumeController.
"""
#!/usr/bin/env python
import time
from pycaw.pycaw import AudioUtilities
import pyautogui
import serial
from PIL import Image
from pystray import Icon, Menu, MenuItem
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

def main():
    try:
        '''
            Arduinoのシリアルポートを指定
            ボーレート: 115200
            COMポート: COM3
        '''
        ser = serial.Serial('COM3', 115200, timeout=0.1)
    except:
        print("Serial not found")
    
    # def quit_app():
    #     icon.stop()
    # def run_app():
    #     pass
    # image = Image.open('e.ico')
    # menu = Menu(MenuItem('Quit', quit_app), MenuItem('Run', run_app))
    # icon = Icon(name='test', icon=image, title='pystray App', menu=menu)
    # icon.run()
    audio_controller = AudioController("chrome.exe")
    action = ""
    vlm_val = 0
    pre_vlm_val = 0
    delta_vlm = 1/1023
    
    try:
        val_arduino = ser.readline()
        val_arduino = val_arduino.decode('utf-8')
        split_val = val_arduino.split(',')
        if(len(split_val) > 1): 
            # ボリュームの初期値を取得
            vlm_val = int(split_val[1].replace('\r\n', ''))
        # 接続待ちにするために2.5秒待機
        print("接続待ちにするために2.5秒待機")
        time.sleep(2.5)
        print("接続待ち終了")
        while(True):
            val_arduino = ser.readline()
            val_arduino = val_arduino.decode('utf-8')
            split_val = val_arduino.split(',')
            if(len(split_val) > 1):
                action = split_val[0]
                pre_vlm_val = vlm_val
                # ボリューム値を取得
                vlm_val = int(split_val[1].replace('\r\n', ''))
                
            if action == '#tct2':
                print("tct2ボタンが押されました")
                audio_controller.increase_volume(0.01)
                
            if action == '#tct1':
                print("tct1ボタンが押されました")
                audio_controller.decrease_volume(0.01)
            
            if action == '#tct3':
                print("tct3ボタンが押されました")
                pyautogui.keyDown('playpause')
            
            if action == '#tct4':
                print("tct4ボタンが押されました")
                
            if action == '#tct5':
                print("tct5ボタンが押されました")
                
            if action == '#tct6':
                print("tct6ボタンが押されました")
            
            # vlm_valの変更があった場合、処理を実行
            if vlm_val != pre_vlm_val:
                audio_controller.set_volume(vlm_val * delta_vlm)
            # 待機時間: 0.05秒
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        print("例外'KeyboardInterrupt'")
        ser.close()
    print("処理を終了します")


if __name__ == "__main__":
    main()