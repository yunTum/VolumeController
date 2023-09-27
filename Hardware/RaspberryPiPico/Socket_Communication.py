import network
import socket
import machine
from time import sleep
from picozero import pico_temp_sensor, pico_led
ssid = ''
password = ''
# Wi-Fi 接続実行関数   
def connect():
    wlan = network.WLAN(network.STA_IF)      # WLANオブジェクトを作成
    wlan.active(True)                        # WLANインタフェースを有効化
    wlan.connect(ssid, password)             # 指定されたSSIDとパスワードでWi-Fiに接続する

    while wlan.isconnected() == False:       # Wi-Fi接続が確立されるまで待機
        print('Waiting for connection...')
        sleep(1)

    print(wlan.ifconfig())                   # Wi-Fi接続情報を全て出力
    ip = wlan.ifconfig()[0]                  # IPアドレスのみを取得
    print(f'Connected IP: {ip}')             # IPアドレスを出力
    return ip                                # IPアドレスを返す

#  ソケットを開く関数
def open_socket(ip):
    address = (ip, 8080)            # IPアドレスとポート番号のタプルを作成
    connection = socket.socket()   # ソケットオブジェクトを作成
    connection.bind(address)       # IPアドレスとポート番号をバインド
    connection.listen(1)           # 接続待機
    print(connection)              # ソケットオブジェクトを出力
    return connection              # ソケットオブジェクトを返す

def serve(client):
    # 初期状態を設定
    state = 'OFF'
    pico_led.off()
    sensor_1 = machine.ADC(0)
    sensor_2 = machine.ADC(1)
    sensor_3 = machine.ADC(2)
    conversion_factor = 1024 / (65535)
    tct_val = 0
    tggl_state = False
    tggl_val = 0
    vlm_val = 0
    
    while True:
        tct_val = int(sensor_1.read_u16() * conversion_factor)
        tggl_val = int(sensor_2.read_u16() * conversion_factor)
        vlm_val = int(sensor_3.read_u16() * conversion_factor)
        send_data = ""
        if( tggl_val > 512):
            tggl_state = True
        else:
            tggl_state = False
        if ( (tct_val < 100) & tggl_state ):
            send_data += "#tct1,"
        elif ( (400 < tct_val) & (tct_val < 570) & tggl_state ):
            send_data += "#tct2,"
        elif ( (600 < tct_val) & (tct_val < 800) &  tggl_state ):
            send_data += "#tct3,"
        elif ( (tct_val < 100) & (not tggl_state) ):
            send_data += "#tct4,"
        elif ( (400 < tct_val) & (tct_val < 570) & (not tggl_state) ):
            send_data += "#tct5,"
        elif ( (600 < tct_val) & (tct_val < 800) & (not tggl_state) ):
            send_data += "#tct6,"
        else:
            send_data += "#default,"
        if ( tggl_state ):
            send_data += "#sw1:"
        elif ( not tggl_state ):
            send_data += "#sw2:"
        send_data += str(vlm_val) + ",\r\n"
        try:
            client.send(send_data)
        except:
            client.close()
            machine.reset()       # Picoを再起動する
        pico_led.on()             # 本体LEDをオンにする
        sleep(0.3)
        pico_led.off()            # 本体LEDをオフにする


# メイン処理
try:
    ip = connect()                  # Wi-Fiに接続し、IPアドレスを取得する
    connection = open_socket(ip)    # IPアドレスを使用してソケットを開く
    client = connection.accept()[0]
    serve(client)
except KeyboardInterrupt:
    machine.reset()                 # 停止（Ctrl-C）が押されたときにPicoを再起動する

