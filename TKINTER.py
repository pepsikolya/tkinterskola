import tkinter as tk
from PIL import Image, ImageTk
from pygame import mixer
import os
import random
import math

def main():
    mixer.init()

    sound_path = "happy.mp3"
    happy_phonk_path = "67.mp3"

    root = tk.Tk()
    root.title("President Clicker: Phonk Edition")
    root.geometry("1920x1080")
    root.resizable(False, False)
    root.configure(bg="#0a0a0a")

    # ─── Herní proměnné ───
    max_hp = 100
    current_hp = max_hp
    time_left = 30          
    game_active = False
    click_count = 0

    # ─── Pohyb prezidenta ───
    pres_x = 800
    pres_y = 400
    move_dx = random.choice([-1, 1]) * 6
    move_dy = random.choice([-1, 1]) * 6
    move_job = None

    PRES_W, PRES_H = 220, 310

    # ─── Načtení obrázků ───
    def load_img(path, size):
        if os.path.exists(path):
            img = Image.open(path).resize(size, Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        return None

    bg_photo   = load_img("whitehouse.png", (1920, 1080))
    pres_photo = load_img("sigma.png",      (PRES_W, PRES_H))
    exp_photo  = load_img("explosion.png",  (1920, 1080))
    evil_photo = load_img("evil_president.png", (1920, 1080))

    # ─── Canvas ───
    canvas = tk.Canvas(root, width=1920, height=1080, highlightthickness=0, bg="#0a0a0a")
    canvas.pack()

    # Pozadí
    if bg_photo:
        canvas.create_image(0, 0, anchor="nw", image=bg_photo, tags="bg")
    else:
        canvas.create_rectangle(0, 0, 1920, 1080, fill="#0a0a0a", tags="bg")

    # Tmavý overlay
    canvas.create_rectangle(0, 0, 1920, 1080, fill="#000000", stipple="gray50", tags="overlay")

    # ─── START SCREEN ───
    start_frame = tk.Frame(root, bg="#0a0a0a", bd=0)
    canvas.create_window(960, 540, window=start_frame, tags="start_screen")

    tk.Label(
        start_frame,
        text="PRESIDENT CLICKER",
        font=("Courier New", 62, "bold"),
        fg="#ff2222", bg="#0a0a0a", pady=10,
    ).pack()

    tk.Label(
        start_frame,
        text="Kolja, Jáchym",
        font=("Courier New", 28, "bold"),
        fg="#ff8800", bg="#0a0a0a", pady=4,
    ).pack()

    tk.Label(
        start_frame,
        text="Klikni 100× na prezidenta za 30 sekund.\nPohybuje se — buď rychlý!",
        font=("Courier New", 20),
        fg="#cccccc", bg="#0a0a0a", pady=16, justify="center",
    ).pack()

    start_btn = tk.Button(
        start_frame,
        text="ZAČÍT HRU",
        font=("Courier New", 30, "bold"),
        fg="#000000", bg="#ff2222",
        activebackground="#ff6666", activeforeground="#000000",
        relief="flat", cursor="hand2",
        padx=40, pady=18, bd=0,
    )
    start_btn.pack(pady=30)

    # ─── HP BAR ───
    HP_BAR_X, HP_BAR_Y = 60, 30
    HP_BAR_W, HP_BAR_H = 420, 42

    canvas.create_text(
        HP_BAR_X, HP_BAR_Y - 6,
        text="HP PREZIDENTA", anchor="sw",
        font=("Courier New", 14, "bold"), fill="#ff4444", tags="ui",
    )
    canvas.create_rectangle(
        HP_BAR_X, HP_BAR_Y,
        HP_BAR_X + HP_BAR_W, HP_BAR_Y + HP_BAR_H,
        fill="#1a1a1a", outline="#ff2222", width=3, tags="ui",
    )
    hp_fill = canvas.create_rectangle(
        HP_BAR_X + 3, HP_BAR_Y + 3,
        HP_BAR_X + HP_BAR_W - 3, HP_BAR_Y + HP_BAR_H - 3,
        fill="#ff2222", outline="", tags="ui",
    )
    hp_text_id = canvas.create_text(
        HP_BAR_X + HP_BAR_W // 2, HP_BAR_Y + HP_BAR_H // 2,
        text=f"{max_hp} / {max_hp}",
        font=("Courier New", 16, "bold"), fill="white", tags="ui",
    )

    # ─── TIMER ───
    TIMER_X = 1920 - 60
    TIMER_Y = 30
    canvas.create_rectangle(
        TIMER_X - 170, TIMER_Y,
        TIMER_X, TIMER_Y + 80,
        fill="#1a1a1a", outline="#ff8800", width=3, tags="ui",
    )
    canvas.create_text(
        TIMER_X - 85, TIMER_Y + 16,
        text="ČAS", font=("Courier New", 13, "bold"), fill="#ff8800", tags="ui",
    )
    timer_id = canvas.create_text(
        TIMER_X - 85, TIMER_Y + 52,
        text=f"{time_left}s",
        font=("Courier New", 34, "bold"), fill="#ffcc00", tags="ui",
    )

    # ─── CLICK COUNTER ───  
    click_id = canvas.create_text(
        960, 30,
        text="KLIKY: 0 / 100",
        font=("Courier New", 22, "bold"),
        fill="#aaaaaa", anchor="n", tags="ui",
    )

    # ─── Prezident ───
    if pres_photo:
        pres_item = canvas.create_image(
            pres_x, pres_y, image=pres_photo, anchor="nw", tags="president"
        )
    else:
        pres_item = canvas.create_rectangle(
            pres_x, pres_y, pres_x + PRES_W, pres_y + PRES_H,
            fill="#003080", outline="#ffffff", width=3, tags="president",
        )
        canvas.create_text(
            pres_x + PRES_W // 2, pres_y + PRES_H // 2,
            text="PREZIDENT", font=("Courier New", 18, "bold"),
            fill="white", tags="president",
        )

    canvas.itemconfigure("president", state="hidden")

    # ─── Status text ───
    status_id = canvas.create_text(
        960, 540, text="",
        font=("Courier New", 64, "bold"),
        fill="#ffffff", justify="center", tags="status",
    )

    # ─── Blikání ───
    blink_job = [None]
    blink_state = [True]

    def blink_status():
        blink_state[0] = not blink_state[0]
        canvas.itemconfigure(status_id, fill="#ff2222" if blink_state[0] else "#ffcc00")
        blink_job[0] = root.after(500, blink_status)

    # ─── HP bar update ───
    def update_hp_bar():
        ratio = max(current_hp, 0) / max_hp
        fill_w = int((HP_BAR_W - 6) * ratio)
        if ratio > 0.5:
            color = "#22cc22"
        elif ratio > 0.25:
            color = "#ff8800"
        else:
            color = "#ff2222"
        canvas.coords(
            hp_fill,
            HP_BAR_X + 3, HP_BAR_Y + 3,
            HP_BAR_X + 3 + fill_w, HP_BAR_Y + HP_BAR_H - 3,
        )
        canvas.itemconfigure(hp_fill, fill=color)
        canvas.itemconfigure(hp_text_id, text=f"{max(current_hp, 0)} / {max_hp}")

    # ─── Pohyb prezidenta ───
    def move_president():
        nonlocal pres_x, pres_y, move_dx, move_dy, move_job
        if not game_active:
            return

        pres_x += move_dx
        pres_y += move_dy

        if pres_x <= 0 or pres_x + PRES_W >= 1920:
            move_dx = -move_dx
            pres_x = max(0, min(pres_x, 1920 - PRES_W))
        if pres_y <= 100 or pres_y + PRES_H >= 1080:
            move_dy = -move_dy
            pres_y = max(100, min(pres_y, 1080 - PRES_H))

        canvas.coords(pres_item, pres_x, pres_y)

        # Zrychlování jak ubývá HP
        speed = math.sqrt(move_dx ** 2 + move_dy ** 2)
        max_speed = 12 + (max_hp - current_hp) * 0.1
        if speed < max_speed:
            move_dx *= 1.002
            move_dy *= 1.002

        move_job = root.after(16, move_president)

    # ─── Klik na prezidenta ───
    def on_president_click(event):
        nonlocal current_hp, game_active, click_count
        if not game_active:
            return

        cx, cy = event.x, event.y
        if not (pres_x <= cx <= pres_x + PRES_W and pres_y <= cy <= pres_y + PRES_H):
            return

        current_hp -= 1
        click_count += 1
        update_hp_bar()
        canvas.itemconfigure(click_id, text=f"KLIKY: {click_count} / 100")

        # Flash
        canvas.itemconfigure(pres_item, state="hidden")
        root.after(30, lambda: canvas.itemconfigure(pres_item, state="normal"))

        if current_hp <= 0:
            win_game()

    canvas.bind("<Button-1>", on_president_click)

    # ─── VÝHRA ───
    def win_game():
        nonlocal game_active
        game_active = False
        canvas.itemconfigure("president", state="hidden")
        mixer.music.stop()
        if exp_photo:
            canvas.itemconfigure("bg", image=exp_photo)
        else:
            canvas.configure(bg="#ff4400")
        canvas.itemconfigure(status_id, text="EXPLOZE!\nVYHRÁL JSI!", fill="#ffcc00")
        blink_status()
        if os.path.exists(happy_phonk_path):
            mixer.music.load(happy_phonk_path)
            mixer.music.play(-1)

    # ─── PROHRA ───
    def lose_game():
        nonlocal game_active
        game_active = False
        canvas.itemconfigure("president", state="hidden")
        mixer.music.stop()
        if evil_photo:
            canvas.itemconfigure("bg", image=evil_photo)
        else:
            canvas.configure(bg="#3a0000")
        canvas.itemconfigure(
            status_id,
            text="PROHRÁL JSI!\nDÉMON TĚ DOSTAL!",
            fill="#ff2222",
        )
        blink_status()

    # ─── Timer ───
    def update_timer():
        nonlocal time_left, game_active
        if not game_active:
            return
        time_left -= 1
        canvas.itemconfigure(timer_id, text=f"{time_left}s")
        if time_left <= 10:
            canvas.itemconfigure(timer_id, fill="#ff2222")
        elif time_left <= 20:
            canvas.itemconfigure(timer_id, fill="#ff8800")
        if time_left > 0:
            root.after(1000, update_timer)
        else:
            if current_hp > 0:
                lose_game()

    # ─── Exploze animace před hrou ───
    def show_explosion_then_start():
        canvas.itemconfigure("start_screen", state="hidden")
        flash = canvas.create_rectangle(0, 0, 1920, 1080, fill="white", tags="flash")
        root.after(80,  lambda: canvas.itemconfigure(flash, fill="#ffcc00"))
        root.after(160, lambda: canvas.itemconfigure(flash, fill="#ff8800"))
        root.after(240, lambda: canvas.itemconfigure(flash, fill="#ff2222"))
        root.after(320, lambda: canvas.itemconfigure(flash, fill="#880000"))
        root.after(400, lambda: canvas.delete(flash))
        root.after(450, begin_game)

    # ─── Začátek hry ───
    def begin_game():
        nonlocal game_active
        game_active = True
        canvas.itemconfigure("president", state="normal")
        move_president()
        update_timer()
        if os.path.exists(sound_path):
            mixer.music.load(sound_path)
            mixer.music.play(-1)

    start_btn.config(command=show_explosion_then_start)

    # ─── Zavření ───
    def on_closing():
        if blink_job[0]:
            root.after_cancel(blink_job[0])
        mixer.music.stop()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()