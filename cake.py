# I LOVE YOU cake  🎂 #

import math
import random
import sys
import time

PHRASES = [
    "I love you", "Main tumse pyar karta hoon", "Te amo", "Je t'aime",
    "Ich liebe dich", "Ti amo", "Eu te amo", "Я тебя люблю", "愛してる",
    "我爱你", "사랑해", "أحبك", "میں تم سے محبت کرتا ہوں", "دوستت دارم",
    "אני אוהב אותך", "Seni seviyorum", "Σ'αγαπώ", "Ik hou van je",
    "Jag älskar dig", "Jeg elsker deg", "Jeg elsker dig", "Minä rakastan sinua",
    "Kocham cię", "Miluji tě", "Szeretlek", "Te iubesc", "Я тебе кохаю",
    "ฉันรักเธอ", "Anh yêu em", "Aku cinta kamu", "Saya cintakan awak",
    "Mahal kita", "আমি তোমাকে ভালোবাসি", "मैं तुमसे प्यार करता हूँ",
    "நான் உன்னை காதலிக்கிறேன்", "నేను నిన్ను ప్రేమిస్తున్నాను",
    "ਮੈਂ ਤੈਨੂੰ ਪਿਆਰ ਕਰਦਾ ਹਾਂ", "म तिमीलाई माया गर्छु", "Nakupenda",
    "Tá grá agam duit", "Dw i'n dy garu di", "Ég elska þig", "Volim te",
    "Обичам те", "Aloha au iā 'oe", "Ek is lief vir jou", "მიყვარხარ",
    "Ես սիրում եմ քեզ", "Би чамд хайртай", "Inħobbok", "Mi amas vin",
    "T'estimo", "Maite zaitut", "Aš tave myliu", "Es tevi mīlu",
    "Ma armastan sind", "Të dua", "Milujem ťa", "Ljubim te", "Seni sevaman",
    "Мен сені жақсы көремін", "እወድሃለሁ", "Mo nifẹ rẹ", "Ngiyakuthanda",
    "Waan ku jeclahay", "Ina son ka", "Aroha ahau ki a koe",
]

W, H = 780, 650
BG = (0, 0, 0)
FONT_SIZE = 10
ROW_H = 17
TIERS = [(5, 270), (6, 410), (7, 550)]          
CANDLES = 5
CANDLE_H = 85
CANDLE_GAP = 40
CORNER_R = 42                

T_BUILD_ROW_STEP = 0.28      
T_CANDLE_RISE = 5.2
T_LIGHT = 6.6
T_COUNT = 3                  
T_COUNT_START = 8.0          
T_BLOW = T_COUNT_START + T_COUNT  
T_BLOW_STEP = 0.06            
T_FADE_START = 14.5
T_FADE_DUR = 7.0
T_END = T_FADE_START + T_FADE_DUR + 1.5
LOOP = True

if sys.platform.startswith("win"):
    FONT = "Segoe UI"
elif sys.platform == "darwin":
    FONT = "Arial Unicode MS"
else:
    FONT = "Noto Sans"


def shape_rtl(s):
    """Urdu/Arabic/Hebrew ko sahi order me dikhane ki koshish (optional libs)."""
    if not any("֐" <= ch <= "ࣿ" for ch in s):
        return s
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
        return get_display(arabic_reshaper.reshape(s))
    except Exception:
        return s


def clamp01(x):
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def smooth(x):
    x = clamp01(x)
    return x * x * (3 - 2 * x)


def lerp(a, b, t):
    return a + (b - a) * t


def mix(rgb, a):
    """rgb ko black background ki taraf alpha a se blend karo -> '#rrggbb'."""
    a = clamp01(a)
    return "#%02x%02x%02x" % tuple(int(BG[i] + (rgb[i] - BG[i]) * a) for i in range(3))


def row_color(f):
    """f: 0 (top) .. 1 (bottom)  ->  pink -> purple -> blue"""
    stops = [(255, 120, 170), (200, 120, 255), (110, 160, 255)]
    if f < 0.5:
        u = f / 0.5
        a, b = stops[0], stops[1]
    else:
        u = (f - 0.5) / 0.5
        a, b = stops[1], stops[2]
    return tuple(int(lerp(a[i], b[i], u)) for i in range(3))


class CakeAnim:
    def __init__(self, canvas, measure):
        """canvas: tk.Canvas, measure(text) -> pixel width"""
        self.c = canvas
        self.measure = measure
        self.cx = W / 2
        self.cake_top = 250
        self.rng = random.Random(7)
        self.items = []          
        self._build_cake()
        self._build_candles()
        self.count_id = self.c.create_text(self.cx, 62, text="", fill=mix((255, 200, 220), 0),
                                           font=(FONT, 40, "bold"))

    # -- cake ---------------------------------------------------------------
    def _fit_row(self, pool, tw):
        """tw width me fit hone wale phrases chuno: gaps ~14px, ends bilkul barabar."""
        best, best_score = None, 1e9
        idx = list(range(len(pool)))
        for _ in range(120):
            self.rng.shuffle(idx)
            chosen, used = [], 0
            for j in idx:
                w = self.widths[j]
                if used + w + 10 * len(chosen) <= tw:
                    chosen.append(j)
                    used += w
                if len(chosen) >= 7:
                    break
            if len(chosen) < 2:
                continue
            score = abs(tw - (used + 14 * (len(chosen) - 1)))
            if score < best_score:
                best, best_score = chosen, score
        return best

    def _build_cake(self):
        rng, c = self.rng, self.c
        pool = [shape_rtl(p) for p in PHRASES]
        self.widths = [self.measure(p) for p in pool]
        total_rows = sum(r for r, _ in TIERS)
        row = 0
        y = self.cake_top
        for tier_i, (rows, width) in enumerate(TIERS):
            for k in range(rows):
    
                d_top = (k + 0.5) * ROW_H
                d_bot = (rows - k - 0.5) * ROW_H
                inset = 0.0
                for d in (d_top, d_bot):
                    if d < CORNER_R:
                        inset = max(inset, CORNER_R - math.sqrt(CORNER_R ** 2 - (CORNER_R - d) ** 2))
                tw = width - 2 * inset
                chosen = self._fit_row(pool, tw)
                used = sum(self.widths[j] for j in chosen)
                gap = (tw - used) / (len(chosen) - 1)
                x = self.cx - tw / 2                       
                col = row_color(row / (total_rows - 1))
                order = total_rows - 1 - row               
                for j in chosen:
                    w = self.widths[j]
                    tid = c.create_text(x + w / 2, y, text=pool[j], fill=mix(col, 0),
                                        font=(FONT, FONT_SIZE, "bold"))
                    delay = order * T_BUILD_ROW_STEP + rng.random() * 0.35
                    self.items.append((tid, col, delay))
                    x += w + gap
                y += ROW_H
                row += 1
        self.cake_bottom = y

    # -- candles -------------------------------------------------------------
    def _build_candles(self):
        c = self.c
        self.candles = []
        order = [2, 0, 4, 1, 3]                           
        base_y = self.cake_top - 14
        for i in range(CANDLES):
            x = self.cx + (i - (CANDLES - 1) / 2) * CANDLE_GAP
            body = c.create_line(x, base_y, x, base_y, width=5, fill=mix((170, 200, 255), 0))
            wick = c.create_line(x, base_y, x, base_y, width=1, fill=mix((90, 90, 90), 0))
            glow = c.create_oval(0, 0, 0, 0, fill=mix((255, 110, 20), 0), outline="", state="hidden")
            fl = c.create_oval(0, 0, 0, 0, fill=mix((255, 140, 30), 0), outline="", state="hidden")
            core = c.create_oval(0, 0, 0, 0, fill=mix((255, 240, 150), 0), outline="", state="hidden")
            smoke = [c.create_oval(0, 0, 0, 0, fill="#000", outline="", state="hidden") for _ in range(4)]
            self.candles.append(dict(
                x=x, base=base_y, body=body, wick=wick, glow=glow, fl=fl, core=core,
                smoke=smoke, rise=T_CANDLE_RISE + i * 0.12,
                light=T_LIGHT + i * 0.15,
                blow=T_BLOW + order.index(i) * T_BLOW_STEP,
            ))

    # -- countdown 3..2..1 -----------------------------------------------------
    def _draw_countdown(self, t):
        c = self.c
        k = int(t - T_COUNT_START)                       
        if 0 <= t - T_COUNT_START < T_COUNT:
            u = (t - T_COUNT_START) - k                  
            num = T_COUNT - k
            pop = smooth(u / 0.25)                      
            out = 1 - smooth((u - 0.7) / 0.3)           
            size = int(46 + 40 * (1 - pop) + 10 * u)
            c.itemconfig(self.count_id, text=str(num), font=(FONT, size, "bold"),
                         fill=mix((255, 205, 225), pop * out))
        else:
            c.itemconfig(self.count_id, text="")

    # -- frame ----------------------------------------------------------------
    def draw(self, t):
        c = self.c
        self._draw_countdown(t)
        fade = 1 - smooth((t - T_FADE_START) / T_FADE_DUR)   # 1 -> 0 (slow)

        for tid, col, delay in self.items:
            a = smooth((t - delay) / 0.9) * fade
            c.itemconfig(tid, fill=mix(col, a))

        for i, cd in enumerate(self.candles):
            x, base = cd["x"], cd["base"]
            h = CANDLE_H * smooth((t - cd["rise"]) / 0.9)
            top = base - h
            vis = clamp01(h / 6) * fade
            c.coords(cd["body"], x, base, x, top)
            c.itemconfig(cd["body"], fill=mix((170, 200, 255), vis))
            c.coords(cd["wick"], x, top, x, top - 5)
            c.itemconfig(cd["wick"], fill=mix((120, 120, 120), vis))
            
            s = smooth((t - cd["light"]) / 0.5)
            p = clamp01((t - cd["blow"]) / 0.55)             
            s *= (1 - p)
            if s > 0.02:
                flick = 1 + 0.14 * math.sin(t * 14 + i * 1.7) + 0.07 * math.sin(t * 23 + i)
                lean = p * 9 + 2 * math.sin(t * 9 + i)
                fx, fy = x + lean, top - 14
                fw, fh = 4.5 * s, 11 * s * flick
                c.itemconfig(cd["glow"], state="normal", fill=mix((255, 110, 20), 0.22 * s))
                c.coords(cd["glow"], fx - fw * 3, fy - fh * 1.2, fx + fw * 3, fy + fh * 1.2)
                c.itemconfig(cd["fl"], state="normal", fill=mix((255, 140, 30), s))
                c.coords(cd["fl"], fx - fw, fy - fh, fx + fw, fy + fh * 0.9)
                c.itemconfig(cd["core"], state="normal", fill=mix((255, 240, 150), s))
                c.coords(cd["core"], fx - fw * 0.5, fy - fh * 0.2, fx + fw * 0.5, fy + fh * 0.9)
            else:
                for k in ("glow", "fl", "core"):
                    c.itemconfig(cd[k], state="hidden")

            
            age = t - cd["blow"] - 0.25
            for k, sm in enumerate(cd["smoke"]):
                a = age - k * 0.18
                if 0 < a < 2.2:
                    r = 2 + a * 2.2
                    sx = x + 9 + 7 * math.sin(a * 4 + k * 1.3) + a * 4
                    sy = top - 14 - a * 30
                    al = 0.45 * (1 - a / 2.2)
                    c.itemconfig(sm, state="normal", fill=mix((170, 170, 190), al))
                    c.coords(sm, sx - r, sy - r, sx + r, sy + r)
                else:
                    c.itemconfig(sm, state="hidden")


def main():
    import tkinter as tk
    import tkinter.font as tkfont

    root = tk.Tk()
    root.title("I love you")
    root.configure(bg="black")
    root.resizable(False, False)
    canvas = tk.Canvas(root, width=W, height=H, bg="black", highlightthickness=0)
    canvas.pack()
    font = tkfont.Font(family=FONT, size=FONT_SIZE, weight="bold")
    anim = CakeAnim(canvas, font.measure)
    root.bind("<Escape>", lambda e: root.destroy())
    root.bind("<space>", lambda e: restart())

    state = {"t0": time.time()}

    def restart():
        state["t0"] = time.time()

    def tick():
        t = time.time() - state["t0"]
        anim.draw(t)
        if t > T_END and LOOP:
            restart()
        root.after(16, tick)

    tick()
    root.mainloop()


if __name__ == "__main__":
    main()
