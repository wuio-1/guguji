#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
弹窗雨 v2 —— 恶搞专用（致敬 新建 Python File (12).py）
=========================================================
原版的问题：100 个窗口一次性全出来（卡一下，瞬间铺满，少点戏剧性）
v2 的改动：
  * 弹窗一个个"陆续"冒出来（每 45ms 一个），像下雨 🌧️
  * 每个弹窗置顶（topmost），关掉也压不住
  * 标题带计数（第 37/100 个），绝望感拉满
  * 前 10 个带系统提示音，后面静音（别把人吵死）
  * 文字轮换，不会 100 个都说同一句
  * 隐藏逃生钥匙：连按 3 次 ESC → 关掉全部 + 揭晓真相
     （比 Ctrl+Alt+Del 体面一点 😄）

用法：
    python 弹窗雨_v2.py            # 正片：100 个
    python 弹窗雨_v2.py --demo     # 演示：只弹 5 个
    python 弹窗雨_v2.py --n 30     # 自定义数量

注意：本脚本不会真的动任何文件，纯窗口恶搞。
"""

import ctypes
import random
import sys
import tkinter as tk

try:
    import winsound
except ImportError:            # 非 Windows 平台也能跑（没声音而已）
    winsound = None

msg_box = ctypes.windll.user32.MessageBoxW      # Windows 原生对话框 ✅

MB_YESNO = 4
MB_ICONWARNING = 0x30
MB_ICONINFORMATION = 0x40
IDYES = 6

TEXTS = [
    "你是不是想杀了我？",
    "我还能再抢救一下……",
    "求你了，我只是个系统",
    "删我 Windows 文件夹干嘛",
    "内存条已离家出走",
    "正在把你刚才的操作上报给微软",
    "你的 Chrome 已经打开 247 个标签页了",
    "再点我就真哭了 (╥﹏╥)",
    "错误代码：WHY_ARE_YOU_LIKE_THIS",
    "建议你喝口水冷静一下",
]

esc_count = [0]


def main():
    total = 100
    if "--demo" in sys.argv:
        total = 5
    if "--n" in sys.argv:
        try:
            total = max(1, min(300, int(sys.argv[sys.argv.index("--n") + 1])))
        except (ValueError, IndexError):
            pass

    # ---- 开场：真正的系统对话框 ----
    res = msg_box(
        0,
        "要不要删除 Windows 文件夹？\n\n"
        "（点击【是】继续，点击【否】保平安）",
        "系统警告",
        MB_YESNO | MB_ICONWARNING,
    )
    if res != IDYES:
        msg_box(0, "明智的选择。\n祝你今天不蓝屏 🙂", "提示", MB_ICONINFORMATION)
        return

    # ---- 正片 ----
    root = tk.Tk()
    root.withdraw()                                   # 藏起主窗口
    root.title("系统错误")

    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()

    windows = []
    made = [0]
    closed = [False]

    def close_all(reveal=True):
        if closed[0]:
            return
        closed[0] = True
        for w in windows:
            try:
                w.destroy()
            except tk.TclError:
                pass
        if reveal:
            def _reveal():
                msg_box(0,
                        "骗你的 😄\n\n"
                        "一个文件都没删，你的 Windows 文件夹完好无损。\n"
                        "（求你别真的去删它）",
                        "真相", MB_ICONINFORMATION)
                root.destroy()
            root.after(250, _reveal)
        else:
            root.destroy()

    def spawn():
        if closed[0]:
            return
        if made[0] >= total:
            return                                    # 出完了，让它赖在屏幕上

        made[0] += 1
        idx = made[0]
        w, h = 340, 152
        x = random.randint(0, max(0, sw - w))
        y = random.randint(0, max(0, sh - h - 70))    # 避开任务栏

        win = tk.Toplevel(root)
        win.title(f"系统错误 ({idx}/{total})")
        win.geometry(f"{w}x{h}+{x}+{y}")
        win.resizable(False, False)
        try:
            win.attributes("-topmost", True)          # 置顶，压不住 😈
        except tk.TclError:
            pass
        windows.append(win)

        # 仿 Win11 报错布局
        frame = tk.Frame(win)
        frame.pack(pady=(18, 6), padx=14)

        tk.Label(frame, text="✖", fg="#c42b1c", font=("Segoe UI", 26)).grid(
            row=0, column=0, padx=(0, 12), sticky="n")
        tk.Label(frame, text=TEXTS[(idx - 1) % len(TEXTS)],
                 font=("Microsoft YaHei", 10), justify="left", wraplength=230).grid(
            row=0, column=1, sticky="w")

        tk.Button(win, text="确定", width=9,
                  command=lambda: _dismiss(win)).pack(pady=(2, 10))

        # 前 10 个带系统提示音，后面静音
        if winsound is not None and idx <= 10:
            try:
                winsound.MessageBeep(0x30)
            except Exception:
                pass

        root.after(45, spawn)                        # 45ms 后下一个 → 弹窗雨 🌧️

    def _dismiss(win):
        try:
            win.destroy()
        except tk.TclError:
            pass

    # ---- 逃生钥匙：连按 3 次 ESC ----
    def on_esc(_e=None):
        esc_count[0] += 1
        if esc_count[0] >= 3:
            close_all()

    root.bind_all("<Escape>", on_esc)
    root.bind_all("<Button-1>", lambda _e: esc_count.__setitem__(0, 0))

    root.after(120, spawn)                            # 稍微等一下再开始
    root.mainloop()


if __name__ == "__main__":
    main()
