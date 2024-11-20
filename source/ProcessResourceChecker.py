#==========================================#
#
#  プロセス毎の負荷状況をチェックする
#  作成者：セイカ
#  作成日：2024/11/20
#
#==========================================#

#★import群================================#
import psutil       #プロセスチェック用
import csv          #CSV出力用
import configparser #パラメータ読込用
import os           #ファイル存在チェック用
import sys          #アプリ制御用
import datetime     #日付操作用
import threading    #並列処理用
from tkinter import messagebox

#★定数群==================================#
#設定ファイル
SETTING_FILENAME = "setting.ini"
#セクション
SECTION_LOG      = "SECTION-LOG"
#キー値
KEY_PATH         = "LOG_PATH"

#★関数群==================================#
def CheckProcess(_sysdate, _systime, _proc, _logWriter):
    #プロセス情報格納用
    process_list = list()
    process_list.clear()
    try:
        #情報取得
        process       = psutil.Process(_proc.pid)

        cpu_usage     = process.cpu_percent(interval=1)
        memory_info   = process.memory_info()
        memory_rss_mb = memory_info.rss / 1024 / 1024
        memory_vms_mb = memory_info.vms / 1024 / 1024
        #ログ出力用リスト格納
        process_list.append(sys_date)               #日付
        process_list.append(sys_time)               #時間
        process_list.append(str(_proc.pid))              #プロセスID
        process_list.append(_proc.name())                #プロセス名
        process_list.append(_proc.exe())                 #実行ファイル
        process_list.append(f"{float(cpu_usage):.2f}")     #CPU使用率
        process_list.append(f"{float(memory_rss_mb):.2f}") #RSS(Resident Set Size)   物理メモリを占有しているサイズ[MB]
        process_list.append(f"{float(memory_vms_mb):.2f}") #VMS(Virtual Memory Size) 仮想メモリの総量[MB]
        #ログ出力
        _logWriter.writerow(process_list)

    #例外：アクセス権が無い
    except psutil.AccessDenied:
        process_list.clear()
        #ログ出力用リスト格納
        process_list.append(sys_date)      #日付
        process_list.append(sys_time)      #時間
        process_list.append(str(_proc.pid))     #プロセスID
        process_list.append("アクセス権が無いため、出力できませんでした")
        process_list.append("None")
        process_list.append("None")
        process_list.append("None")
        process_list.append("None")
        #ログ出力
        _logWriter.writerow(process_list)

    #例外：プロセスが既に終了していた
    except psutil.NoSuchProcess:
        process_list.clear()
        #ログ出力用リスト格納
        process_list.append(sys_date)      #日付
        process_list.append(sys_time)      #時間
        process_list.append(str(_proc.pid))     #プロセスID
        process_list.append("プロセスが既に終了しているため、出力できませんでした")
        process_list.append("None")
        process_list.append("None")
        process_list.append("None")
        process_list.append("None")
        #ログ出力
        _logWriter.writerow(process_list)



#★初期処理群==============================#
#ConfigParserオブジェクトを生成
config = configparser.ConfigParser()
#設定ファイルのパス取得(実行ファイルと同じ階層)
settingFilePath = os.path.dirname(sys.argv[0]) + '\\'
#デバッグ用
#settingFilePath = os.path.dirname(os.path.abspath(__file__)) + '\\'
#設定ファイル読込
config.read(settingFilePath + SETTING_FILENAME)
#エラーメッセージ格納用
errorMessage = ""


#●エラーチェック(設定ファイル存在チェック)～#
if os.path.isfile(settingFilePath + SETTING_FILENAME) == False:
    errorMessage = "設定ファイルが見つかりませんでした。プログラム終了します。\n"
    errorMessage = errorMessage + "参照ファイル：" + settingFilePath + SETTING_FILENAME
    messagebox.showerror("!!ファイル存在チェックエラー!!",errorMessage)
    sys.exit()

#●設定ファイル読込～～～～～～～～～～～～～#
#ログファイルパス読込
logPath = config[SECTION_LOG][KEY_PATH]
#パス編集(「"」を削除)
logPath      = logPath.replace('"','')
#ヘッダー情報格納用
header_list = list()
header_list.clear()
#ファイルが存在しない場合は、ヘッダー情報を出力する
if os.path.isfile(logPath) == False:
    header_list.append("日付")
    header_list.append("時間")
    header_list.append("プロセスID")
    header_list.append("プロセス名")
    header_list.append("実行ファイル")
    header_list.append("CPU使用率")
    header_list.append("RSS(Resident Set Size)[MB]")
    header_list.append("VMS(Virtual Memory Size)[MB]")
#ログファイル出力準備
logfile      = open(logPath,'a', newline="")
logWriter    = csv.writer(logfile)

#ヘッダー情報があれば、出力する
if len(header_list) > 0:
    logWriter.writerow(header_list)

#●メイン処理～～～～～～～～～～～～～～～～#
# 各プロセスを監視するスレッドを作成
threads = []

#プロセス分ループ
for proc in psutil.process_iter():
    # 日付を取得する
    sys_date = datetime.datetime.now().strftime('%Y/%m/%d')
    sys_time = datetime.datetime.now().strftime('%H:%M')
    thread = threading.Thread(target=CheckProcess, args=(sys_date, sys_time, proc, logWriter))
    threads.append(thread)
    thread.start()

# スレッドの終了を待機
for thread in threads:
    thread.join()



