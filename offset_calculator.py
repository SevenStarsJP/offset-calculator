import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import csv
import json
import os

# 入力が16進数であるかをチェックする関数
def is_hex(value):
    try:
        int(value, 16)  # 16進数に変換できるか確認
        return True
    except ValueError:
        return False

# オフセット計算関数
def calculate_offset(base_address=None, offset=None):
    if base_address is None or offset is None:
        base_address = entry_base.get()  # 基準アドレスを取得
        offset = entry_offset.get()  # オフセットを取得

    # 16進数を整数に変換して計算
    base_address_int = int(base_address, 16)
    offset_int = int(offset, 16)
    new_address = base_address_int + offset_int

    # 結果を表示
    result.set(f"新しいアドレス: {hex(new_address)}")

    # 計算履歴に追加
    history_list.insert(0, f"基準: {base_address}, オフセット: {offset} -> 結果: {hex(new_address)}")
    save_history()  # 計算結果を履歴として保存

# 計算結果をクリップボードにコピーする関数
def copy_to_clipboard():
    root.clipboard_clear()  # クリップボードをクリア
    root.clipboard_append(result.get())  # 結果をクリップボードにコピー
    messagebox.showinfo("コピー完了", "計算結果がクリップボードにコピーされました")

# 入力欄のリアルタイム検証とエラーメッセージの表示
def validate_input():
    base_value = entry_base.get()
    offset_value = entry_offset.get()

    valid_base = is_hex(base_value) or base_value == ""
    valid_offset = is_hex(offset_value) or offset_value == ""

    # 基準アドレスのエラーメッセージ
    if not valid_base:
        error_label_base.config(text="無効な16進数です", foreground="red")
    else:
        error_label_base.config(text="")  # エラーなしの場合はラベルをクリア

    # オフセットのエラーメッセージ
    if not valid_offset:
        error_label_offset.config(text="無効な16進数です", foreground="red")
    else:
        error_label_offset.config(text="")  # エラーなしの場合はラベルをクリア

    # 両方の入力が有効な場合のみ計算ボタンを有効化
    if valid_base and valid_offset and base_value != "" and offset_value != "":
        calculate_button.config(state=tk.NORMAL)
    else:
        calculate_button.config(state=tk.DISABLED)

# 履歴から再計算する関数
def recalculate_from_history(event):
    selected = history_list.get(history_list.curselection())  # 選択された履歴項目を取得
    parts = selected.split(" -> ")[0].split(", ")
    base_address = parts[0].split(": ")[1]
    offset = parts[1].split(": ")[1]
    calculate_offset(base_address, offset)

# 履歴をファイルに保存
def save_history():
    history = history_list.get(0, tk.END)
    with open("history.json", "w") as f:
        json.dump(list(history), f)

# 履歴をファイルから読み込み
def load_history():
    if os.path.exists("history.json"):
        with open("history.json", "r") as f:
            history = json.load(f)
            for item in history:
                history_list.insert(tk.END, item)

# 複数のオフセットを計算する関数
def calculate_multiple_offsets():
    base_address = entry_base.get()
    offsets = entry_offset.get().split(',')
    results = []

    for offset in offsets:
        if is_hex(offset.strip()):
            base_address_int = int(base_address, 16)
            offset_int = int(offset.strip(), 16)
            new_address = base_address_int + offset_int
            results.append(f"オフセット {offset.strip()} -> 結果: {hex(new_address)}")

    result.set("\n".join(results))

# テーマ変更関数
def change_theme(event):
    selected_theme = theme_var.get()
    style.theme_use(selected_theme)

# CSVへの履歴保存
def export_history_to_csv():
    filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if filepath:
        with open(filepath, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(["基準アドレス", "オフセット", "結果"])
            for item in history_list.get(0, tk.END):
                parts = item.split(" -> ")
                base_offset = parts[0].split(", ")
                result = parts[1]
                csvwriter.writerow([base_offset[0].split(": ")[1], base_offset[1].split(": ")[1], result])

# メインウィンドウの作成
root = tk.Tk()
root.title("オフセット計算機")
root.geometry("500x600")

# カスタムデザインのために ttk を使用
style = ttk.Style()
style.theme_use("clam")  # カスタムテーマを使用

# 基準アドレスの入力欄とリアルタイムエラーメッセージ
ttk.Label(root, text="基準アドレス (16進)").pack(pady=5)
entry_base = ttk.Entry(root)
entry_base.pack(pady=5)
error_label_base = ttk.Label(root, text="", foreground="red")
error_label_base.pack()

# オフセットの入力欄とリアルタイムエラーメッセージ
ttk.Label(root, text="オフセット (16進, カンマ区切りで複数指定)").pack(pady=5)
entry_offset = ttk.Entry(root)
entry_offset.pack(pady=5)
error_label_offset = ttk.Label(root, text="", foreground="red")
error_label_offset.pack()

# 結果を表示するためのラベル
result = tk.StringVar()
ttk.Label(root, textvariable=result).pack(pady=10)

# 計算ボタン
calculate_button = ttk.Button(root, text="計算", command=calculate_multiple_offsets)
calculate_button.pack(pady=5)
calculate_button.config(state=tk.DISABLED)  # 初期状態では無効化

# コピーするボタン
copy_button = ttk.Button(root, text="コピー", command=copy_to_clipboard)
copy_button.pack(pady=5)

# 履歴表示用のリストボックス
ttk.Label(root, text="計算履歴").pack(pady=5)
history_list = tk.Listbox(root, height=5)
history_list.pack(pady=5)
history_list.bind("<Double-1>", recalculate_from_history)  # 履歴の項目をダブルクリックで再計算

# テーマ選択用ドロップダウンメニュー
ttk.Label(root, text="テーマ選択").pack(pady=5)
theme_var = tk.StringVar(value="clam")
theme_menu = ttk.Combobox(root, textvariable=theme_var, values=style.theme_names(), state="readonly")
theme_menu.pack(pady=5)
theme_menu.bind("<<ComboboxSelected>>", change_theme)

# CSVエクスポートボタン
ttk.Button(root, text="CSVとして保存", command=export_history_to_csv).pack(pady=5)

# 入力欄の内容が変更されたときにリアルタイムで入力を検証
entry_base.bind("<KeyRelease>", lambda event: validate_input())
entry_offset.bind("<KeyRelease>", lambda event: validate_input())

# ホットキーのバインド
root.bind("<Control-c>", lambda event: copy_to_clipboard())  # Ctrl+Cでコピー
root.bind("<Control-r>", lambda event: calculate_multiple_offsets())  # Ctrl+Rで再計算

# アプリケーションのループを開始
load_history()  # 起動時に履歴を読み込む
root.mainloop()
