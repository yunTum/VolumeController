# VolumeController
## ソフトウェア
### 起動方法
main.pyを起動し、ハードウェア側とシリアル通信で監視させる。

### exe化
作業ディレクトリで
```
pyinstaller main.py
```

## ハードウェア
前提
　Arduino IDEから、Arduinoにプログラムを書き込み済みであること

Arduino UNO等のANALOG INにそれぞれ入力する。
A0：トグルスイッチ
A1：タクトスイッチ
A2：ボリューム

### 回路図
![スクリーンショット 2023-07-10 232243](https://github.com/yunTum/VolumeController/assets/34528586/691acfe1-de45-436d-8b56-03ab8100768b)

## 操作
トグルスイッチを切り替えることで、6チャンネル＋ボリュームの操作が可能
