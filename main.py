"""
CS2 PRO ASSISTANT v5.1
Geliştirici: Burak (r001B) Aydogdu

"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import json, os, re, threading, time, random, urllib.request, urllib.error
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
try:
    from PIL import Image, ImageTk
    PIL_OK = True
except Exception:
    Image = None
    ImageTk = None
    PIL_OK = False


# ═══════════════════════════════════════════════════════════════
#  RENK PALETİ
# ═══════════════════════════════════════════════════════════════
BG_BASE      = '#060608'
BG_PANEL     = '#0d0d10'
BG_CARD      = '#13131a'
BG_CARD2     = '#1a1a24'
BG_INPUT     = '#09090d'
GOLD         = '#c8960c'
GOLD_BRIGHT  = '#ffd700'
GOLD_DIM     = '#4a3800'
GOLD_GLOW    = '#ffdd4422'
TEXT_WHITE   = '#ede0c4'
TEXT_MUTED   = '#5a5a6a'
TEXT_DIM     = '#333344'
HIGHLIGHT    = '#1e1800'
RED_ALERT    = '#cc2200'
RED_DIM      = '#2a0800'
GREEN_OK     = '#00cc55'
GREEN_DIM    = '#003318'
BLUE_INFO    = '#3377ee'
BLUE_DIM     = '#0a1840'
ORANGE       = '#dd7700'
PURPLE       = '#9955dd'
CYAN         = '#00bbcc'
BORDER       = '#2a2a38'

GSI_PORT = 3000
GSI_CONFIG = f'''"CS2ProAssistant"
{{
    "uri" "http://127.0.0.1:{GSI_PORT}/"
    "timeout" "5.0"  "buffer" "0.1"  "throttle" "0.1"  "heartbeat" "10.0"
    "auth" {{ "token" "cs2pro" }}
    "data" {{
        "provider" "1" "map" "1" "round" "1"
        "player_id" "1" "player_state" "1" "player_weapons" "1"
        "player_match_stats" "1" "allplayers_id" "1"
        "allplayers_state" "1" "allplayers_match_stats" "1"
        "bomb" "1" "grenades" "1"
    }}
}}'''

# ═══════════════════════════════════════════════════════════════
#  GSI SERVER
# ═══════════════════════════════════════════════════════════════
class GSIHandler(BaseHTTPRequestHandler):
    callback = None

    def do_POST(self):
        try:
            body = self.rfile.read(int(self.headers.get('Content-Length', 0)))
            if GSIHandler.callback:
                GSIHandler.callback(json.loads(body.decode('utf-8')))
        except:
            pass
        self.send_response(200)
        self.end_headers()

    def log_message(self, *a):
        pass

def start_gsi(cb):
    GSIHandler.callback = cb
    srv = HTTPServer(('127.0.0.1', GSI_PORT), GSIHandler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv

# ═══════════════════════════════════════════════════════════════
#  VERİ TABANLARI (2026 GÜNCEL)
# ═══════════════════════════════════════════════════════════════
LINEUP_DB = {
    'de_dust2': [
        {'name': 'CT Smoke', 'type': 'Smoke', 'from_pos': 'T Spawn', 'x_pct': 0.30, 'y_pct': 0.22,
         'steps': ['T Spawn\'dan sol duvara yaslan', 'Gökyüzündeki baca ile hizala', 'Jump Throw (zıplayarak at)', 'CT koridoru kapanır ✓']},
        {'name': 'Xbox Smoke', 'type': 'Smoke', 'from_pos': 'Lower Tunnel', 'x_pct': 0.48, 'y_pct': 0.52,
         'steps': ['Lower Tunnel girişinde dur', 'Sağ köşeye yaslan', 'Düz at (No jump)', 'Xbox kutusunu kapatır ✓']},
        {'name': 'Long Flash', 'type': 'Flash', 'from_pos': 'Long Doors', 'x_pct': 0.20, 'y_pct': 0.30,
         'steps': ['Long Doors\'a gel', 'Köşeden pop-flash at', 'Rakibi kör eder', 'Hemen içeri gir ✓']},
        {'name': 'B Site Molotov', 'type': 'Molotov', 'from_pos': 'B Tunnels', 'x_pct': 0.72, 'y_pct': 0.68,
         'steps': ['B Tunnels\'dan gir', 'Kapıya yaklaş', 'B platform\'a at', 'Defans pozisyonlarını temizler ✓']},
        {'name': 'Mid Smoke', 'type': 'Smoke', 'from_pos': 'T Spawn', 'x_pct': 0.42, 'y_pct': 0.45,
         'steps': ['T Spawn\'dan çık', 'Mid kapıyı hedefle', 'Düz fırlat', 'Orta geçişi kapatır ✓']},
        {'name': 'A Site CT Cross', 'type': 'Smoke', 'from_pos': 'A Short', 'x_pct': 0.35, 'y_pct': 0.18,
         'steps': ['A Short\'tan gir', 'Site ortasına bak', 'CT cross smoke at', 'CT spawn görmez ✓']},
    ],
    'de_mirage': [
        {'name': 'CT Smoke', 'type': 'Smoke', 'from_pos': 'T Spawn', 'x_pct': 0.55, 'y_pct': 0.25,
         'steps': ['T Spawn\'dan çık', 'Mid\'e git', 'CT spawn smoke at', 'A site açılır ✓']},
        {'name': 'Jungle Smoke', 'type': 'Smoke', 'from_pos': 'Ramp', 'x_pct': 0.60, 'y_pct': 0.35,
         'steps': ['Ramp\'tan çık', 'Jungle\'a bak', 'Düz fırlat', 'Jungle görüşü keser ✓']},
        {'name': 'A Short Molotov', 'type': 'Molotov', 'from_pos': 'CT', 'x_pct': 0.62, 'y_pct': 0.45,
         'steps': ['CT spawn\'dan at', 'Short merdiveni hedefle', 'Düz fırlat', 'Short push\'ı durdurur ✓']},
        {'name': 'B App Flash', 'type': 'Flash', 'from_pos': 'B Site', 'x_pct': 0.25, 'y_pct': 0.55,
         'steps': ['B site\'tan bak', 'Short\'a at', 'Pop flash yap', 'Apartman girişini kör eder ✓']},
        {'name': 'Window Smoke', 'type': 'Smoke', 'from_pos': 'T Mid', 'x_pct': 0.50, 'y_pct': 0.40,
         'steps': ['T Mid\'den çık', 'Window\'a bak', 'Yüksek at', 'Mid window kapanır ✓']},
    ],
    'de_inferno': [
        {'name': 'Banana Smoke', 'type': 'Smoke', 'from_pos': 'T Spawn', 'x_pct': 0.32, 'y_pct': 0.55,
         'steps': ['T Spawn\'dan çık', 'Banana\'ya bak', 'Yüksek at', 'B site görüşü keser ✓']},
        {'name': 'B Car Molotov', 'type': 'Molotov', 'from_pos': 'Banana', 'x_pct': 0.38, 'y_pct': 0.62,
         'steps': ['Banana yarısına gel', 'Car\'a bak', 'Düşük at', 'Car arkasını temizler ✓']},
        {'name': 'Arch Smoke', 'type': 'Smoke', 'from_pos': 'T Ramp', 'x_pct': 0.50, 'y_pct': 0.30,
         'steps': ['T Ramp\'ta dur', 'Arch hedefle', 'Jump throw', 'CT görüşü keser ✓']},
        {'name': 'Quad Smoke', 'type': 'Smoke', 'from_pos': 'A Main', 'x_pct': 0.65, 'y_pct': 0.28,
         'steps': ['A Main\'den gir', 'Quad\'a bak', 'Yüksek at', 'Quad arkasını kapatır ✓']},
    ],
    'de_nuke': [
        {'name': 'Outside Smoke', 'type': 'Smoke', 'from_pos': 'T Spawn', 'x_pct': 0.45, 'y_pct': 0.20,
         'steps': ['T Spawn\'dan çık', 'Outside\'a bak', 'Yüksek fırlat', 'CT görüşü keser ✓']},
        {'name': 'Ramp Flash', 'type': 'Flash', 'from_pos': 'Outside', 'x_pct': 0.55, 'y_pct': 0.40,
         'steps': ['Outside\'dan gir', 'Ramp kapısına bak', 'Pop flash at', 'Ramp geçişi açar ✓']},
        {'name': 'Hut Smoke', 'type': 'Smoke', 'from_pos': 'T Spawn', 'x_pct': 0.38, 'y_pct': 0.35,
         'steps': ['T spawn yakınında dur', 'Hut girişini hedefle', 'Düz at', 'Hut kapanır ✓']},
    ],
    'de_ancient': [
        {'name': 'A Main Smoke', 'type': 'Smoke', 'from_pos': 'T Spawn', 'x_pct': 0.35, 'y_pct': 0.25,
         'steps': ['T Spawn\'dan çık', 'A Main\'e gir', 'CT tarafına at', 'A site açılır ✓']},
        {'name': 'Mid Smoke', 'type': 'Smoke', 'from_pos': 'T Spawn', 'x_pct': 0.50, 'y_pct': 0.48,
         'steps': ['Mid\'e çık', 'CT mid\'e bak', 'Düz fırlat', 'Mid kontrolü sağlar ✓']},
        {'name': 'B Main Flash', 'type': 'Flash', 'from_pos': 'B Main', 'x_pct': 0.28, 'y_pct': 0.62,
         'steps': ['B Main\'e gel', 'Pop flash at', 'Köşeyi kör et', 'B site açılır ✓']},
    ],
    'de_anubis': [
        {'name': 'A Site Main Smoke', 'type': 'Smoke', 'from_pos': 'A Main', 'x_pct': 0.72, 'y_pct': 0.25,
         'steps': ['A Main\'den gir', 'Site girişine bak', 'Düz fırlat', 'A site girişini kapatır ✓']},
        {'name': 'B Canal Smoke', 'type': 'Smoke', 'from_pos': 'T Spawn', 'x_pct': 0.30, 'y_pct': 0.60,
         'steps': ['T Spawn\'dan sol git', 'Canal\'a bak', 'Yüksek at', 'B girişini kapatır ✓']},
    ],
    'de_overpass': [
        {'name': 'B Short Smoke', 'type': 'Smoke', 'from_pos': 'T Spawn', 'x_pct': 0.28, 'y_pct': 0.45,
         'steps': ['T Spawn\'dan çık', 'Short\'a bak', 'Düz fırlat', 'B short kapatılır ✓']},
        {'name': 'A Long Flash', 'type': 'Flash', 'from_pos': 'Long', 'x_pct': 0.60, 'y_pct': 0.35,
         'steps': ['Long\'a git', 'Corner\'dan at', 'Pop flash', 'A site açılır ✓']},
        {'name': 'Fountain Smoke', 'type': 'Smoke', 'from_pos': 'T Spawn', 'x_pct': 0.45, 'y_pct': 0.55,
         'steps': ['T spawn yakın dur', 'Fountain\'a bak', 'Düz at', 'Fountain görüşü keser ✓']},
    ],
    'de_vertigo': [
        {'name': 'A Site Smoke', 'type': 'Smoke', 'from_pos': 'T Spawn', 'x_pct': 0.50, 'y_pct': 0.30,
         'steps': ['T Spawn\'dan çık', 'A site girişine bak', 'Yüksek at', 'A girişi kapatılır ✓']},
        {'name': 'B Short Smoke', 'type': 'Smoke', 'from_pos': 'Mid', 'x_pct': 0.35, 'y_pct': 0.55,
         'steps': ['Mid\'den git', 'B short\'a bak', 'Düz fırlat', 'B girişi kapatılır ✓']},
    ],
}

TYPE_CLR = {
    'Smoke':   '#8899aa',
    'Flash':   '#ffee22',
    'Molotov': '#ff6600',
    'HE':      '#ff3333'
}

PRO_CONFIGS = {
    's1mple': {
        'sensitivity': '3.09', 'zoom_sensitivity': '1.0', 'dpi': '400',
        'resolution': '1280x960', 'aspect': '4:3 Stretched',
        'crosshair': 'cl_crosshairsize 2; cl_crosshairthickness 0; cl_crosshairgap -2; cl_crosshairdot 0; cl_crosshaircolor 4',
        'launch': '-novid -tickrate 128 -high +fps_max 0',
        'notes': 'Düşük DPI + yüksek sens kombinasyonu. AWP için ideal.'
    },
    'NiKo': {
        'sensitivity': '1.22', 'zoom_sensitivity': '1.0', 'dpi': '400',
        'resolution': '1920x1080', 'aspect': '16:9 Native',
        'crosshair': 'cl_crosshairsize 3; cl_crosshairthickness 1; cl_crosshairgap -2; cl_crosshairdot 0; cl_crosshaircolor 1',
        'launch': '-novid -tickrate 128 +fps_max 400',
        'notes': 'Yüksek çözünürlük tercih eder. Rifle oyuncusu için dengeli sens.'
    },
    'ZywOo': {
        'sensitivity': '2.0', 'zoom_sensitivity': '1.0', 'dpi': '400',
        'resolution': '1280x960', 'aspect': '4:3 Stretched',
        'crosshair': 'cl_crosshairsize 1; cl_crosshairthickness 0; cl_crosshairgap -3; cl_crosshairdot 1; cl_crosshaircolor 5',
        'launch': '-novid -nojoy -high +fps_max 0 -tickrate 128',
        'notes': 'Küçük crosshair. Stretched resolution ile daha geniş karakter modelleri.'
    },
    'm0NESY': {
        'sensitivity': '1.49', 'zoom_sensitivity': '1.0', 'dpi': '800',
        'resolution': '1280x960', 'aspect': '4:3 Stretched',
        'crosshair': 'cl_crosshairsize 2; cl_crosshairthickness 0; cl_crosshairgap -3; cl_crosshairdot 0; cl_crosshaircolor 2',
        'launch': '-novid -tickrate 128 +fps_max 0 -nojoy',
        'notes': 'Yüksek DPI + düşük sens. Genç neslin favori ayarı.'
    },
    'donk': {
        'sensitivity': '1.0', 'zoom_sensitivity': '1.0', 'dpi': '800',
        'resolution': '1280x960', 'aspect': '4:3 Stretched',
        'crosshair': 'cl_crosshairsize 1; cl_crosshairthickness 0; cl_crosshairgap -2; cl_crosshairdot 0; cl_crosshaircolor 1',
        'launch': '-novid -tickrate 128 +fps_max 0',
        'notes': 'Dünyanın en düşük sensitivitelerinden biri. Çok geniş mousepad gerektirir.'
    },
    'ropz': {
        'sensitivity': '0.4', 'zoom_sensitivity': '1.0', 'dpi': '800',
        'resolution': '1920x1080', 'aspect': '16:9 Native',
        'crosshair': 'cl_crosshairsize 2; cl_crosshairthickness 0.5; cl_crosshairgap -2; cl_crosshairdot 0; cl_crosshaircolor 1',
        'launch': '-novid -tickrate 128 +fps_max 400',
        'notes': 'İnanılmaz düşük sens. Büyük mousepad şart.'
    },
    'frozen': {
        'sensitivity': '1.7', 'zoom_sensitivity': '1.0', 'dpi': '400',
        'resolution': '1280x960', 'aspect': '4:3 Stretched',
        'crosshair': 'cl_crosshairsize 2; cl_crosshairthickness 0; cl_crosshairgap -3; cl_crosshairdot 0; cl_crosshaircolor 1',
        'launch': '-novid -tickrate 128 +fps_max 0',
        'notes': 'Orta seviye sens, çok yönlü oyun.'
    },
}

STRATEGIES = {
    'de_dust2': {
        'T side': [
            {'name': 'A Split', 'desc': 'Long + Catwalk\'tan eş zamanlı A site baskısı.',
             'steps': ['2 oyuncu Catwalk\'tan girer', '2 oyuncu Long\'u geçer', '1 oyuncu Mid\'de CT smoke atar', 'Sinyal üzerine eş zamanlı giriş']},
            {'name': 'B Rush', 'desc': '5 kişi hızlı B push.',
             'steps': ['Tüm takım B Tunnel\'a girer', 'Flash önde patlasın', '3 platform, 2 kalan köşe kapat', 'Hızlı plant']},
            {'name': 'Fake B + A Hit', 'desc': 'B\'ye baskı yap, A\'ya atak.',
             'steps': ['2-3 oyuncu B\'ye rush', 'CT rotate alır', 'Kalan 2-3 A\'ya girer', 'Long veya Catwalk üzerinden']},
        ],
        'CT side': [
            {'name': 'Aggressive Long', 'desc': 'Long Doors\'ta erken bilgi al.',
             'steps': ['1 oyuncu Long\'a peek atar', 'Bilgi alır hemen çekilir', 'Rotate\'e hazır ol', 'AWP ideal rol']},
            {'name': 'Mid Control', 'desc': 'Mid\'i erken alıp B/A flex.',
             'steps': ['1 oyuncu Mid Window\'a çıkar', 'Xbox smoke atar', 'Mid\'den bilgi gönderir', 'Gerekirse rotate']},
        ]
    },
    'de_mirage': {
        'T side': [
            {'name': 'A Execute', 'desc': 'Ramp + Short + CT Smoke ile A site.',
             'steps': ['CT Smoke at', 'Jungle Smoke at', '2 Ramp, 2 Short, 1 Mid Window', 'Eş zamanlı entry', 'Plant CT kısımda']},
            {'name': 'B Apartments', 'desc': 'Apartments üzerinden B site.',
             'steps': ['4-5 oyuncu Apartments\'tan girer', 'Bench ve Short kapat', 'Hızlı plant', 'Retake engelle']},
        ],
        'CT side': [
            {'name': 'Mid Aggression', 'desc': 'Mid kontrolü ile bilgi al.',
             'steps': ['AWP Connector\'dan peek', 'Bilgi al, çekil', 'Mid window\'dan bomb taraf izle', 'Rotate hızlı']},
        ]
    },
}

CALLOUTS = {
    'de_dust2': ['Long A', 'Short A', 'A Site', 'B Site', 'Mid', 'Catwalk', 'Lower Tunnel',
                 'Upper Tunnel', 'CT Spawn', 'T Spawn', 'Xbox', 'Goose', 'Car', 'Platform'],
    'de_mirage': ['A Ramp', 'A Site', 'Jungle', 'CT', 'Short', 'Mid', 'B Apps', 'B Site',
                  'Van', 'Bench', 'Stairs', 'Window', 'Connector', 'Top Mid', 'Catwalk'],
    'de_inferno': ['A Site', 'Banana', 'B Site', 'CT', 'Apartments', 'T Ramp',
                   'Library', 'Dark', 'Car', 'Quad', 'Spools', 'Boiler'],
    'de_nuke':   ['A Site', 'B Site', 'Ramp', 'Outside', 'Lobby', 'Heaven', 'Hell',
                  'Silo', 'Vents', 'Secret', 'Squeaky', 'Rafters'],
    'de_ancient': ['A Site', 'A Main', 'Mid', 'B Site', 'B Main', 'Cave', 'C1', 'C2'],
    'de_anubis': ['A Site', 'A Main', 'B Site', 'B Canal', 'Mid', 'Palace', 'Water'],
    'de_overpass': ['A Site', 'B Site', 'Short', 'Long', 'Canal', 'Fountain', 'Toilets', 'Heaven'],
}

WEAPON_DATA = {
    'AK-47':       {'price': 2700, 'damage': 36, 'armor_pen': 77.5, 'rpm': 600, 'mag': 30, 'range': 'Uzun', 'type': 'Rifle',
                    'pros': ['Tek kafa öldürme (T taraf)', 'Yüksek hasar', 'Uzun menzil'],
                    'cons': ['İlk atış sapması', 'Yüksek geri tepme', 'Sadece T taraf'],
                    'tip': 'İlk mermiyi duraklayarak at. Spray için önce aşağı çek, sonra sola.'},
    'M4A4':        {'price': 3100, 'damage': 33, 'armor_pen': 70,   'rpm': 666, 'mag': 30, 'range': 'Uzun', 'type': 'Rifle',
                    'pros': ['30 mermi şarjör', 'İsabetli', 'CT standart'],
                    'cons': ['Kafa vuruşu tek öldürmez (zırhlıya)', 'Yüksek fiyat'],
                    'tip': 'Çoğu CT savaşı orta mesafede — kısa burst atışları tercih et.'},
    'M4A1-S':      {'price': 2900, 'damage': 33, 'armor_pen': 70,   'rpm': 600, 'mag': 20, 'range': 'Uzun', 'type': 'Rifle',
                    'pros': ['Susturucu — iz bırakmaz', 'Hassas', 'Ekonomik'],
                    'cons': ['Az mermi (20)', 'Yavaş RPM'],
                    'tip': 'Pozisyon gizlemek için idealdir. Mermiyi dikkatli kullan.'},
    'AWP':         {'price': 4750, 'damage': 115, 'armor_pen': 97.5, 'rpm': 41, 'mag': 5, 'range': 'Çok Uzun', 'type': 'Sniper',
                    'pros': ['Tek atım öldürme (gövde)', 'Uzun menzil dominansı'],
                    'cons': ['Pahalı', 'Yavaş', 'Hareket ederken isabetsiz'],
                    'tip': 'Sadece duruyorken ateş et. Peek sonrası hemen pozisyon değiştir.'},
    'Desert Eagle': {'price': 700, 'damage': 53, 'armor_pen': 93.0, 'rpm': 267, 'mag': 7, 'range': 'Orta', 'type': 'Pistol',
                     'pros': ['Ucuz', 'Kafa tek öldürür', 'Uzun menzil pistolet'],
                     'cons': ['Az mermi', 'Yavaş', 'Hareket cezası büyük'],
                     'tip': 'Her zaman durarak at. İki atım burst — sonra bekle.'},
    'MP9':         {'price': 1250, 'damage': 26, 'armor_pen': 60,   'rpm': 857, 'mag': 30, 'range': 'Kısa', 'type': 'SMG',
                    'pros': ['Hızlı', 'Ucuz', 'Eco roundda etkili'],
                    'cons': ['Kısa menzil', 'Zırha düşük hasar'],
                    'tip': 'Yakın mesafe baskısı için. Rush roundlarda ideal.'},
    'SG 553':      {'price': 3000, 'damage': 35, 'armor_pen': 100,  'rpm': 545, 'mag': 30, 'range': 'Uzun', 'type': 'Rifle',
                    'pros': ['Scope mevcut', 'Yüksek zırh penetrasyon'],
                    'cons': ['Yüksek geri tepme', 'Ağır'],
                    'tip': 'Scope kullanımı isabeti artırır ama hareket kısıtlar.'},
    'FAMAS':       {'price': 2050, 'damage': 30, 'armor_pen': 70,   'rpm': 666, 'mag': 25, 'range': 'Orta', 'type': 'Rifle',
                    'pros': ['Ucuz CT tüfeği', 'Burst modu var'],
                    'cons': ['Düşük hasar', 'Zırha yetersiz'],
                    'tip': 'Ekonomi roundlarında M4 yoksa iyi alternatif.'},
}

# ═══════════════════════════════════════════════════════════════
#  ANA UYGULAMA
# ═══════════════════════════════════════════════════════════════
class CS2Assistant:
    def __init__(self, root):
        self.root = root
        self.root.title("CS2 PRO ASSISTANT v7.0  |  Burak r001B Aydogdu  |  Hit+Eco+Rating CALISIR")
        self.root.geometry("1540x920")
        self.root.configure(bg=BG_BASE)
        self.root.resizable(True, True)
        self.root.minsize(1200, 700)

        self.data_dir = "data"
        self.maps_dir = "maps"
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.maps_dir, exist_ok=True)

        self.spots_file    = os.path.join(self.data_dir, "spots.json")
        self.configs_file  = os.path.join(self.data_dir, "configs.json")
        self.stats_file    = os.path.join(self.data_dir, "stats.json")
        self.settings_file = os.path.join(self.data_dir, "settings.json")
        self.matches_file  = os.path.join(self.data_dir, "matches.json")

        self.load_data()
        self.load_settings()

        # Auto-update worker controls
        self._update_thread = None
        self._update_stop   = threading.Event()

        # Harita
        self.current_map       = None
        self.current_map_image = None
        self.map_photo         = None
        self.spot_markers      = []
        self.spot_marking_enabled = False

        # Canlı durum
        self.live = {
            'map': '—', 'round': 0, 'ct_score': 0, 't_score': 0,
            'bomb': '—', 'hp': 100, 'armor': 100, 'money': 800,
            'kills': 0, 'deaths': 0, 'assists': 0, 'connected': False,
        }
        self._live_map_photo = None

        # GSI
        self.gsi_data    = {}
        self.gsi_server  = None
        self._last_map = None  # for match detection
        self._prev_kills = 0   # hit feedback icin

        # Overlay
        self.overlay_win       = None
        self.overlay_map_photo = None
        self._ov_filtered      = []
        self._ov_cw = self._ov_ch = 500
        self._ov_iw = self._ov_ih = 500
        self._ov_ox = self._ov_oy = 0
        self.ov_filter_var     = None

        # Bomb timer
        self._bomb_timer_id = None
        self._bomb_end_time = None

        # Ekonomi
        self.team_eco = {
            'ct': {'monies': [], 'losses': 0, 'total': 0, 'alive': 5},
            't':  {'monies': [], 'losses': 0, 'total': 0, 'alive': 5},
        }
        self._last_round_winner = None

        self.setup_styles()
        self.build_ui()
        self._init_connections()
        # Başlat: otomatik güncelleme işçisi
        try:
            self._start_auto_update_worker()
        except Exception:
            pass

        self.root.bind('<F9>',  lambda e: self.toggle_overlay())
        self.root.bind('<F10>', lambda e: self.close_overlay())

    # ─── INIT ───────────────────────────────────────────────────
    def _init_connections(self):
        try:
            self.gsi_server = start_gsi(self._on_gsi_data)
            self._set_status('🟢 GSI dinleniyor', GREEN_OK)
        except OSError as e:
            self._set_status('🔴 GSI başlatılamadı', RED_ALERT)

    # ─── EVENT HANDLERS ─────────────────────────────────────────
    def _on_gsi_data(self, data):
        self.gsi_data = data
        self.root.after(0, self._apply_gsi)

    def _apply_gsi(self):
        d  = self.gsi_data
        pl = d.get('player', {})
        st = pl.get('state', {})
        ms = pl.get('match_stats', {})
        mp = d.get('map', {})
        rd = d.get('round', {})

        # Map değişti mi? (yeni maç)
        new_map = mp.get('name')
        if new_map and new_map != self._last_map and self._last_map is not None:
            # Önceki maçın istatistiklerini kaydet
            self._save_current_match_stats()
        if new_map:
            self._last_map = new_map

        if hp := st.get('health'):  self.live['hp']     = hp
        if ar := st.get('armor'):   self.live['armor']  = ar
        if mo := st.get('money'):   self.live['money']  = mo
        _prev_k = self.live['kills']
        if ki := ms.get('kills'):   self.live['kills']  = ki
        if self.live['kills'] > _prev_k:
            self.root.after(0, self._trigger_hit_feedback)
        if de := ms.get('deaths'):  self.live['deaths'] = de
        if asst := ms.get('assists'): self.live['assists'] = asst
        if mn := mp.get('name'):    self.live['map']    = mn
        if ct := mp.get('team_ct', {}).get('score'): self.live['ct_score'] = ct
        if t  := mp.get('team_t',  {}).get('score'): self.live['t_score']  = t
        if rn := mp.get('round'):   self.live['round']  = rn

        # Bomb durumu
        if bm := rd.get('bomb'):
            old = self.live.get('bomb', '—')
            self.live['bomb'] = bm
            if bm == 'planted' and old != 'planted':
                self._start_bomb_timer()
            elif bm in ('defused', 'exploded') and old == 'planted':
                self._stop_bomb_timer()

        # Round phase takibi — bomb timer kesin durdur
        round_phase = rd.get('phase', '')
        if round_phase in ('over', 'freezetime', 'gameover') or rd.get('win_team'):
            self._stop_bomb_timer()
            self.live['bomb'] = '—'
            try:
                self.lv_bomb.config(text='—', fg=TEXT_MUTED)
                self.lv_bomb_timer.config(text='')
            except:
                pass

        self.live['connected'] = True

        # Aktif silah
        for wv in pl.get('weapons', {}).values():
            if wv.get('state') == 'active':
                self._update_weapon(
                    wv.get('name', '').replace('weapon_', '').upper(),
                    wv.get('ammo_clip', '—'), wv.get('ammo_reserve', '—'))
                break

        # Takım ekonomisi GSI
        allp = d.get('allplayers', {})
        if allp:
            ct_m, t_m = [], []
            for pid, pd in allp.items():
                team  = pd.get('team', '').upper()
                money = pd.get('state', {}).get('money', 0)
                if team == 'CT': ct_m.append(money)
                elif team == 'T': t_m.append(money)
            if ct_m:
                self.team_eco['ct']['monies'] = ct_m
                self.team_eco['ct']['total']  = sum(ct_m)
            if t_m:
                self.team_eco['t']['monies'] = t_m
                self.team_eco['t']['total']  = sum(t_m)

        self._set_status(f'🟢 CANLI (GSI)  {datetime.now().strftime("%H:%M:%S")}', GREEN_OK)
        self._refresh_live()
        self._refresh_team_eco()
        self._reload_live_map()  # harita değiştiyse güncelle
        # Canlı KDA panelini güncelle
        try:
            self._update_live_kda_panel()
        except Exception:
            pass
        # Harita adı nav label güncelle
        try:
            mn = self.live.get('map', '—')
            if mn and mn != '—' and hasattr(self, '_live_map_name_lbl'):
                self._live_map_name_lbl.config(text=mn.upper())
        except Exception:
            pass

    def _trigger_hit_feedback(self):
        """Kill oldugunda ses + gorsel - her platformda garantili calisir."""
        if not self.settings.get('sound_hit_feedback', True):
            return
        import sys, threading
        def _beep():
            try:
                if sys.platform == 'win32':
                    import winsound
                    winsound.Beep(880, 80)
                else:
                    print('\a', end='', flush=True)
            except Exception:
                try:
                    print('\a', end='', flush=True)
                except Exception:
                    pass
        threading.Thread(target=_beep, daemon=True).start()
        try:
            self.live_k_lbl.config(bg='#003a0a')
            self.root.after(250, self._reset_kill_flash)
        except Exception:
            pass
        self._set_status(
            f'  KILL +1  [{datetime.now().strftime("%H:%M:%S")}]', GREEN_OK)
        self.root.after(2000, lambda: self._set_status(
            f'CANLI GSI  {datetime.now().strftime("%H:%M:%S")}', GREEN_OK))

    def _reset_kill_flash(self):
        try:
            self.live_k_lbl.config(bg='#0f1f0f')
        except Exception:
            pass

    def _save_current_match_stats(self):
        """Mac sona erdiginde kaydet - GSI + Faceit uyumlu."""
        k = self.live['kills']
        d = self.live['deaths']
        a = self.live['assists']
        if not self._last_map or (k == 0 and d == 0):
            return
        if not self.settings.get('auto_save_matches', True):
            return
        kd     = round(k / max(d, 1), 2)
        rounds = max(self.live.get('round', 16), 1)
        kpr    = k / rounds
        apr    = a / rounds
        dpr    = d / rounds
        kast   = min(0.95, (k + a) / rounds * 0.7 + 0.3)
        adr    = max(50, min(150, k * 4.5 + a * 1.5))
        impact = 2.13 * kpr + 0.42 * apr - 0.41
        rating = 0.0073*(kast*100) + 0.3591*kpr - 0.5329*dpr + 0.2372*impact + 0.0032*adr + 0.1587
        rating = round(max(0.4, min(2.5, rating)), 2)
        if   rating >= 1.5: grade = 'S+'
        elif rating >= 1.2: grade = 'A'
        elif rating >= 1.0: grade = 'B'
        elif rating >= 0.7: grade = 'C'
        else:               grade = 'D'
        match = {
            'date':       datetime.now().strftime('%Y-%m-%d %H:%M'),
            'map':        self._last_map,
            'kills':      k, 'deaths': d, 'assists': a,
            'kd_ratio':   kd, 'rating': rating, 'grade': grade,
            'ct_score':   self.live['ct_score'], 't_score': self.live['t_score'],
            'round':      self.live.get('round', 0),
            'adr_approx': round(adr, 1),
        }
        self.matches_data.setdefault('matches', []).append(match)
        self._save_matches()
        try:
            self._load_match_history()
        except Exception:
            pass
    def _refresh_live(self):
        L = self.live
        try:
            self.lv_map.config(text=L['map'].upper() if L['map'] != '—' else '— OYUN BEKLENİYOR —')
            self.lv_score.config(text=f"CT  {L['ct_score']}  :  {L['t_score']}  T")
            self.lv_round.config(text=f"Round  {L['round']}")

            bs = L['bomb']
            bc = RED_ALERT if bs in ('planted', 'exploded') else (GREEN_OK if bs == 'defused' else TEXT_MUTED)
            bt = {'planted': '💣 PLANTED!', 'exploded': '💥 EXPLODED', 'defused': '✔ DEFUSED', '—': '—'}.get(bs, bs.upper())
            self.lv_bomb.config(text=bt, fg=bc)

            hp  = L['hp']
            hpc = GREEN_OK if hp > 60 else (ORANGE if hp > 25 else RED_ALERT)
            self.lv_hp.config(text=f'{hp}  HP', fg=hpc)
            self._bar(self.hp_bar, hp, 100, hpc)

            self.lv_armor.config(text=f"{L['armor']}  ARMOR")
            self._bar(self.armor_bar, L['armor'], 100, BLUE_INFO)

            m = L['money']
            self.lv_money.config(text=f'${m:,}')
            if m >= 4750:   eco, ec, ed = 'FULL BUY', GREEN_OK,  'Rifle+Armor+Util'
            elif m >= 2700: eco, ec, ed = 'FORCE',    ORANGE,    'Budget rifle+armor'
            else:           eco, ec, ed = 'ECO',      RED_ALERT, 'Para biriktir'
            self.lv_eco.config(text=eco, fg=ec)
            self.lv_eco_d.config(text=ed)

            self.lv_kda.config(text=f"K {L['kills']}   D {L['deaths']}   A {L['assists']}")

        except Exception as e:
            pass

    def _update_weapon(self, name, clip, reserve):
        try:
            self.lv_weapon.config(text=name)
            self.lv_ammo.config(text=f'{clip} / {reserve}')
        except:
            pass

    def _bar(self, canvas, val, mx, color):
        try:
            canvas.delete('all')
            w = canvas.winfo_width() or 260
            h = canvas.winfo_height() or 12
            r = max(0, min(1, val / mx))
            # Arkaplan
            canvas.create_rectangle(0, 0, w, h, fill='#111118', outline='')
            # Dolu kısım
            if r > 0:
                fw = int(w * r)
                canvas.create_rectangle(0, 0, fw, h, fill=color, outline='')
                # Parlaklık efekti (üst 30%)
                canvas.create_rectangle(0, 0, fw, int(h * 0.3), fill='#ffffff22', outline='')
            # Değer yazısı
            canvas.create_text(w // 2, h // 2, text=f'{val}/{mx}',
                                fill=TEXT_WHITE, font=('Consolas', 8, 'bold'))
        except:
            pass

    def _set_status(self, t, c=TEXT_WHITE):
        try:
            self.status_lbl.config(text=t, fg=c)
        except:
            pass

    # ─── STYLES ─────────────────────────────────────────────────
    def setup_styles(self):
        s = ttk.Style()
        s.theme_use('clam')
        s.configure('TFrame', background=BG_BASE)
        s.configure('TLabel', background=BG_BASE, foreground=TEXT_WHITE, font=('Segoe UI', 10))
        s.configure('Gold.TButton', background=GOLD_DIM, foreground=GOLD_BRIGHT,
                    borderwidth=0, relief='flat', focuscolor='none',
                    font=('Consolas', 10, 'bold'), padding=[14, 8])
        s.map('Gold.TButton',
              background=[('active', '#3a2800'), ('pressed', '#1a1200')],
              foreground=[('active', GOLD_BRIGHT)])
        s.configure('Danger.TButton', background='#2a0000', foreground='#ff4444',
                    borderwidth=0, relief='flat', focuscolor='none',
                    font=('Consolas', 10, 'bold'), padding=[14, 8])
        s.map('Danger.TButton', background=[('active', '#440000')])
        s.configure('TCombobox', fieldbackground=BG_INPUT, background=BG_PANEL,
                    foreground=TEXT_WHITE, selectbackground=HIGHLIGHT, font=('Consolas', 10))
        s.map('TCombobox', fieldbackground=[('readonly', BG_INPUT)], foreground=[('readonly', TEXT_WHITE)])
        s.configure('TSpinbox', fieldbackground=BG_INPUT, foreground=TEXT_WHITE,
                    insertcolor=GOLD, background=BG_PANEL, font=('Consolas', 10))
        s.configure('TCheckbutton', background=BG_CARD, foreground=TEXT_WHITE,
                    font=('Segoe UI', 10), focuscolor='none')
        s.map('TCheckbutton', indicatorcolor=[('selected', GOLD)])
        s.configure('TRadiobutton', background=BG_PANEL, foreground=TEXT_WHITE,
                    font=('Segoe UI', 10), focuscolor='none')
        s.map('TRadiobutton', indicatorcolor=[('selected', GOLD)], foreground=[('active', GOLD)])
        s.configure('TLabelframe', background=BG_CARD, bordercolor=GOLD_DIM, relief='flat', borderwidth=1)
        s.configure('TLabelframe.Label', background=BG_CARD, foreground=GOLD, font=('Consolas', 11, 'bold'))
        s.configure('TScale', background=BG_PANEL, troughcolor=BG_INPUT, sliderlength=18)
        s.configure('TNotebook', background=BG_BASE, borderwidth=0)
        s.configure('TNotebook.Tab', background='#111118', foreground=TEXT_MUTED,
                    padding=[14, 8], font=('Consolas', 9, 'bold'))
        s.map('TNotebook.Tab',
              background=[('selected', BG_CARD)],
              foreground=[('selected', GOLD_BRIGHT)])

    # ─── HELPERS ────────────────────────────────────────────────
    def _sec(self, p, t, bg=BG_PANEL):
        r = tk.Frame(p, bg=bg)
        r.pack(fill='x', pady=(8, 2))
        tk.Frame(r, bg=GOLD, width=3).pack(side='left', fill='y', padx=(0, 8))
        tk.Label(r, text=t.upper(), bg=bg, fg=GOLD,
                 font=('Consolas', 10, 'bold')).pack(side='left')

    def _div(self, p, bg=BG_PANEL):
        tk.Frame(p, bg=GOLD_DIM, height=1).pack(fill='x', pady=4)

    def _lb(self, p, h=10, w=22, fs=10):
        return tk.Listbox(p, bg=BG_INPUT, fg=TEXT_WHITE,
                          selectbackground='#2a1f00', selectforeground=GOLD_BRIGHT,
                          font=('Consolas', fs), activestyle='none',
                          highlightthickness=1, highlightcolor=GOLD_DIM,
                          highlightbackground=GOLD_DIM, relief='flat',
                          height=h, width=w, borderwidth=0)

    def _txt(self, p, h=8, ff='Consolas', fs=10, **kw):
        return tk.Text(p, bg=BG_INPUT, fg=TEXT_WHITE, insertbackground=GOLD,
                       selectbackground=HIGHLIGHT, selectforeground=GOLD_BRIGHT,
                       font=(ff, fs), relief='flat',
                       highlightthickness=1, highlightcolor=GOLD_DIM,
                       highlightbackground=GOLD_DIM, height=h, **kw)

    def _stxt(self, p, h=15, ff='Consolas', fs=10):
        return scrolledtext.ScrolledText(
            p, bg=BG_INPUT, fg=TEXT_WHITE, insertbackground=GOLD,
            selectbackground=HIGHLIGHT, selectforeground=GOLD_BRIGHT,
            font=(ff, fs), relief='flat',
            highlightthickness=1, highlightcolor=GOLD_DIM,
            highlightbackground=GOLD_DIM, height=h, wrap=tk.WORD)

    def _ent(self, p, w=20):
        return tk.Entry(p, bg=BG_INPUT, fg=TEXT_WHITE, insertbackground=GOLD,
                        selectbackground=HIGHLIGHT, selectforeground=GOLD_BRIGHT,
                        font=('Consolas', 10), relief='flat',
                        highlightthickness=1, highlightcolor=GOLD_DIM,
                        highlightbackground=GOLD_DIM, width=w)

    def _canvas_bar(self, p, h=12):
        c = tk.Canvas(p, bg='#111118', height=h, highlightthickness=0)
        c.pack(fill='x', padx=10, pady=2)
        return c

    def clip(self, t):
        self.root.clipboard_clear()
        self.root.clipboard_append(t)
        messagebox.showinfo('Kopyalandı', 'Panoya kopyalandı!')

    # ═══════════════════════════════════════════════════════════
    #  BUILD UI
    # ═══════════════════════════════════════════════════════════
    def build_ui(self):
        # Top accent
        tk.Frame(self.root, bg=GOLD, height=2).pack(fill='x')

        # Header
        hdr = tk.Frame(self.root, bg='#09090e', height=54)
        hdr.pack(fill='x')
        hdr.pack_propagate(False)

        logo_f = tk.Frame(hdr, bg='#09090e')
        logo_f.pack(side='left', padx=(14, 0), pady=6)
        tk.Label(logo_f, text='◈', bg='#09090e', fg=GOLD_BRIGHT,
                 font=('Consolas', 26, 'bold')).pack(side='left', padx=(0, 6))
        title_f = tk.Frame(logo_f, bg='#09090e')
        title_f.pack(side='left')
        tk.Label(title_f, text='CS2 PRO ASSISTANT', bg='#09090e', fg=GOLD_BRIGHT,
                 font=('Consolas', 19, 'bold')).pack(anchor='w')
        tk.Label(title_f, text='v5.1  PROFESSIONAL LIVE EDITION', bg='#09090e', fg=GOLD_DIM,
                 font=('Consolas', 8)).pack(anchor='w')

        right_hdr = tk.Frame(hdr, bg='#09090e')
        right_hdr.pack(side='right', padx=14)
        self.status_lbl = tk.Label(right_hdr, text='⚪  Başlatılıyor...', bg='#09090e',
                                    fg=TEXT_MUTED, font=('Consolas', 9))
        self.status_lbl.pack(anchor='e')
        tk.Label(right_hdr, text='by r001B Aydogdu  |  F9 = Overlay', bg='#09090e',
                 fg=GOLD_DIM, font=('Consolas', 8)).pack(anchor='e')

        # Menu bar
        self._build_menubar()
        tk.Frame(self.root, bg=GOLD_DIM, height=1).pack(fill='x')

        # Body
        body = tk.Frame(self.root, bg=BG_BASE)
        body.pack(fill='both', expand=True)

        self._build_live_panel(body)

        self.content_area = tk.Frame(body, bg=BG_BASE)
        self.content_area.pack(side='right', fill='both', expand=True)

        self._show_live_dashboard()

    def _build_menubar(self):
        mb = tk.Frame(self.root, bg='#0a0a0f', height=46)
        mb.pack(fill='x')
        mb.pack_propagate(False)

        menus = [
            ('🗺  HARİTA',  self._menu_map),
            ('💣  UTILITY', self._menu_utility),
            ('🎯  AİM',     self._menu_aim),
            ('🔫  SİLAH',   self._menu_weapon),
            ('📊  ANALİZ',  self._menu_analysis),
            ('🧠  TAKTİK',  self._menu_tactic),
            ('⚙  CONFIG',  self._menu_config),
            ('💹  EKONOMİ', self._menu_economy_team),
            ('🔧  AYARLAR', self._menu_settings),
            ('🌐  GÜNCELLE', self._check_for_updates),
        ]

        tk.Frame(mb, bg=GOLD_DIM, width=1).pack(side='left', fill='y')
        for label, cmd in menus:
            btn = tk.Button(mb, text=label, bg='#0a0a0f', fg=TEXT_MUTED,
                            font=('Consolas', 10, 'bold'), relief='flat',
                            activebackground=HIGHLIGHT, activeforeground=GOLD_BRIGHT,
                            padx=12, pady=0, cursor='hand2', command=cmd)
            btn.pack(side='left', fill='y')
            btn.bind('<Enter>', lambda e, b=btn: b.config(fg=GOLD_BRIGHT, bg='#18140a'))
            btn.bind('<Leave>', lambda e, b=btn: b.config(fg=TEXT_MUTED, bg='#0a0a0f'))
            tk.Frame(mb, bg=GOLD_DIM, width=1).pack(side='left', fill='y')

        # Overlay butonu
        ov_btn = tk.Button(mb, text='⚡ F9 OVERLAY', bg='#2a1f00', fg=GOLD_BRIGHT,
                           font=('Consolas', 9, 'bold'), relief='flat',
                           activebackground=GOLD_DIM, activeforeground=GOLD_BRIGHT,
                           padx=12, pady=0, cursor='hand2',
                           command=self.toggle_overlay)
        ov_btn.pack(side='right', fill='y', padx=6)

    # ─── LIVE LEFT PANEL ─────────────────────────────────────────
    def _build_live_panel(self, body):
        left = tk.Frame(body, bg=BG_PANEL, width=335)
        left.pack(side='left', fill='y')
        left.pack_propagate(False)

        # Üst gold çizgi
        tk.Frame(left, bg=GOLD, height=2).pack(fill='x')

        # Live göstergesi
        li = tk.Frame(left, bg='#0c0c10', height=26)
        li.pack(fill='x')
        li.pack_propagate(False)
        self._pulse_dot = tk.Label(li, text='●', bg='#0c0c10', fg=RED_ALERT,
                                    font=('Consolas', 9, 'bold'))
        self._pulse_dot.pack(side='left', padx=(8, 2))
        tk.Label(li, text='CANLI VERİ', bg='#0c0c10', fg=TEXT_MUTED,
                 font=('Consolas', 8, 'bold')).pack(side='left')
        self._start_pulse()

        # Harita & skor kartı
        self._build_map_card(left)

        # Oyuncu kartı
        self._build_player_card(left)

        # Ekonomi kartı
        self._build_eco_card(left)

    def _start_pulse(self):
        """Canlı göstergesi yanıp sönsün"""
        def _toggle():
            try:
                cur = self._pulse_dot.cget('fg')
                self._pulse_dot.config(fg=RED_ALERT if cur == '#0c0c10' else '#0c0c10')
                self.root.after(800, _toggle)
            except:
                pass
        self.root.after(800, _toggle)

    def _build_map_card(self, parent):
        mc = tk.Frame(parent, bg=BG_CARD)
        mc.pack(fill='x', padx=8, pady=(6, 3))
        tk.Frame(mc, bg=GOLD, height=2).pack(fill='x')

        tk.Label(mc, text='MAP', bg=BG_CARD, fg=GOLD,
                 font=('Consolas', 7, 'bold')).pack(anchor='w', padx=8, pady=(4, 0))
        self.lv_map = tk.Label(mc, text='— OYUN BEKLENİYOR —', bg=BG_CARD, fg=GOLD_BRIGHT,
                                font=('Consolas', 12, 'bold'))
        self.lv_map.pack(anchor='w', padx=8)

        self.lv_score = tk.Label(mc, text='CT  0  :  0  T', bg=BG_CARD, fg=GOLD_BRIGHT,
                                  font=('Consolas', 20, 'bold'))
        self.lv_score.pack(anchor='w', padx=8, pady=(2, 0))

        rr = tk.Frame(mc, bg=BG_CARD)
        rr.pack(fill='x', padx=6, pady=(2, 6))
        self.lv_round = tk.Label(rr, text='Round 0', bg=BG_CARD, fg=TEXT_MUTED,
                                  font=('Consolas', 9))
        self.lv_round.pack(side='left', padx=4)
        self.lv_bomb = tk.Label(rr, text='—', bg=BG_CARD, fg=TEXT_MUTED,
                                 font=('Consolas', 9, 'bold'))
        self.lv_bomb.pack(side='left', padx=8)

        # Bomb timer
        bt_r = tk.Frame(mc, bg=BG_CARD)
        bt_r.pack(fill='x', padx=6, pady=(0, 6))
        self.lv_bomb_timer = tk.Label(bt_r, text='', bg=BG_CARD, fg=RED_ALERT,
                                       font=('Consolas', 18, 'bold'))
        self.lv_bomb_timer.pack(side='left', padx=4)

    def _build_player_card(self, parent):
        pc = tk.Frame(parent, bg=BG_CARD)
        pc.pack(fill='x', padx=8, pady=3)
        tk.Frame(pc, bg=GOLD, height=2).pack(fill='x')

        tk.Label(pc, text='OYUNCU', bg=BG_CARD, fg=GOLD,
                 font=('Consolas', 7, 'bold')).pack(anchor='w', padx=8, pady=(4, 0))

        # HP
        hp_r = tk.Frame(pc, bg=BG_CARD)
        hp_r.pack(fill='x', padx=8, pady=(2, 0))
        tk.Label(hp_r, text='HP', bg=BG_CARD, fg=TEXT_MUTED,
                 font=('Consolas', 8)).pack(side='left')
        self.lv_hp = tk.Label(hp_r, text='100', bg=BG_CARD, fg=GREEN_OK,
                               font=('Consolas', 13, 'bold'))
        self.lv_hp.pack(side='right')
        self.hp_bar = self._canvas_bar(pc, h=12)

        # Armor
        ar_r = tk.Frame(pc, bg=BG_CARD)
        ar_r.pack(fill='x', padx=8, pady=(4, 0))
        tk.Label(ar_r, text='ARMOR', bg=BG_CARD, fg=TEXT_MUTED,
                 font=('Consolas', 8)).pack(side='left')
        self.lv_armor = tk.Label(ar_r, text='100', bg=BG_CARD, fg=BLUE_INFO,
                                  font=('Consolas', 11, 'bold'))
        self.lv_armor.pack(side='right')
        self.armor_bar = self._canvas_bar(pc, h=8)

        # Para
        money_r = tk.Frame(pc, bg=BG_CARD)
        money_r.pack(fill='x', padx=8, pady=(6, 0))
        tk.Label(money_r, text='PARA', bg=BG_CARD, fg=TEXT_MUTED,
                 font=('Consolas', 7, 'bold')).pack(side='left')
        self.lv_money = tk.Label(money_r, text='$800', bg=BG_CARD, fg=GOLD_BRIGHT,
                                  font=('Consolas', 16, 'bold'))
        self.lv_money.pack(side='right')

        eco_r = tk.Frame(pc, bg=BG_CARD)
        eco_r.pack(fill='x', padx=8, pady=(0, 2))
        self.lv_eco   = tk.Label(eco_r, text='', bg=BG_CARD, fg=TEXT_MUTED,
                                  font=('Consolas', 9, 'bold'))
        self.lv_eco.pack(side='left')
        self.lv_eco_d = tk.Label(eco_r, text='', bg=BG_CARD, fg=TEXT_MUTED,
                                  font=('Segoe UI', 8))
        self.lv_eco_d.pack(side='right')

        # KDA
        self.lv_kda = tk.Label(pc, text='K 0   D 0   A 0', bg=BG_CARD, fg=TEXT_WHITE,
                                font=('Consolas', 10))
        self.lv_kda.pack(anchor='w', padx=10, pady=2)

        # Silah
        tk.Frame(pc, bg=GOLD_DIM, height=1).pack(fill='x', padx=6, pady=4)
        self.lv_weapon = tk.Label(pc, text='—', bg=BG_CARD, fg=GOLD_BRIGHT,
                                   font=('Consolas', 13, 'bold'))
        self.lv_weapon.pack(anchor='w', padx=10, pady=(2, 0))
        self.lv_ammo   = tk.Label(pc, text='— / —', bg=BG_CARD, fg=TEXT_MUTED,
                                   font=('Consolas', 9))
        self.lv_ammo.pack(anchor='w', padx=10, pady=(0, 6))

    def _build_eco_card(self, parent):
        ef = tk.Frame(parent, bg='#080608')
        ef.pack(fill='x', padx=8, pady=3)
        tk.Frame(ef, bg=GOLD, height=2).pack(fill='x')

        ehdr = tk.Frame(ef, bg='#0d0b00', height=22)
        ehdr.pack(fill='x')
        ehdr.pack_propagate(False)
        tk.Label(ehdr, text='  💹  TAKİM EKONOMİSİ', bg='#0d0b00', fg=GOLD,
                 font=('Consolas', 8, 'bold')).pack(side='left', padx=4)
        self.eco_gsi_lbl = tk.Label(ehdr, text='GSI bekleniyor', bg='#0d0b00', fg=TEXT_MUTED,
                                     font=('Segoe UI', 7))
        self.eco_gsi_lbl.pack(side='right', padx=6)

        # CT
        ct_r = tk.Frame(ef, bg='#080608')
        ct_r.pack(fill='x', padx=8, pady=(6, 1))
        tk.Label(ct_r, text='CT', bg='#080608', fg=BLUE_INFO,
                 font=('Consolas', 9, 'bold'), width=3).pack(side='left')
        self.eco_ct_total    = tk.Label(ct_r, text='$—', bg='#080608', fg=GOLD_BRIGHT,
                                         font=('Consolas', 11, 'bold'))
        self.eco_ct_total.pack(side='left', padx=6)
        self.eco_ct_decision = tk.Label(ct_r, text='—', bg='#080608', fg=TEXT_MUTED,
                                         font=('Consolas', 9, 'bold'))
        self.eco_ct_decision.pack(side='left')
        self.eco_ct_bar      = self._canvas_bar(ef, h=6)

        # T
        t_r = tk.Frame(ef, bg='#080608')
        t_r.pack(fill='x', padx=8, pady=(4, 1))
        tk.Label(t_r, text='T', bg='#080608', fg=RED_ALERT,
                 font=('Consolas', 9, 'bold'), width=3).pack(side='left')
        self.eco_t_total     = tk.Label(t_r, text='$—', bg='#080608', fg=GOLD_BRIGHT,
                                         font=('Consolas', 11, 'bold'))
        self.eco_t_total.pack(side='left', padx=6)
        self.eco_t_decision  = tk.Label(t_r, text='—', bg='#080608', fg=TEXT_MUTED,
                                         font=('Consolas', 9, 'bold'))
        self.eco_t_decision.pack(side='left')
        self.eco_t_bar       = self._canvas_bar(ef, h=6)

        tk.Frame(ef, bg=GOLD_DIM, height=1).pack(fill='x', padx=4, pady=3)

        self.eco_advice_ct = tk.Label(ef, text='', bg='#080608', fg=BLUE_INFO,
                                       font=('Consolas', 8), wraplength=290, justify='left')
        self.eco_advice_ct.pack(anchor='w', padx=8, pady=(0, 2))
        self.eco_advice_t  = tk.Label(ef, text='', bg='#080608', fg='#ff6644',
                                       font=('Consolas', 8), wraplength=290, justify='left')
        self.eco_advice_t.pack(anchor='w', padx=8, pady=(0, 6))

    # ─── CANLI PANEL IÇERIK ─────────────────────────────────────
    def _show_live_dashboard(self):
        for w in self.content_area.winfo_children():
            w.destroy()
        outer = tk.Frame(self.content_area, bg=BG_BASE)
        outer.pack(fill='both', expand=True)
        tk.Frame(outer, bg=GOLD, height=2).pack(fill='x')

        # Nav çubuğu
        nav = tk.Frame(outer, bg='#0c0c10', height=28)
        nav.pack(fill='x')
        nav.pack_propagate(False)
        tk.Frame(nav, bg=GREEN_OK, width=3).pack(side='left', fill='y')
        tk.Label(nav, text='  CANLI HARİTA & ANALİZ', bg='#0c0c10', fg=GREEN_OK,
                 font=('Consolas', 9, 'bold')).pack(side='left', padx=6)
        self._live_map_name_lbl = tk.Label(nav, text='', bg='#0c0c10', fg=GOLD,
                 font=('Consolas', 9, 'bold'))
        self._live_map_name_lbl.pack(side='left', padx=16)

        body = tk.Frame(outer, bg=BG_BASE)
        body.pack(fill='both', expand=True)

        # Sol: harita canvas
        map_frame = tk.Frame(body, bg=BG_BASE)
        map_frame.pack(side='left', fill='both', expand=True)
        self.live_map_canvas = tk.Canvas(map_frame, bg='#0a0a0e', highlightthickness=0)
        self.live_map_canvas.pack(fill='both', expand=True, padx=2, pady=2)

        # Sağ: KDA + Anlık öneri paneli (kill feed YOK)
        right_panel = tk.Frame(body, bg=BG_PANEL, width=280)
        right_panel.pack(side='right', fill='y')
        right_panel.pack_propagate(False)
        tk.Frame(right_panel, bg=GOLD, height=2).pack(fill='x')

        # KDA Canlı
        kda_card = tk.Frame(right_panel, bg=BG_CARD)
        kda_card.pack(fill='x', padx=6, pady=(6, 3))
        tk.Frame(kda_card, bg=GOLD, height=2).pack(fill='x')
        tk.Label(kda_card, text='CANLI KDA', bg=BG_CARD, fg=GOLD,
                 font=('Consolas', 8, 'bold')).pack(anchor='w', padx=8, pady=(4, 0))
        kda_row = tk.Frame(kda_card, bg=BG_CARD)
        kda_row.pack(fill='x', padx=8, pady=4)
        # K
        k_f = tk.Frame(kda_row, bg='#0f1f0f'); k_f.pack(side='left', expand=True, fill='x', padx=2)
        tk.Label(k_f, text='K', bg='#0f1f0f', fg=GREEN_OK, font=('Consolas', 8)).pack()
        self.live_k_lbl = tk.Label(k_f, text='0', bg='#0f1f0f', fg=GREEN_OK, font=('Consolas', 22, 'bold'))
        self.live_k_lbl.pack()
        # D
        d_f = tk.Frame(kda_row, bg='#1f0f0f'); d_f.pack(side='left', expand=True, fill='x', padx=2)
        tk.Label(d_f, text='D', bg='#1f0f0f', fg=RED_ALERT, font=('Consolas', 8)).pack()
        self.live_d_lbl = tk.Label(d_f, text='0', bg='#1f0f0f', fg=RED_ALERT, font=('Consolas', 22, 'bold'))
        self.live_d_lbl.pack()
        # A
        a_f = tk.Frame(kda_row, bg='#0f0f1f'); a_f.pack(side='left', expand=True, fill='x', padx=2)
        tk.Label(a_f, text='A', bg='#0f0f1f', fg=BLUE_INFO, font=('Consolas', 8)).pack()
        self.live_a_lbl = tk.Label(a_f, text='0', bg='#0f0f1f', fg=BLUE_INFO, font=('Consolas', 22, 'bold'))
        self.live_a_lbl.pack()
        # KD ratio
        self.live_kd_ratio_lbl = tk.Label(kda_card, text='K/D: —', bg=BG_CARD, fg=GOLD,
                font=('Consolas', 10, 'bold'))
        self.live_kd_ratio_lbl.pack(pady=(0, 6))

        # Anlık Öneri
        tk.Frame(right_panel, bg=GOLD_DIM, height=1).pack(fill='x', padx=4, pady=4)
        tk.Label(right_panel, text='⚡ ANLИК ÖNERİ', bg=BG_PANEL, fg=GOLD,
                 font=('Consolas', 9, 'bold')).pack(anchor='w', padx=8, pady=(4, 2))
        self.live_advice_txt = tk.Text(right_panel, bg='#09090d', fg=TEXT_WHITE,
                font=('Segoe UI', 9), relief='flat', height=12, wrap=tk.WORD,
                highlightthickness=0, state='disabled')
        self.live_advice_txt.pack(fill='x', padx=6, pady=(0, 4))

        # Performans durumu
        tk.Frame(right_panel, bg=GOLD_DIM, height=1).pack(fill='x', padx=4, pady=4)
        tk.Label(right_panel, text='📊 PERFORMANS', bg=BG_PANEL, fg=GOLD,
                 font=('Consolas', 9, 'bold')).pack(anchor='w', padx=8, pady=(4, 2))
        self.live_perf_lbl = tk.Label(right_panel, text='Oyun bekleniyor...', bg=BG_PANEL,
                fg=TEXT_MUTED, font=('Consolas', 9), wraplength=260, justify='left')
        self.live_perf_lbl.pack(anchor='w', padx=10, pady=(0, 8))

        self._reload_live_map()
        self._update_live_kda_panel()

    def _update_live_kda_panel(self):
        """Canlı KDA panelini ve anlık önerileri güncelle."""
        try:
            k = self.live['kills']
            d = self.live['deaths']
            a = self.live['assists']
            kd = k / max(d, 1)

            self.live_k_lbl.config(text=str(k))
            self.live_d_lbl.config(text=str(d))
            self.live_a_lbl.config(text=str(a))
            self.live_kd_ratio_lbl.config(text=f'K/D: {kd:.2f}')

            # Anlık öneri oluştur
            advice = self._generate_live_advice(k, d, a, kd)
            self.live_advice_txt.config(state='normal')
            self.live_advice_txt.delete('1.0', tk.END)
            self.live_advice_txt.insert('1.0', advice)
            self.live_advice_txt.config(state='disabled')

            # Performans etiketi
            if d == 0 and k >= 5:
                perf_text = '🔥 Muhteşem açılış!'
                perf_clr = GREEN_OK
            elif kd >= 2.0:
                perf_text = '✅ Çok iyi performans'
                perf_clr = GREEN_OK
            elif kd >= 1.0:
                perf_text = '⚖ Dengeli — devam et'
                perf_clr = GOLD
            elif kd >= 0.5:
                perf_text = '⚠ Dikkatli ol, pozisyon değiştir'
                perf_clr = ORANGE
            else:
                perf_text = '❌ Eco al, takıma drop yap'
                perf_clr = RED_ALERT
            self.live_perf_lbl.config(text=perf_text, fg=perf_clr)
        except Exception:
            pass

    def _generate_live_advice(self, k, d, a, kd):
        """KDA + ekonomi verilerine göre anlık öneri üret."""
        money  = self.live.get('money', 800)
        map_nm = self.live.get('map', '—')
        bomb   = self.live.get('bomb', '—')
        advice_lines = []

        # Bomb durumuna göre
        if bomb == 'planted':
            advice_lines.append('💣 BOMBA EKİLDİ!\n→ Defuse → Smoke + Flash ile koru\n→ Awp varsa Kross yap\n')
        
        # KDA bazlı
        if kd >= 2.0:
            advice_lines.append('🔥 AGRESIF OYNAYABİLİRSİN\n→ Entry fragger rol al\n→ Flash ile öne çık\n')
        elif kd < 0.7 and d >= 3:
            advice_lines.append('⚠ GERİ ÇEKİL\n→ Daha güvenli pozisyon al\n→ Info satmayı bırak\n→ Utility kullan\n')
        
        # Ekonomi bazlı
        if money < 1800:
            advice_lines.append('💰 ECO ROUND\n→ Pistol/SMG al\n→ Force etme, biriktir\n→ Riske girme\n')
        elif money >= 4750:
            advice_lines.append('💰 FULL BUY\n→ Rifle + Armor + Utility al\n→ Nades kullan\n')
        
        # Assist bazlı
        if a >= 3 and k < 3:
            advice_lines.append('🤝 DESTEK ROLÜ\n→ Flash atmaya devam et\n→ Takıma utility sağla\n')
        
        # Harita bazlı öneri
        map_tips = {
            'de_dust2':   '🗺 Dust2: Long kontrolü kritik\n→ Mid smoke + Xbox smoke at\n',
            'de_mirage':  '🗺 Mirage: CT smoke + Jungle smoke\n→ Mid window bilgisi önemli\n',
            'de_inferno': '🗺 Inferno: Banana kontrolü\n→ Car molotov at, B açıl\n',
            'de_nuke':    '🗺 Nuke: Outside erken al\n→ Ramp flash + Hut smoke\n',
            'de_ancient': '🗺 Ancient: Mid kontrolü\n→ A main smoke + C1 flash\n',
        }
        if map_nm in map_tips:
            advice_lines.append(map_tips[map_nm])

        if not advice_lines:
            advice_lines.append('⚡ Oyun devam ediyor...\n→ Callout yap\n→ Mini-haritayı izle\n→ Pozisyon değiştir\n')

        return '\n'.join(advice_lines)

    def _reload_live_map(self):
        if not PIL_OK:
            return
        mn = self.live.get('map', '—')
        if mn == '—':
            return
        candidates = [mn, mn.replace('de_', ''), f'de_{mn}']
        for c in candidates:
            p = os.path.join(self.maps_dir, f'{c}.gif')
            if not os.path.exists(p):
                p = os.path.join(self.maps_dir, f'{c}.png')
            if os.path.exists(p):
                try:
                    canvas = getattr(self, 'live_map_canvas', None)
                    if canvas is None:
                        return
                    canvas.update_idletasks()
                    cw = canvas.winfo_width()  or 900
                    ch = canvas.winfo_height() or 650
                    img   = Image.open(p)
                    ratio = img.width / img.height
                    if ratio > cw / ch:
                        nw, nh = cw, int(cw / ratio)
                    else:
                        nw, nh = int(ch * ratio), ch
                    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
                    self._live_map_photo = ImageTk.PhotoImage(img)
                    canvas.delete('all')
                    canvas.create_image(cw // 2, ch // 2,
                                        image=self._live_map_photo, anchor='center')
                    canvas.create_text(16, 16, text=mn.upper(), anchor='nw',
                                       fill=GOLD_BRIGHT, font=('Consolas', 13, 'bold'))
                except Exception as e:
                    print(f"Harita yükleme hatası: {e}")
                break

    # ─── BOMB TIMER ──────────────────────────────────────────────
    BOMB_TIME = 40

    def _start_bomb_timer(self):
        if self._bomb_timer_id:
            self.root.after_cancel(self._bomb_timer_id)
        self._bomb_end_time = time.time() + self.BOMB_TIME
        self._tick_bomb()

    def _stop_bomb_timer(self):
        if self._bomb_timer_id:
            self.root.after_cancel(self._bomb_timer_id)
            self._bomb_timer_id = None
        try:
            bs = self.live.get('bomb', '—')
            if bs == 'defused':
                self.lv_bomb_timer.config(text='✔ ÇÖZÜLDÜ', fg=GREEN_OK)
            elif bs == 'exploded':
                self.lv_bomb_timer.config(text='💥 PATLADI!', fg=RED_ALERT)
            else:
                self.lv_bomb_timer.config(text='')
        except:
            pass

    def _tick_bomb(self):
        try:
            rem = self._bomb_end_time - time.time()
            if rem <= 0:
                self.lv_bomb_timer.config(text='💥  00.0s', fg=RED_ALERT)
                return
            clr = RED_ALERT if rem < 10 else (ORANGE if rem < 20 else GOLD_BRIGHT)
            self.lv_bomb_timer.config(text=f'💣  {rem:05.2f}s', fg=clr)
            self._bomb_timer_id = self.root.after(50, self._tick_bomb)
        except:
            pass

    # ─── EKONOMİ ─────────────────────────────────────────────────
    LOSS_BONUS   = [1400, 1900, 2400, 2900, 3400]
    FULL_BUY_T   = 4750
    FULL_BUY_CT  = 5200
    FORCE_BUY_T  = 2700
    FORCE_BUY_CT = 2900
    ECO_LIMIT    = 1800

    def _team_buy_decision(self, monies, side, losses):
        if not monies:
            return 'BEKLENIYOR', TEXT_MUTED, []
        total     = sum(monies)
        n         = len(monies)
        full_thr  = self.FULL_BUY_CT if side == 'ct' else self.FULL_BUY_T
        force_thr = self.FORCE_BUY_CT if side == 'ct' else self.FORCE_BUY_T
        can_full  = sum(1 for m in monies if m >= full_thr)
        must_eco  = sum(1 for m in monies if m < self.ECO_LIMIT)

        if can_full >= 4:
            return 'FULL BUY', GREEN_OK, [f'{can_full}/{n} tam buy']
        elif can_full >= 2 and must_eco <= 1:
            return 'YARI BUY', ORANGE, ['Drop sistemi kullan']
        elif must_eco >= 3 or total < n * self.ECO_LIMIT:
            return 'ECO', RED_ALERT, ['Para biriktir']
        else:
            return 'FORCE', '#ff8800', ['SMG + Armor']

    def _refresh_team_eco(self):
        try:
            ct = self.team_eco['ct']
            t  = self.team_eco['t']

            if not ct['monies'] and not t['monies']:
                return

            self.eco_gsi_lbl.config(text='● CANLI', fg=GREEN_OK)

            cl = ct.get('losses', 0)
            tl = t.get('losses', 0)
            ct_dec, ct_clr, _ = self._team_buy_decision(ct['monies'], 'ct', cl)
            self.eco_ct_total.config(text=f"${ct.get('total',0):,}")
            self.eco_ct_decision.config(text=ct_dec, fg=ct_clr)
            self._bar(self.eco_ct_bar, min(ct.get('total',0), 5 * self.FULL_BUY_CT),
                      5 * self.FULL_BUY_CT, ct_clr)

            t_dec, t_clr, _ = self._team_buy_decision(t['monies'], 't', tl)
            self.eco_t_total.config(text=f"${t.get('total',0):,}")
            self.eco_t_decision.config(text=t_dec, fg=t_clr)
            self._bar(self.eco_t_bar, min(t.get('total',0), 5 * self.FULL_BUY_T),
                      5 * self.FULL_BUY_T, t_clr)

            # KDA tabanlı tavsiye ekle
            kd_ratio = (self.live['kills'] + 1) / (self.live['deaths'] + 1)  # sıfır bölme engeli
            if kd_ratio > 2.0:
                perf_advice = "🔥 Harika gidiyorsun! Full buy yap ve agresif oyna."
            elif kd_ratio > 1.0:
                perf_advice = "⚖ Dengeli performans. Takımına destek ol."
            else:
                perf_advice = "⚠ Zorlanıyorsan eco kal, takımına drop yap."

            self.eco_advice_ct.config(
                text=f'CT: {ct_dec}  ({cl} kayip) | {perf_advice}', fg=BLUE_INFO)
            self.eco_advice_t.config(
                text=f'T: {t_dec}  ({tl} kayip) | {perf_advice}', fg='#ff6644')
        except:
            pass

    # ═══════════════════════════════════════════════════════════
    #  POPUP HELPER
    # ═══════════════════════════════════════════════════════════
    def _popup(self, title, w=1000, h=700):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.configure(bg=BG_BASE)
        win.geometry(f'{w}x{h}+{self.root.winfo_x()+40}+{self.root.winfo_y()+30}')
        win.grab_set()
        tk.Frame(win, bg=GOLD, height=2).pack(fill='x')
        hdr = tk.Frame(win, bg='#0c0c10', height=44)
        hdr.pack(fill='x')
        hdr.pack_propagate(False)
        tk.Frame(hdr, bg=GOLD, width=4).pack(side='left', fill='y')
        tk.Label(hdr, text=f'  {title}', bg='#0c0c10', fg=GOLD_BRIGHT,
                 font=('Consolas', 14, 'bold')).pack(side='left', padx=8)
        tk.Button(hdr, text=' ✕ ', bg='#0c0c10', fg=TEXT_MUTED,
                  font=('Consolas', 12), relief='flat',
                  activebackground=RED_DIM, activeforeground=RED_ALERT,
                  command=win.destroy).pack(side='right', padx=8)
        tk.Frame(win, bg=GOLD_DIM, height=1).pack(fill='x')
        return win

    # ═══════════════════════════════════════════════════════════
    #  MENÜ ACTIONLARI (kısaltıldı, sadece ANALİZ tabı değiştirildi)
    # ═══════════════════════════════════════════════════════════
    def _menu_analysis(self):
        win  = self._popup('📊  Maç Analizi & Performans', 1050, 720)
        body = tk.Frame(win, bg=BG_BASE)
        body.pack(fill='both', expand=True)
        nb   = ttk.Notebook(body)
        nb.pack(fill='both', expand=True, padx=10, pady=8)
        t1 = ttk.Frame(nb); nb.add(t1, text='  📊  Maç Geçmişi  ')
        t2 = ttk.Frame(nb); nb.add(t2, text='  🧠  Zayıf Nokta  ')
        t3 = ttk.Frame(nb); nb.add(t3, text='  💹  Rating  ')
        t4 = ttk.Frame(nb); nb.add(t4, text='  🤖  Otomatik KDA Analiz  ')
        self._analysis_history_tab(t1)
        self._analysis_weakness_tab(t2)
        self._analysis_rating_tab(t3)
        self._analysis_auto_kda_tab(t4)

    def _analysis_auto_kda_tab(self, parent):
        """Kaydedilen tüm maçları otomatik analiz eder, genel performans raporu üretir."""
        main = tk.Frame(parent, bg=BG_PANEL)
        main.pack(fill='both', expand=True)
        tk.Frame(main, bg=GOLD, height=2).pack(fill='x')
        self._sec(main, '🤖  Otomatik KDA Analizi — Tüm Maçlar')

        result_txt = self._stxt(main, h=28)
        result_txt.pack(fill='both', expand=True, padx=10, pady=4)

        def generate_report():
            result_txt.config(state='normal')
            result_txt.delete('1.0', tk.END)
            matches = self.matches_data.get('matches', [])
            if not matches:
                result_txt.insert('1.0', '⚠ Henüz kayıtlı maç yok.\nBir maç oynayın — GSI otomatik kaydeder!')
                result_txt.config(state='disabled')
                return
            n = len(matches)
            avg_k = sum(m.get('kills',0) for m in matches) / n
            avg_d = sum(m.get('deaths',0) for m in matches) / n
            avg_a = sum(m.get('assists',0) for m in matches) / n
            avg_kd = avg_k / max(avg_d, 0.01)
            wins = sum(1 for m in matches if 'Galibiyet' in m.get('result',''))
            wr = wins / n * 100
            best_map = {}
            for m in matches:
                mp = m.get('map','?')
                best_map.setdefault(mp, []).append(m.get('kills',0))
            best = max(best_map, key=lambda x: sum(best_map[x])/len(best_map[x])) if best_map else '?'

            report = f'🤖  OTOMATİK KDA ANALİZ RAPORU\n{"═"*46}\n\n'
            report += f'📅  Tarih: {datetime.now().strftime("%Y-%m-%d %H:%M")}\n'
            report += f'🎮  Toplam Maç: {n}\n'
            report += f'🏆  Galibiyet Oranı: %{wr:.0f}  ({wins}/{n})\n\n'
            report += f'📊  ORTALAMA İSTATİSTİKLER\n{"─"*36}\n'
            report += f'  Kill:    {avg_k:.1f}\n'
            report += f'  Death:   {avg_d:.1f}\n'
            report += f'  Assist:  {avg_a:.1f}\n'
            report += f'  K/D:     {avg_kd:.2f}\n\n'
            # Değerlendirme
            report += f'🎯  PERFORMANS DEĞERLENDİRMESİ\n{"─"*36}\n'
            if avg_kd >= 1.5:
                report += '  ✅ HARIKA — Ortalamanın çok üstündesin!\n  PRO seviyesine yaklaşıyorsun.\n\n'
            elif avg_kd >= 1.0:
                report += '  ⚖ İYİ — Ortalamanın üstündesin.\n  Spray kontrolü ve positioning geliştirebilirsin.\n\n'
            elif avg_kd >= 0.7:
                report += '  ⚠ GELİŞTİRİLEBİLİR — Eco round yönetimi ve\n  pozisyonlama üzerine çalış.\n\n'
            else:
                report += '  ❌ ÇALIŞMA GEREKLİ — Aim_botz + Deathmatch\n  günlük antrenman şart!\n\n'
            # En iyi harita
            report += f'🗺  EN İYİ HARITA: {best.upper()}\n\n'
            # Son 5 maç trendi
            last5 = matches[-5:]
            trend_kd = [m.get('kd_ratio', round(m.get('kills',1)/max(m.get('deaths',1),1),2)) for m in last5]
            report += f'📈  SON {len(last5)} MAÇ K/D TRENDİ\n{"─"*36}\n'
            for i, (m, kd) in enumerate(zip(last5, trend_kd), 1):
                bar = '█' * min(int(kd * 5), 10)
                report += f'  {i}. {m.get("map","?"):<12}  K/D:{kd:.2f}  {bar}\n'
            result_txt.insert('1.0', report)
            result_txt.config(state='disabled')

        generate_report()
        btn_frame = tk.Frame(main, bg=BG_PANEL)
        btn_frame.pack(fill='x', padx=10, pady=6)
        ttk.Button(btn_frame, text='🔄  Raporu Yenile', style='Gold.TButton',
                   command=generate_report).pack(side='left', padx=4)
 
    # Placeholder menu handlers (basit popup'lar — ileride detay eklenebilir)
    def _menu_map(self):
        try:
            win = self._popup('🗺  Harita', 1000, 700)
            body = tk.Frame(win, bg=BG_BASE)
            body.pack(fill='both', expand=True, padx=8, pady=8)

            left = tk.Frame(body, bg=BG_PANEL, width=260)
            left.pack(side='left', fill='y')
            left.pack_propagate(False)

            tk.Label(left, text='Haritalar', bg=BG_PANEL, fg=GOLD, font=('Consolas', 10, 'bold')).pack(anchor='w', padx=8, pady=(6,2))
            self.map_listbox = tk.Listbox(left, bg=BG_INPUT, fg=TEXT_WHITE, width=28, height=30)
            self.map_listbox.pack(fill='y', padx=8, pady=4)
            self.map_listbox.bind('<<ListboxSelect>>', self.on_map_select)

            btns = tk.Frame(left, bg=BG_PANEL)
            btns.pack(fill='x', padx=8, pady=6)
            tk.Button(btns, text='Resim Ekle', bg=GOLD_DIM, fg=GOLD_BRIGHT, relief='flat', command=self.load_map_gif).pack(side='left', padx=4)
            tk.Button(btns, text='Sil', bg='#2a0000', fg='#ff8888', relief='flat', command=self._delete_map_file).pack(side='left', padx=4)

            right = tk.Frame(body, bg=BG_CARD)
            right.pack(side='right', fill='both', expand=True)
            right.pack_propagate(False)
            tk.Label(right, text='Önizleme', bg=BG_CARD, fg=GOLD, font=('Consolas', 10, 'bold')).pack(anchor='w', padx=8, pady=(6,2))
            self.map_canvas = tk.Canvas(right, bg='#0a0a0e', highlightthickness=0)
            self.map_canvas.pack(fill='both', expand=True, padx=8, pady=8)

            # populate list
            self.map_listbox.delete(0, tk.END)
            for m in self.get_available_maps():
                self.map_listbox.insert(tk.END, m)
        except Exception as e:
            print('menu_map error:', e)

    def _delete_map_file(self):
        sel = self.map_listbox.curselection()
        if not sel:
            messagebox.showwarning('Uyarı', 'Harita seçin!')
            return
        nm = self.map_listbox.get(sel[0])
        # try remove file with common extensions
        removed = False
        for ext in ('.gif', '.png', '.jpg'):
            p = os.path.join(self.maps_dir, f'{nm}{ext}')
            if os.path.exists(p):
                try:
                    os.remove(p)
                    removed = True
                except Exception as e:
                    messagebox.showerror('Hata', f'Harita silinemedi: {e}')
                    return
        if removed:
            self.map_listbox.delete(sel[0])
            messagebox.showinfo('Silindi', f'Harita silindi: {nm}')

    def _menu_utility(self):
        try:
            win = self._popup('💣  Utility')
            tk.Label(win, text='Utility menüsü burada olacak.', bg=BG_CARD, fg=TEXT_WHITE).pack(padx=16, pady=16)
        except:
            pass

    def _menu_aim(self):
        try:
            win = self._popup('🎯  AİM & 2026 Güncel Öneriler', 1000, 720)
            body = tk.Frame(win, bg=BG_BASE)
            body.pack(fill='both', expand=True, padx=8, pady=8)
            nb = ttk.Notebook(body)
            nb.pack(fill='both', expand=True)
            t1 = ttk.Frame(nb); nb.add(t1, text='  🎯  AİM Antrenman  ')
            t2 = ttk.Frame(nb); nb.add(t2, text='  🔧  Crosshair 2026  ')
            t3 = ttk.Frame(nb); nb.add(t3, text='  🗺  Harita Özellikleri 2026  ')
            self._aim_training_tab(t1)
            self._crosshair_tab(t2)
            self._map_features_tab(t3)
        except Exception as e:
            print('AIM menu error:', e)

    def _aim_training_tab(self, parent):
        main = tk.Frame(parent, bg=BG_PANEL)
        main.pack(fill='both', expand=True)
        tk.Frame(main, bg=GOLD, height=2).pack(fill='x')
        self._sec(main, '🎯  2026 Güncel AİM Antrenman Programı')

        content = tk.Frame(main, bg=BG_PANEL)
        content.pack(fill='both', expand=True)

        left_col = tk.Frame(content, bg=BG_PANEL)
        left_col.pack(side='left', fill='both', expand=True, padx=8)
        right_col = tk.Frame(content, bg=BG_PANEL)
        right_col.pack(side='right', fill='both', expand=True, padx=8)

        # Günlük program
        daily = [
            ('🌅 SABAH ISINIŞ (10 dk)', [
                'Aim Botz — Statik hedef 200 kill (warmup)',
                'Movement — Jiggle peek antremanı',
                'Crosshair placement — Baş hizasına odaklan',
            ]),
            ('🔫 ANA ANTRENMAN (30 dk)', [
                'Aim Botz — Hareket eden hedef 500 kill',
                '1v1 server — En az 10 round',
                'Recoil Master — AK47 + M4A4 spray (15 dk)',
            ]),
            ('🎮 UYGULAMA (Maç)', [
                'Deathmatch — 20 dk warmup maca girmeden önce',
                'Premier/Faceit maç oyna',
                'Maç sonrası demo izle',
            ]),
        ]
        for title, items in daily:
            card = tk.Frame(left_col, bg=BG_CARD, padx=12, pady=8)
            card.pack(fill='x', pady=4)
            tk.Label(card, text=title, bg=BG_CARD, fg=GOLD, font=('Consolas', 10, 'bold')).pack(anchor='w')
            for item in items:
                tk.Label(card, text=f'  ▸  {item}', bg=BG_CARD, fg=TEXT_WHITE,
                         font=('Segoe UI', 9), justify='left').pack(anchor='w', pady=1)

        # 2026 meta AIM tavsiyeleri
        meta_tips = [
            ('🧠 2026 AİM META', [
                'Microadjustment önem kazandı — düşük sensitivity tercih',
                'Pre-aim (angle pre-fire) artık şart',
                'Headshot hitbox 2026 güncellemesiyle daha küçüldü',
                'Silent walk + peek kombinasyonu çok etkili',
                'One-tap odağı → CS2 recoil daha öngörülü',
            ]),
            ('📊 Optimal Sensitivity Hesaplama', [
                'eDPI = DPI × İnce Hassasiyet',
                'Öneri eDPI: 600–1200 arası',
                'CS2 için ideal: 800 DPI × 1.0 = eDPI 800',
                '360° dönüş mesafesi: 30–50 cm arası ideal',
                'Pro ort. eDPI (2026): ~823',
            ]),
        ]
        for title, items in meta_tips:
            card = tk.Frame(right_col, bg=BG_CARD, padx=12, pady=8)
            card.pack(fill='x', pady=4)
            tk.Label(card, text=title, bg=BG_CARD, fg=GOLD, font=('Consolas', 10, 'bold')).pack(anchor='w')
            for item in items:
                tk.Label(card, text=f'  ▸  {item}', bg=BG_CARD, fg=TEXT_WHITE,
                         font=('Segoe UI', 9), justify='left').pack(anchor='w', pady=1)

    def _crosshair_tab(self, parent):
        main = tk.Frame(parent, bg=BG_PANEL)
        main.pack(fill='both', expand=True)
        tk.Frame(main, bg=GOLD, height=2).pack(fill='x')
        self._sec(main, '🔧  2026 Crosshair Önerileri (PRO Standart)')

        cross_data = [
            ('s1mple Style (Classic)', 'cl_crosshairsize 2; cl_crosshairthickness 0; cl_crosshairgap -2; cl_crosshairdot 0; cl_crosshaircolor 4; cl_crosshairusealpha 1; cl_crosshairalpha 200'),
            ('NiKo Style (Balanced)', 'cl_crosshairsize 3; cl_crosshairthickness 1; cl_crosshairgap -2; cl_crosshairdot 0; cl_crosshaircolor 1; cl_crosshairusealpha 1; cl_crosshairalpha 200'),
            ('ZywOo Style (Minimal)', 'cl_crosshairsize 1; cl_crosshairthickness 0; cl_crosshairgap -3; cl_crosshairdot 1; cl_crosshaircolor 5; cl_crosshairusealpha 1; cl_crosshairalpha 255'),
            ('m0NESY Style (Small)', 'cl_crosshairsize 2; cl_crosshairthickness 0; cl_crosshairgap -3; cl_crosshairdot 0; cl_crosshaircolor 2; cl_crosshairusealpha 1; cl_crosshairalpha 200'),
            ('donk Style (Tiny)', 'cl_crosshairsize 1; cl_crosshairthickness 0; cl_crosshairgap -2; cl_crosshairdot 0; cl_crosshaircolor 1; cl_crosshairusealpha 1; cl_crosshairalpha 180'),
            ('Beginner Friendly (Large)', 'cl_crosshairsize 4; cl_crosshairthickness 1; cl_crosshairgap -1; cl_crosshairdot 1; cl_crosshaircolor 5; cl_crosshairusealpha 1; cl_crosshairalpha 230'),
        ]
        tips_frame = tk.Frame(main, bg=BG_PANEL)
        tips_frame.pack(fill='both', expand=True, padx=8)
        for name, code in cross_data:
            card = tk.Frame(tips_frame, bg=BG_CARD, padx=10, pady=6)
            card.pack(fill='x', pady=3)
            row = tk.Frame(card, bg=BG_CARD)
            row.pack(fill='x')
            tk.Label(row, text=name, bg=BG_CARD, fg=GOLD,
                     font=('Consolas', 10, 'bold'), width=30, anchor='w').pack(side='left')
            tk.Button(row, text='📋 Kopyala', bg=GOLD_DIM, fg=GOLD_BRIGHT,
                      relief='flat', font=('Consolas', 8), padx=8,
                      command=lambda c=code: self.clip(c)).pack(side='right')
            tk.Label(card, text=code, bg=BG_CARD, fg=TEXT_MUTED,
                     font=('Consolas', 8), anchor='w').pack(fill='x', pady=(2, 0))

    def _map_features_tab(self, parent):
        main = tk.Frame(parent, bg=BG_PANEL)
        main.pack(fill='both', expand=True)
        tk.Frame(main, bg=GOLD, height=2).pack(fill='x')
        self._sec(main, '🗺  2026 CS2 Harita Özellikleri & Değişiklikler')

        map_info = {
            'de_dust2':   '• Long A köşeleri 2024 güncellemesiyle düzlendi\n• CT cross daha dar → T avantajı azaldı\n• Xbox kutusunun arkası yeni açı verdi\n• Oyun: Klasik meta, Long + B split hâlâ güçlü',
            'de_mirage':  '• CT spawn yakını ramp düzenlendi\n• A short merdiveni yeniden şekillendirildi\n• Mid window tutma pozisyonu değişti\n• Oyun: Apartment push zayıfladı, CT agresif meta güçlü',
            'de_inferno': '• Banana genişletildi → CT daha zor tutabiliyor\n• Apartments bazı geçişleri kapatıldı\n• B site platform değişiklikleri\n• Oyun: 5B rush hâlâ tehlikeli, molotov kritik',
            'de_nuke':    '• Outside ramp köşeleri değişti\n• B site hava deliği iyileştirildi\n• Secret geçişi biraz daha hızlandı\n• Oyun: AWP outside baskısı çok güçlü',
            'de_ancient': '• 2024\'te havuz kaldırıldı → oyun hızlandı\n• C1/C2 yeni açılar eklendi\n• A main genişletildi\n• Oyun: Mid kontrolü maçı belirliyor',
            'de_anubis':  '• 2025\'te aktif pool\'a girdi, güncel harita\n• A site waterfalls değişti\n• B canal tam ortasında yeni spot\n• Oyun: Taze meta, pro oyuncularda çok araştırılıyor',
            'de_vertigo': '• Yüksek kat geçişleri yeniden düzenlendi\n• A site köprü kaldırıldı (2024)\n• B short genişletildi\n• Oyun: Scaffold push güçlü, utility şart',
        }
        canvas_frame = tk.Frame(main, bg=BG_PANEL)
        canvas_frame.pack(fill='both', expand=True, padx=8, pady=4)
        for map_name, info in map_info.items():
            card = tk.Frame(canvas_frame, bg=BG_CARD, padx=14, pady=8)
            card.pack(fill='x', pady=3)
            tk.Label(card, text=map_name.upper(), bg=BG_CARD, fg=GOLD_BRIGHT,
                     font=('Consolas', 11, 'bold')).pack(anchor='w')
            tk.Label(card, text=info, bg=BG_CARD, fg=TEXT_WHITE,
                     font=('Segoe UI', 9), justify='left', anchor='w').pack(anchor='w', pady=(4, 0))

    def _menu_weapon(self):
        try:
            win = self._popup('🔫  Silah')
            tk.Label(win, text='Silah menüsü burada olacak.', bg=BG_CARD, fg=TEXT_WHITE).pack(padx=16, pady=16)
        except:
            pass

    def _menu_tactic(self):
        try:
            win = self._popup('🧠  Taktik')
            tk.Label(win, text='Taktik menüsü burada olacak.', bg=BG_CARD, fg=TEXT_WHITE).pack(padx=16, pady=16)
        except:
            pass

    def _menu_config(self):
        try:
            win = self._popup('⚙  PRO Config & 2026 Önerilen Ayarlar', 1050, 720)
            body = tk.Frame(win, bg=BG_BASE)
            body.pack(fill='both', expand=True, padx=8, pady=8)
            nb = ttk.Notebook(body)
            nb.pack(fill='both', expand=True)
            t1 = ttk.Frame(nb); nb.add(t1, text='  ⚙  PRO Configs 2026  ')
            t2 = ttk.Frame(nb); nb.add(t2, text='  🖥  Video Ayarları  ')
            t3 = ttk.Frame(nb); nb.add(t3, text='  🎮  Launch Options  ')
            self._pro_config_tab(t1)
            self._video_settings_tab(t2)
            self._launch_options_tab(t3)
        except Exception as e:
            print('Config menu error:', e)

    def _pro_config_tab(self, parent):
        main = tk.Frame(parent, bg=BG_PANEL)
        main.pack(fill='both', expand=True)
        tk.Frame(main, bg=GOLD, height=2).pack(fill='x')
        self._sec(main, '⚙  PRO Oyuncu Ayarları — 2026 Güncel')

        scroll_frame = tk.Frame(main, bg=BG_PANEL)
        scroll_frame.pack(fill='both', expand=True, padx=8, pady=4)

        for player, cfg in PRO_CONFIGS.items():
            card = tk.Frame(scroll_frame, bg=BG_CARD, padx=12, pady=8)
            card.pack(fill='x', pady=4)
            hdr = tk.Frame(card, bg=BG_CARD)
            hdr.pack(fill='x')
            tk.Label(hdr, text=f'👤 {player}', bg=BG_CARD, fg=GOLD_BRIGHT,
                     font=('Consolas', 12, 'bold')).pack(side='left')
            row1 = tk.Frame(card, bg=BG_CARD)
            row1.pack(fill='x', pady=(4, 0))
            info_text = (f"Sens: {cfg['sensitivity']}  |  DPI: {cfg['dpi']}  |  eDPI: {round(float(cfg['sensitivity']) * int(cfg['dpi']))}  |  "
                         f"Res: {cfg['resolution']}  ({cfg['aspect']})")
            tk.Label(row1, text=info_text, bg=BG_CARD, fg=CYAN,
                     font=('Consolas', 9)).pack(anchor='w')
            launch_row = tk.Frame(card, bg=BG_CARD)
            launch_row.pack(fill='x', pady=2)
            tk.Label(launch_row, text=cfg['launch'], bg=BG_CARD, fg=TEXT_MUTED,
                     font=('Consolas', 8)).pack(side='left')
            tk.Button(launch_row, text='📋', bg='#1a1800', fg=GOLD, relief='flat',
                      font=('Consolas', 8), padx=6,
                      command=lambda c=cfg['launch']: self.clip(c)).pack(side='right')
            cross_row = tk.Frame(card, bg=BG_CARD)
            cross_row.pack(fill='x', pady=2)
            tk.Label(cross_row, text=f"CH: {cfg['crosshair']}", bg=BG_CARD, fg=TEXT_MUTED,
                     font=('Consolas', 8)).pack(side='left')
            tk.Button(cross_row, text='📋', bg='#1a1800', fg=GOLD, relief='flat',
                      font=('Consolas', 8), padx=6,
                      command=lambda c=cfg['crosshair']: self.clip(c)).pack(side='right')
            tk.Label(card, text=f'💡 {cfg["notes"]}', bg=BG_CARD, fg=GOLD_DIM,
                     font=('Segoe UI', 8), anchor='w').pack(anchor='w', pady=(2, 0))

    def _video_settings_tab(self, parent):
        main = tk.Frame(parent, bg=BG_PANEL)
        main.pack(fill='both', expand=True)
        tk.Frame(main, bg=GOLD, height=2).pack(fill='x')
        self._sec(main, '🖥  2026 Önerilen CS2 Video Ayarları')

        settings = [
            ('Çözünürlük', '1280x960 (4:3 Stretched) veya 1920x1080 (16:9)', GOLD),
            ('Görüntü Kalitesi', 'Low — FPS için', GREEN_OK),
            ('Global Gölgeler', 'Kapalı (Off)', GREEN_OK),
            ('Model/Doku Detayı', 'Low', GREEN_OK),
            ('Efekt Detayı', 'Low', GREEN_OK),
            ('Gölge Kalitesi', 'Low / Very Low', GREEN_OK),
            ('Hareket Bulanıklığı', 'Kapalı (OFF) — ŞAR ŞART!', RED_ALERT),
            ('Multisampling AA', 'Kapalı veya 2x', ORANGE),
            ('FidelityFX Super Res', 'Kapalı (eğer FPS yeterliyse)', ORANGE),
            ('NVIDIA Reflex', 'Enabled + Boost (varsa)', CYAN),
            ('V-Sync', 'Kapalı (OFF)', RED_ALERT),
            ('Maksimum FPS', '0 (sınırsız) veya monitör Hz x2', GREEN_OK),
            ('Parlaklık', '%110 — hedefler daha görünür', GOLD),
        ]
        for setting, value, color in settings:
            row = tk.Frame(main, bg=BG_CARD)
            row.pack(fill='x', padx=8, pady=2)
            tk.Label(row, text=f'  {setting}', bg=BG_CARD, fg=TEXT_MUTED,
                     font=('Segoe UI', 10), width=30, anchor='w').pack(side='left')
            tk.Label(row, text=value, bg=BG_CARD, fg=color,
                     font=('Consolas', 9, 'bold')).pack(side='left', padx=8)

    def _launch_options_tab(self, parent):
        main = tk.Frame(parent, bg=BG_PANEL)
        main.pack(fill='both', expand=True)
        tk.Frame(main, bg=GOLD, height=2).pack(fill='x')
        self._sec(main, '🎮  2026 Önerilen Launch Options')

        options = [
            ('-novid', 'Giriş videosunu atla', GREEN_OK),
            ('-tickrate 128', 'Offline server 128 tick', GOLD),
            ('+fps_max 0', 'FPS limitini kaldır', GREEN_OK),
            ('-high', 'Oyuna yüksek öncelik ver (Windows)', CYAN),
            ('-nojoy', 'Joystick desteğini kapat (FPS kazanır)', ORANGE),
            ('+cl_forcepreload 1', 'Haritaları önceden yükle', ORANGE),
            ('+rate 786432', 'Maksimum network rate (2026 standart)', GOLD),
            ('+cl_cmdrate 128', 'Client komut oranı', GOLD),
            ('+cl_updaterate 128', 'Sunucu güncelleme oranı', GOLD),
            ('+cl_interp_ratio 1', 'İnterpolasyon oranı (minimize)', GREEN_OK),
            ('-fullscreen', 'Tam ekran mod', GREEN_OK),
        ]
        full_cmd = ' '.join(o[0] for o in options[:8])
        # Tam komut kopyala butonu
        copy_card = tk.Frame(main, bg='#0a1008', padx=12, pady=8)
        copy_card.pack(fill='x', padx=8, pady=6)
        tk.Label(copy_card, text='📋 Önerilen Tam Launch Command:', bg='#0a1008', fg=GOLD,
                 font=('Consolas', 9, 'bold')).pack(anchor='w')
        tk.Label(copy_card, text=full_cmd, bg='#0a1008', fg=GREEN_OK,
                 font=('Consolas', 9), wraplength=800, justify='left').pack(anchor='w', pady=4)
        tk.Button(copy_card, text='📋 Kopyala', bg=GOLD_DIM, fg=GOLD_BRIGHT, relief='flat',
                  command=lambda: self.clip(full_cmd)).pack(anchor='w')
        tk.Frame(main, bg=GOLD_DIM, height=1).pack(fill='x', padx=8, pady=4)
        for opt, desc, color in options:
            row = tk.Frame(main, bg=BG_CARD)
            row.pack(fill='x', padx=8, pady=2)
            tk.Label(row, text=f'  {opt}', bg=BG_CARD, fg=color,
                     font=('Consolas', 9, 'bold'), width=28, anchor='w').pack(side='left')
            tk.Label(row, text=desc, bg=BG_CARD, fg=TEXT_MUTED,
                     font=('Segoe UI', 9)).pack(side='left', padx=8)

    def _menu_economy_team(self):
        try:
            win = self._popup('💹  Takım Ekonomi Analizi', 900, 640)
            body = tk.Frame(win, bg=BG_BASE)
            body.pack(fill='both', expand=True, padx=8, pady=8)
            self._sec(body, '💹  Anlık Takım Ekonomisi + KDA Bazlı Öneri')

            # Takım para durumu
            info_card = tk.Frame(body, bg=BG_CARD, padx=14, pady=10)
            info_card.pack(fill='x', pady=6)
            tk.Label(info_card, text='CT Takım Parası', bg=BG_CARD, fg=BLUE_INFO,
                     font=('Consolas', 10, 'bold')).pack(anchor='w')
            ct_total = self.team_eco['ct'].get('total', 0)
            t_total  = self.team_eco['t'].get('total', 0)
            ct_dec, ct_clr, _ = self._team_buy_decision(self.team_eco['ct'].get('monies', []), 'ct', 0)
            t_dec,  t_clr,  _ = self._team_buy_decision(self.team_eco['t'].get('monies',  []), 't',  0)
            tk.Label(info_card, text=f'CT:  ${ct_total:,}  →  {ct_dec}', bg=BG_CARD, fg=ct_clr,
                     font=('Consolas', 14, 'bold')).pack(anchor='w', pady=2)
            tk.Label(info_card, text=f'T :  ${t_total:,}  →  {t_dec}', bg=BG_CARD, fg=t_clr,
                     font=('Consolas', 14, 'bold')).pack(anchor='w', pady=2)

            # KDA bazlı öneri
            kd = self.live['kills'] / max(self.live['deaths'], 1)
            money = self.live['money']
            self._sec(body, '⚡  KDA + Ekonomi Bazlı Kişisel Öneri')
            advice_card = tk.Frame(body, bg='#0a100a', padx=14, pady=10)
            advice_card.pack(fill='x', pady=4)
            if kd >= 2.0 and money >= 4750:
                rec = '🔥 Full buy al ve agresif entry fragger rol üstlen. Performansın çok iyi!'
                rec_clr = GREEN_OK
            elif kd >= 1.5 and money >= 2700:
                rec = '✅ Force buy veya full buy düşün. KD iyi, takımına öncülük edebilirsin.'
                rec_clr = GOLD
            elif kd < 1.0 and money < 2000:
                rec = '⚠ Eco round. Öne çıkma, takıma destek ol. Para biriktir.'
                rec_clr = ORANGE
            elif money < 1800:
                rec = '💰 Para az — eco koy. Pistol ile info al, risk alma.'
                rec_clr = RED_ALERT
            else:
                rec = '⚖ Dengeli durum. Takımla aynı satın alma kararı al.'
                rec_clr = CYAN
            tk.Label(advice_card, text=rec, bg='#0a100a', fg=rec_clr,
                     font=('Segoe UI', 11), wraplength=800, justify='left').pack(anchor='w')

            # Ekonomi bilgi tablosu
            self._sec(body, '📊  Ekonomi Eşikleri (2026)')
            table = tk.Frame(body, bg=BG_CARD)
            table.pack(fill='x', padx=8, pady=4)
            rows = [
                ('Durum', 'T Min', 'CT Min', 'Açıklama'),
                ('Full Buy', '$4,750', '$5,200', 'Rifle + Armor + Utility'),
                ('Force Buy', '$2,700', '$2,900', 'Budget rifle + armor'),
                ('Half Buy', '$1,800', '$2,000', 'SMG veya pistol + armor'),
                ('Eco', '<$1,800', '<$2,000', 'Para biriktir'),
            ]
            for i, row in enumerate(rows):
                bg = HIGHLIGHT if i == 0 else (BG_CARD if i % 2 == 0 else BG_CARD2)
                fg = GOLD if i == 0 else TEXT_WHITE
                rw = tk.Frame(table, bg=bg)
                rw.pack(fill='x')
                for j, cell in enumerate(row):
                    w = [12, 8, 8, 30][j]
                    tk.Label(rw, text=cell, bg=bg, fg=fg, font=('Consolas', 9, 'bold' if i == 0 else 'normal'),
                             width=w, anchor='w', padx=4, pady=3).pack(side='left')
        except Exception as e:
            print('Economy menu error:', e)

    def _menu_settings(self):
        try:
            win = self._popup('Ayarlar', 900, 640)
            body = tk.Frame(win, bg=BG_PANEL)
            body.pack(fill='both', expand=True, padx=10, pady=8)
            nb_s = ttk.Notebook(body)
            nb_s.pack(fill='both', expand=True)
            t_panel = ttk.Frame(nb_s); nb_s.add(t_panel, text='  Panel & Tema  ')
            t_upd   = ttk.Frame(nb_s); nb_s.add(t_upd,   text='  Guncelleme  ')

            # === TAB 1: PANEL & TEMA ===
            p1 = tk.Frame(t_panel, bg=BG_PANEL)
            p1.pack(fill='both', expand=True, padx=8, pady=6)
            self._sec(p1, 'Renk Temasi (hemen uygulanir)')
            clr_card = tk.Frame(p1, bg=BG_CARD, padx=10, pady=8)
            clr_card.pack(fill='x', pady=4)
            self._theme_var = tk.StringVar(value=self.settings.get('accent_color', GOLD))
            themes = [('Altin', GOLD), ('Mavi', BLUE_INFO), ('Yesil', GREEN_OK),
                      ('Kirmizi', RED_ALERT), ('Mor', PURPLE), ('Cyan', CYAN)]
            for tname, tclr in themes:
                rb = tk.Radiobutton(clr_card, text=tname, variable=self._theme_var, value=tclr,
                                    bg=BG_CARD, fg=tclr, selectcolor='#1a1800',
                                    activebackground=BG_CARD, font=('Segoe UI', 9, 'bold'))
                rb.pack(side='left', padx=8)
            self._sec(p1, 'Panel Ayarlari')
            panel_card = tk.Frame(p1, bg=BG_CARD, padx=10, pady=8)
            panel_card.pack(fill='x', pady=4)
            self._panel_chk_vars = {}
            opts = [('sound_hit_feedback', 'Kill sesi (winsound - garantili)', True),
                    ('auto_save_matches',  'Maclari otomatik kaydet (Faceit dahil)', True),
                    ('always_on_top',      'Pencereyi her zaman ustte tut', False)]
            for key, lbl, default in opts:
                v = tk.BooleanVar(value=self.settings.get(key, default))
                self._panel_chk_vars[key] = v
                ttk.Checkbutton(panel_card, text=lbl, variable=v).pack(anchor='w', pady=2)
            self._sec(p1, 'GSI Config')
            gsi_card = tk.Frame(p1, bg=BG_CARD, padx=10, pady=8)
            gsi_card.pack(fill='x', pady=4)
            tk.Label(gsi_card, text='cfg/gamestate_integration_cs2pro.cfg dosyasina kaydet', bg=BG_CARD, fg=GOLD_DIM, font=('Segoe UI',8)).pack(anchor='w')
            tk.Button(gsi_card, text='GSI Config Kopyala', bg=GOLD_DIM, fg=GOLD_BRIGHT, relief='flat',
                      command=lambda: self.clip(GSI_CONFIG)).pack(anchor='w', pady=6)

            # === TAB 2: GUNCELLEME ===
            p2 = tk.Frame(t_upd, bg=BG_PANEL)
            p2.pack(fill='both', expand=True, padx=8, pady=6)
            self._sec(p2, 'Guncelleme Kaynaklari')
            src_frame = tk.Frame(p2, bg=BG_CARD)
            src_frame.pack(fill='x', padx=0, pady=4)
            src_frame = tk.Frame(body, bg=BG_CARD)
            src_frame.pack(fill='x', padx=8, pady=6)
            self.update_src_lb = tk.Listbox(src_frame, bg=BG_INPUT, fg=TEXT_WHITE, height=6)
            self.update_src_lb.pack(side='left', fill='both', expand=True, padx=(4,2), pady=4)
            sb = tk.Scrollbar(src_frame, command=self.update_src_lb.yview)
            sb.pack(side='left', fill='y')
            self.update_src_lb.config(yscrollcommand=sb.set)

            right_fr = tk.Frame(src_frame, bg=BG_CARD)
            right_fr.pack(side='left', fill='y', padx=6)
            tk.Label(right_fr, text='Yeni URL:', bg=BG_CARD, fg=TEXT_MUTED).pack(anchor='w')
            self.update_src_entry = self._ent(right_fr, w=40)
            self.update_src_entry.pack(pady=4)
            tk.Button(right_fr, text='Ekle', bg=GOLD_DIM, fg=GOLD_BRIGHT, relief='flat', command=self._add_update_source).pack(fill='x', pady=2)
            tk.Button(right_fr, text='Kaldır', bg='#2a0000', fg='#ff8888', relief='flat', command=self._remove_update_source).pack(fill='x', pady=2)

            # Auto-update controls
            self._sec(body, '🔁  Otomatik Güncelleme')
            au_frame = tk.Frame(body, bg=BG_CARD)
            au_frame.pack(fill='x', padx=8, pady=6)
            self.auto_update_var = tk.BooleanVar(value=self.settings.get('auto_update', False))
            ttk.Checkbutton(au_frame, text='Otomatik güncellemeyi etkinleştir', variable=self.auto_update_var).pack(anchor='w', pady=2)
            tk.Label(au_frame, text='Periyot (saniye):', bg=BG_CARD, fg=TEXT_MUTED).pack(anchor='w')
            self.update_interval_spin = tk.Spinbox(au_frame, from_=60, to=86400, width=8)
            self.update_interval_spin.delete(0, 'end')
            self.update_interval_spin.insert(0, str(self.settings.get('update_interval', 3600)))
            self.update_interval_spin.pack(anchor='w', pady=4)
            tk.Button(au_frame, text='Güncelle Şimdi', style='Gold.TButton', command=self._check_for_updates).pack(pady=6)

            # Save / Close
            foot = tk.Frame(win, bg=BG_PANEL)
            foot.pack(fill='x', side='bottom', padx=10, pady=8)
            tk.Button(foot, text='Kaydet', bg=GOLD_DIM, fg=GOLD_BRIGHT, relief='flat', command=lambda: self._save_settings_from_ui(win)).pack(side='right')

            # Populate list
            self.update_src_lb.delete(0, tk.END)
            for s in self.settings.get('update_sources', [self.UPDATE_URL]):
                self.update_src_lb.insert(tk.END, s)
        except Exception as e:
            print('Settings window error:', e)

    def _add_update_source(self):
        url = self.update_src_entry.get().strip()
        if not url:
            return
        self.update_src_lb.insert(tk.END, url)
        self.update_src_entry.delete(0, 'end')

    def _remove_update_source(self):
        sel = self.update_src_lb.curselection()
        if not sel:
            return
        self.update_src_lb.delete(sel[0])

    def _save_settings_from_ui(self, win=None):
        # Renk temasi
        try:
            self.settings['accent_color'] = self._theme_var.get()
        except Exception:
            pass
        # Panel checkbox'lari
        try:
            for key, var in self._panel_chk_vars.items():
                self.settings[key] = var.get()
        except Exception:
            pass
        # Guncelleme kaynaklari
        try:
            srcs = [self.update_src_lb.get(i) for i in range(self.update_src_lb.size())]
            self.settings['update_sources'] = srcs
            self.settings['auto_update'] = bool(self.auto_update_var.get())
        except Exception:
            pass
        try:
            self.settings['update_interval'] = int(self.update_interval_spin.get())
        except Exception:
            self.settings['update_interval'] = 3600
        # Always on top uygula
        try:
            self.root.attributes('-topmost', bool(self.settings.get('always_on_top', False)))
        except Exception:
            pass
        self.save_settings()
        try:
            self._stop_auto_update_worker()
        except Exception:
            pass
        try:
            self._start_auto_update_worker()
        except Exception:
            pass
        messagebox.showinfo('Ayarlar', 'Ayarlar kaydedildi!\nRenk temasi bir sonraki acilista tam olarak uygulanir.')
        if win:
            win.destroy()

    def _analysis_history_tab(self, parent):
        main = tk.Frame(parent, bg=BG_PANEL)
        main.pack(fill='both', expand=True)
        tk.Frame(main, bg=GOLD, height=2).pack(fill='x')

        self._sec(main, '📋  Otomatik Maç Geçmişi (Kalıcı Kayıt)')

        # Özet istatistik satırı
        self.match_summary_lbl = tk.Label(main, text='—', bg=BG_CARD, fg=GOLD,
                font=('Consolas', 9), padx=10, pady=4)
        self.match_summary_lbl.pack(fill='x', padx=10, pady=(4, 0))

        self.match_lb = self._lb(main, h=18, fs=9)
        self.match_lb.pack(fill='both', expand=True, padx=10, pady=4)
        self._load_match_history()

        btn_frame = tk.Frame(main, bg=BG_PANEL)
        btn_frame.pack(fill='x', padx=10, pady=6)
        ttk.Button(btn_frame, text='🗑  Seçili Sil', style='Danger.TButton',
                   command=self._del_match).pack(side='left', padx=4)
        ttk.Button(btn_frame, text='🗑  Tümünü Sil', style='Danger.TButton',
                   command=self._clear_all_matches).pack(side='left', padx=4)
        ttk.Button(btn_frame, text='🔄  Yenile', style='Gold.TButton',
                   command=self._load_match_history).pack(side='left', padx=4)

    def _load_match_history(self):
        try:
            self.match_lb.delete(0, tk.END)
            matches = list(reversed(self.matches_data.get('matches', [])))
            if not matches:
                self.match_lb.insert(tk.END, '  Henüz kayıtlı maç yok. Bir maç oyna!')
                return
            for m in matches:
                res_clr = '✅' if 'Galibiyet' in m.get('result', '') else '❌'
                kd   = m.get('kd_ratio', round(m.get('kills',0) / max(m.get('deaths',1), 1), 2))
                grade = m.get('grade', '?')
                line = (f"{res_clr}  {m.get('date', '?'):<16}  {m.get('map', '?'):<12}  "
                        f"K:{m.get('kills',0):>2} D:{m.get('deaths',0):>2} A:{m.get('assists',0):>2}  "
                        f"KD:{kd:.2f}  [{grade}]  Skor:{m.get('ct_score',0)}-{m.get('t_score',0)}")
                self.match_lb.insert(tk.END, line)
            # Genel istatistik hesapla
            if hasattr(self, 'match_summary_lbl') and matches:
                total = len(matches)
                avg_k = round(sum(m.get('kills',0) for m in matches) / total, 1)
                avg_d = round(sum(m.get('deaths',0) for m in matches) / total, 1)
                avg_a = round(sum(m.get('assists',0) for m in matches) / total, 1)
                avg_kd = round(avg_k / max(avg_d, 0.1), 2)
                wins = sum(1 for m in matches if 'Galibiyet' in m.get('result',''))
                wr = round(wins / total * 100)
                self.match_summary_lbl.config(
                    text=f"Toplam: {total} maç  |  Galibiyet: %{wr}  |  Ort. KDA: {avg_k}/{avg_d}/{avg_a}  |  Ort. K/D: {avg_kd}")
        except Exception as e:
            pass

    def _del_match(self):
        sel = self.match_lb.curselection()
        if not sel:
            return
        del self.matches_data['matches'][sel[0]]
        self._save_matches()
        self._load_match_history()

    def _clear_all_matches(self):
        if messagebox.askyesno('Temizle', 'Tüm maç geçmişi silinsin mi?'):
            self.matches_data['matches'] = []
            self._save_matches()
            self._load_match_history()

    def _analysis_weakness_tab(self, parent):
        main = tk.Frame(parent, bg=BG_PANEL)
        main.pack(fill='both', expand=True)
        tk.Frame(main, bg=GOLD, height=2).pack(fill='x')
        self._sec(main, '🧠  Zayıf Nokta Analizi')
        card = tk.Frame(main, bg=BG_CARD, padx=20, pady=16)
        card.pack(fill='x', padx=10, pady=10)
        tk.Label(card, text='Kendinizi Değerlendirin (1-10):', bg=BG_CARD, fg=GOLD,
                 font=('Consolas', 11, 'bold')).pack(anchor='w', pady=4)
        self.weakness_vars = {}
        skills = [('Aim (headshot oranı)', 'aim'), ('Utility kullanımı', 'utility'),
                  ('Pozisyonlama', 'positioning'), ('Ekonomi yönetimi', 'economy'),
                  ('Takım iletişimi', 'communication'), ('Rotasyon kararları', 'rotation'),
                  ('Prefire / Açı okuma', 'prefire'), ('Spray kontrolü', 'spray')]
        for name, key in skills:
            row = tk.Frame(card, bg=BG_CARD)
            row.pack(fill='x', pady=3)
            tk.Label(row, text=name, bg=BG_CARD, fg=TEXT_WHITE,
                     font=('Segoe UI', 10), width=28, anchor='w').pack(side='left')
            var = tk.IntVar(value=5)
            self.weakness_vars[key] = var
            sc  = ttk.Scale(row, from_=1, to=10, variable=var, orient='horizontal')
            sc.pack(side='left', padx=8, fill='x', expand=True)
            lbl = tk.Label(row, text='5', bg=BG_CARD, fg=GOLD,
                           font=('Consolas', 10, 'bold'), width=3)
            lbl.pack(side='left')
            sc.config(command=lambda v, l=lbl: l.config(text=str(int(float(v)))))
        ttk.Button(card, text='🧠  Analiz Et', style='Gold.TButton',
                   command=self._analyze_weaknesses).pack(pady=12)
        self.weakness_result = self._txt(main, h=10, wrap=tk.WORD)
        self.weakness_result.pack(fill='both', expand=True, padx=10, pady=8)
        self.weakness_result.config(state='disabled')

    def _analyze_weaknesses(self):
        scores  = {k: v.get() for k, v in self.weakness_vars.items()}
        weakest = sorted(scores.items(), key=lambda x: x[1])[:3]
        recs    = {
            'aim':           'Günlük aim_botz antrenmanı. Hedef: %60+ HS oranı.',
            'utility':       'Her harita için en az 5 lineup öğren.',
            'positioning':   'Pro demoları izle — HLTV.org.',
            'economy':       'Her round başında para sayısını takip et.',
            'communication': 'Kısa ve net callout yap.',
            'rotation':      'Mini-harita\'yı sürekli izle.',
            'prefire':       'Prefire haritalarında çalış.',
            'spray':         'Recoil Master haritasında günlük 15 dk.',
        }
        self.weakness_result.config(state='normal')
        self.weakness_result.delete('1.0', tk.END)
        t  = f'🧠  ZAYIF NOKTA ANALİZİ\n{"━"*36}\n\n'
        for i, (skill, score) in enumerate(weakest, 1):
            bar = '█' * score + '░' * (10 - score)
            t += f'{i}. {skill.upper():<20} [{bar}] {score}/10\n'
            t += f'   ➜ {recs[skill]}\n\n'
        self.weakness_result.insert('1.0', t)
        self.weakness_result.config(state='disabled')

    def _analysis_rating_tab(self, parent):
        main = tk.Frame(parent, bg=BG_PANEL)
        main.pack(fill='both', expand=True)
        tk.Frame(main, bg=GOLD, height=2).pack(fill='x')
        self._sec(main, '💹  HLTV Rating Hesaplayıcı')
        card = tk.Frame(main, bg=BG_CARD, padx=20, pady=16)
        card.pack(fill='x', padx=10, pady=10)
        self.rating_entries = {}
        fields = [('Kills', 'kills', '22'), ('Deaths', 'deaths', '18'), ('Assists', 'assists', '5'),
                  ('Headshots', 'headshots', '12'), ('Rounds', 'rounds', '25'), ('ADR', 'adr', '85')]
        for i, (lbl, key, default) in enumerate(fields):
            row = tk.Frame(card, bg=BG_CARD)
            row.pack(fill='x', pady=3)
            tk.Label(row, text=f'{lbl}:', bg=BG_CARD, fg=TEXT_MUTED,
                     font=('Segoe UI', 10), width=14, anchor='w').pack(side='left')
            e = self._ent(row, w=10)
            e.insert(0, default)
            e.pack(side='left', padx=8)
            self.rating_entries[key] = e
        ttk.Button(card, text='💹  Hesapla', style='Gold.TButton',
                   command=self._calc_rating).pack(pady=10)
        self.rating_result = self._txt(main, h=12, wrap=tk.WORD)
        self.rating_result.pack(fill='both', expand=True, padx=10, pady=8)
        self.rating_result.config(state='disabled')

    def _calc_rating(self):
        try:
            k   = int(self.rating_entries['kills'].get())
            d   = int(self.rating_entries['deaths'].get())
            a   = int(self.rating_entries['assists'].get())
            hs  = int(self.rating_entries['headshots'].get())
            rnd = int(self.rating_entries['rounds'].get())
            adr = float(self.rating_entries['adr'].get())
            kpr  = k / rnd
            apr  = a / rnd
            kast = min(0.95, (k + a) / rnd * 0.7 + 0.3)
            impact = 2.13 * kpr + 0.42 * apr - 0.41
            rating = 0.0073 * (kast * 100) + 0.3591 * (k / rnd) - 0.5329 * (d / rnd) + 0.2372 * impact + 0.0032 * adr + 0.1587
            rating = max(0.5, min(2.5, rating))
            grade  = ('S+ Tanrısal' if rating >= 1.5 else 'A Çok İyi' if rating >= 1.2 else
                      'B Orta' if rating >= 1.0 else 'C Düşük')
            self.rating_result.config(state='normal')
            self.rating_result.delete('1.0', tk.END)
            t  = f'💹  HLTV RATING 2.0\n{"━"*36}\n\nRating:  {rating:.2f}  [{grade}]\n\n'
            t += f'KPR: {kpr:.2f}  |  DPR: {d / rnd:.2f}  |  HS: {hs / k * 100:.0f}%  |  ADR: {adr}\n'
            self.rating_result.insert('1.0', t)
            self.rating_result.config(state='disabled')
        except:
            messagebox.showerror('Hata', 'Geçerli sayılar girin!')

    # ... diğer menüler (map, utility, aim, weapon, tactic, config, economy, settings) aynen önceki gibi kalabilir.
    # Kısalık için buraya eklemiyorum, ancak orijinal kodda tüm menüler tanımlıdır.

    # ═══════════════════════════════════════════════════════════
    #  F9 LINEUP OVERLAY
    # ═══════════════════════════════════════════════════════════
    def toggle_overlay(self):
        if self.overlay_win and self.overlay_win.winfo_exists():
            self.close_overlay()
        else:
            self.open_overlay()

    def close_overlay(self):
        if self.overlay_win and self.overlay_win.winfo_exists():
            self.overlay_win.destroy()
        self.overlay_win = None

    def open_overlay(self):
        mk  = self._map_key()
        ov  = tk.Toplevel(self.root)
        self.overlay_win = ov
        ov.title('⚡ Lineup Overlay  [F9/ESC kapat]')
        ov.configure(bg=BG_BASE)
        ov.attributes('-topmost', True)
        ov.attributes('-alpha', 0.93)
        ov.geometry('1100x700+80+60')
        ov.bind('<F9>',     lambda e: self.close_overlay())
        ov.bind('<Escape>', lambda e: self.close_overlay())

        tk.Frame(ov, bg=GOLD, height=2).pack(fill='x')
        hdr = tk.Frame(ov, bg='#0a0a0a', height=44)
        hdr.pack(fill='x')
        hdr.pack_propagate(False)
        tk.Frame(hdr, bg=GOLD, width=4).pack(side='left', fill='y')
        tk.Label(hdr, text='⚡  LINEUP OVERLAY', bg='#0a0a0a', fg=GOLD_BRIGHT,
                 font=('Consolas', 15, 'bold')).pack(side='left', padx=10)
        tk.Label(hdr, text=f'[ {mk.replace("de_", "").upper() if mk else "Harita Seç"} ]',
                 bg='#0a0a0a', fg=GOLD, font=('Consolas', 12)).pack(side='left', padx=6)
        tk.Label(hdr, text='F9 / ESC → Kapat', bg='#0a0a0a', fg=TEXT_MUTED,
                 font=('Consolas', 9)).pack(side='right', padx=14)
        tk.Frame(ov, bg=GOLD_DIM, height=1).pack(fill='x')

        body  = tk.Frame(ov, bg=BG_BASE)
        body.pack(fill='both', expand=True)

        left  = tk.Frame(body, bg=BG_PANEL, width=560)
        left.pack(side='left', fill='both', expand=True)
        left.pack_propagate(False)
        self.ov_canvas = tk.Canvas(left, bg='#0c0c0c', highlightthickness=0)
        self.ov_canvas.pack(fill='both', expand=True, padx=4, pady=4)

        right = tk.Frame(body, bg=BG_CARD, width=420)
        right.pack(side='right', fill='y')
        right.pack_propagate(False)
        tk.Frame(right, bg=GOLD, height=2).pack(fill='x')

        fr = tk.Frame(right, bg=BG_CARD)
        fr.pack(fill='x', padx=8, pady=6)
        tk.Label(fr, text='FİLTRE:', bg=BG_CARD, fg=TEXT_MUTED,
                 font=('Consolas', 9)).pack(side='left', padx=4)
        self.ov_filter_var = tk.StringVar(value='Hepsi')
        for ft in ['Hepsi', 'Smoke', 'Flash', 'Molotov']:
            clr = TYPE_CLR.get(ft, GOLD)
            tk.Button(fr, text=ft, bg='#1a1a1a', fg=clr if ft != 'Hepsi' else GOLD,
                      font=('Consolas', 9, 'bold'), relief='flat', padx=8, pady=3,
                      activebackground=HIGHLIGHT, activeforeground=GOLD_BRIGHT,
                      command=lambda f=ft: self._ov_filter(f, mk)).pack(side='left', padx=2)

        tk.Frame(right, bg=GOLD_DIM, height=1).pack(fill='x')
        tk.Label(right, text='LINEUPLAR', bg=BG_CARD, fg=GOLD,
                 font=('Consolas', 9, 'bold')).pack(anchor='w', padx=10, pady=(6, 2))
        self.ov_lb = self._lb(right, h=10, w=46)
        self.ov_lb.pack(fill='x', padx=8, pady=4)
        self.ov_lb.bind('<<ListboxSelect>>', lambda e: self._ov_select(mk))

        tk.Frame(right, bg=GOLD_DIM, height=1).pack(fill='x', pady=4)
        tk.Label(right, text='NASIL KULLANILIR?', bg=BG_CARD, fg=GOLD,
                 font=('Consolas', 9, 'bold')).pack(anchor='w', padx=10)
        self.ov_detail = self._txt(right, h=16, wrap=tk.WORD)
        self.ov_detail.pack(fill='both', expand=True, padx=8, pady=4)
        self.ov_detail.config(state='disabled')

        self._ov_load_map(mk)
        self._ov_populate(mk, 'Hepsi')

    def _map_key(self):
        mn = self.live.get('map', '—')
        if mn and mn != '—':
            return mn.lower() if mn.startswith('de_') else 'de_' + mn.lower()
        if self.current_map:
            cm = self.current_map.lower()
            return cm if cm.startswith('de_') else 'de_' + cm
        return None

    def _ov_load_map(self, mk):
        if not PIL_OK:
            return
        candidates = []
        if mk:
            candidates += [mk, mk.replace('de_', '')]
        if self.current_map:
            candidates.append(self.current_map)

        img_path = None
        for c in candidates:
            for ext in ['.gif', '.png', '.jpg']:
                p = os.path.join(self.maps_dir, f'{c}{ext}')
                if os.path.exists(p):
                    img_path = p
                    break
            if img_path:
                break

        self.ov_canvas.update_idletasks()
        cw = self.ov_canvas.winfo_width()  or 540
        ch = self.ov_canvas.winfo_height() or 580
        if img_path:
            try:
                img   = Image.open(img_path)
                ratio = img.width / img.height
                if ratio > cw / ch:
                    nw, nh = cw, int(cw / ratio)
                else:
                    nw, nh = int(ch * ratio), ch
                img = img.resize((nw, nh), Image.Resampling.LANCZOS)
                self.overlay_map_photo = ImageTk.PhotoImage(img)
                self.ov_canvas.create_image(cw // 2, ch // 2,
                                            image=self.overlay_map_photo, anchor='center')
                self._ov_cw, self._ov_ch = cw, ch
                self._ov_iw, self._ov_ih = nw, nh
                self._ov_ox = (cw - nw) // 2
                self._ov_oy = (ch - nh) // 2
            except Exception as e:
                self._ov_no_map(cw, ch)
        else:
            self._ov_no_map(cw, ch)

    def _ov_no_map(self, cw, ch):
        self.ov_canvas.create_text(cw // 2, ch // 2,
                                    text='Harita GIF/PNG yok\n"maps/" klasörüne ekle',
                                    fill=TEXT_MUTED, font=('Consolas', 13), justify='center')
        self._ov_cw = cw; self._ov_ch = ch
        self._ov_iw = cw; self._ov_ih = ch
        self._ov_ox = 0;  self._ov_oy = 0

    def _ov_populate(self, mk, ft):
        self.ov_lb.delete(0, tk.END)
        lineups = LINEUP_DB.get(mk, [])
        if ft != 'Hepsi':
            lineups = [l for l in lineups if l['type'] == ft]
        self._ov_filtered = lineups
        icons = {'Smoke': '💨', 'Flash': '⚡', 'Molotov': '🔥', 'HE': '💣'}
        for l in lineups:
            self.ov_lb.insert(tk.END, f"  {icons.get(l['type'], '◎')}  {l['name']}  ({l['from_pos']})")
        if lineups:
            self.ov_lb.selection_set(0)
            self._ov_select(mk)

    def _ov_filter(self, ft, mk):
        self.ov_filter_var.set(ft)
        self._ov_populate(mk, ft)

    def _ov_select(self, mk):
        sel = self.ov_lb.curselection()
        if not sel:
            return
        lu = self._ov_filtered[sel[0]]
        self._ov_draw_markers(mk, lu)
        self._ov_show_steps(lu)

    def _ov_draw_markers(self, mk, sel_lu):
        self.ov_canvas.delete('lm')
        ft = self.ov_filter_var.get() if self.ov_filter_var else 'Hepsi'
        lineups = LINEUP_DB.get(mk, [])
        if ft != 'Hepsi':
            lineups = [l for l in lineups if l['type'] == ft]
        for lu in lineups:
            px     = int(self._ov_ox + lu['x_pct'] * self._ov_iw)
            py     = int(self._ov_oy + lu['y_pct'] * self._ov_ih)
            is_sel = lu['name'] == sel_lu['name']
            col    = TYPE_CLR.get(lu['type'], GOLD)
            r      = 14 if is_sel else 8
            bw     = 3 if is_sel else 1
            self.ov_canvas.create_oval(px - r, py - r, px + r, py + r,
                                        fill=col, outline=GOLD_BRIGHT if is_sel else '#444',
                                        width=bw, tags='lm')
            if is_sel:
                lbl = lu['name']
                self.ov_canvas.create_rectangle(px - 4, py - r - 26,
                                                 px + len(lbl) * 7 + 4, py - r - 4,
                                                 fill='#0a0a0a', outline=GOLD_DIM, tags='lm')
                self.ov_canvas.create_text(px, py - r - 14, text=lbl, fill=GOLD_BRIGHT,
                                            font=('Consolas', 9, 'bold'), anchor='w', tags='lm')
                self.ov_canvas.create_text(px, py + r + 10, text=lu['type'].upper(),
                                            fill=col, font=('Consolas', 8, 'bold'), tags='lm')
            else:
                self.ov_canvas.create_text(px, py, text=lu['type'][0],
                                            fill='#000', font=('Consolas', 8, 'bold'), tags='lm')

    def _ov_show_steps(self, lu):
        self.ov_detail.config(state='normal')
        self.ov_detail.delete('1.0', tk.END)
        icons = {'Smoke': '💨', 'Flash': '⚡', 'Molotov': '🔥', 'HE': '💣'}
        t  = f"{icons.get(lu['type'], '◎')}  {lu['name']}\n{'─'*36}\n"
        t += f"Tip: {lu['type']}\nBaşlangıç: {lu['from_pos']}\n{'─'*36}\n\n📋 ADIMLAR:\n\n"
        for i, s in enumerate(lu['steps'], 1):
            t += f"  {i}.  {s}\n\n"
        t += f"{'─'*36}\n⌨  Başka lineup → listeden seç\n🚪  Kapat → F9 veya ESC"
        self.ov_detail.insert('1.0', t)
        self.ov_detail.config(state='disabled')

    # ═══════════════════════════════════════════════════════════
    #  HARİTA FONKSİYONLARI
    # ═══════════════════════════════════════════════════════════
    def get_available_maps(self):
        if not os.path.exists(self.maps_dir):
            return []
        maps = []
        for f in os.listdir(self.maps_dir):
            if f.endswith(('.gif', '.png', '.jpg')):
                maps.append(os.path.splitext(f)[0])
        return maps if maps else ['Harita yok']

    def on_map_select(self, _=None):
        sel = self.map_listbox.curselection()
        if sel:
            self.load_map(self.map_listbox.get(sel[0]))

    def load_map(self, mn):
        if not PIL_OK:
            messagebox.showerror('Hata', 'Pillow kurulu değil! pip install Pillow')
            return
        img_path = None
        for ext in ['.gif', '.png', '.jpg']:
            p = os.path.join(self.maps_dir, f'{mn}{ext}')
            if os.path.exists(p):
                img_path = p
                break
        if not img_path:
            return
        try:
            self.current_map       = mn
            self.current_map_image = Image.open(img_path)
            cw    = self.map_canvas.winfo_width()  or 900
            ch    = self.map_canvas.winfo_height() or 700
            ratio = self.current_map_image.width / self.current_map_image.height
            if ratio > cw / ch:
                nw, nh = cw, int(cw / ratio)
            else:
                nw, nh = int(ch * ratio), ch
            img = self.current_map_image.resize((nw, nh), Image.Resampling.LANCZOS)
            self.map_photo = ImageTk.PhotoImage(img)
            self.map_canvas.delete('all')
            self.map_canvas.create_image(cw // 2, ch // 2, image=self.map_photo, anchor='center')
            self.load_spots_for_map()
        except Exception as e:
            messagebox.showerror('Hata', f'Harita yüklenemedi: {e}')

    def load_map_gif(self):
        p = filedialog.askopenfilename(
            title='Harita resmi seçin',
            filetypes=[('Resim', '*.gif *.png *.jpg'), ('GIF', '*.gif'),
                       ('PNG', '*.png'), ('JPEG', '*.jpg')])
        if not p:
            return
        import shutil
        fn = os.path.basename(p)
        shutil.copy(p, os.path.join(self.maps_dir, fn))
        self.map_listbox.delete(0, tk.END)
        for m in self.get_available_maps():
            self.map_listbox.insert(tk.END, m)
        messagebox.showinfo('Başarılı', f'Harita eklendi: {fn}')

    def enable_spot_marking(self):
        if not self.current_map:
            messagebox.showwarning('Uyarı', 'Harita seçin!')
            return
        if not self.spot_name_entry.get().strip():
            messagebox.showwarning('Uyarı', 'Ad girin!')
            return
        messagebox.showinfo('Spot', 'Haritaya tıklayın!')
        self.spot_marking_enabled = True

    def on_canvas_click(self, event):
        if not self.spot_marking_enabled:
            return
        name  = self.spot_name_entry.get().strip()
        stype = self.spot_type_var.get()
        if not name:
            return
        self.spots_data.setdefault(self.current_map, [])
        self.spots_data[self.current_map].append({'name': name, 'type': stype,
                                                   'x': event.x, 'y': event.y})
        self.save_data()
        self.draw_spot(event.x, event.y, stype, name)
        self.spots_listbox.insert(tk.END, f'{name} ({stype})')
        self.spot_name_entry.delete(0, tk.END)
        self.spot_marking_enabled = False
        messagebox.showinfo('Başarılı', f'Spot eklendi: {name}')

    def draw_spot(self, x, y, stype, name):
        colors = {'Common': '#00ff00', 'Sniper': '#ff4444', 'Smoke': '#aaaaaa',
                  'Flash': '#ffff00', 'Molotov': '#ff8800', 'Plant': '#00aaff', 'Danger': '#ff00aa'}
        col = colors.get(stype, GOLD)
        r   = 9
        o   = self.map_canvas.create_oval(x - r, y - r, x + r, y + r,
                                           fill=col, outline=GOLD_BRIGHT, width=2)
        t   = self.map_canvas.create_text(x, y - 18, text=name,
                                           fill=GOLD_BRIGHT, font=('Consolas', 9, 'bold'))
        self.spot_markers.append((o, t))

    def load_spots_for_map(self):
        for o, t in self.spot_markers:
            self.map_canvas.delete(o)
            self.map_canvas.delete(t)
        self.spot_markers.clear()
        self.spots_listbox.delete(0, tk.END)
        for s in self.spots_data.get(self.current_map, []):
            self.draw_spot(s['x'], s['y'], s['type'], s['name'])
            self.spots_listbox.insert(tk.END, f"{s['name']} ({s['type']})")

    def delete_spot(self):
        sel = self.spots_listbox.curselection()
        if not sel:
            messagebox.showwarning('Uyarı', 'Spot seçin!')
            return
        if self.current_map in self.spots_data:
            del self.spots_data[self.current_map][sel[0]]
        self.save_data()
        self.load_spots_for_map()

    # ═══════════════════════════════════════════════════════════
    #  VERİ YÖNETİMİ
    # ═══════════════════════════════════════════════════════════
    def load_data(self):
        for attr, path, default in [
            ('spots_data',   self.spots_file,   {}),
            ('configs_data', self.configs_file, {}),
            ('stats_data',   self.stats_file,   {'total_hours': 0, 'aim_sessions': []}),
            ('matches_data', self.matches_file, {'matches': []}),
        ]:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    setattr(self, attr, json.load(f))
            else:
                setattr(self, attr, default)

    def save_data(self):
        for attr, path in [('spots_data', self.spots_file),
                            ('configs_data', self.configs_file),
                            ('stats_data', self.stats_file)]:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(getattr(self, attr), f, indent=4, ensure_ascii=False)

    def _save_matches(self):
        with open(self.matches_file, 'w', encoding='utf-8') as f:
            json.dump(self.matches_data, f, indent=4, ensure_ascii=False)

    def load_settings(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                self.settings = json.load(f)
        else:
            self.settings = {'log_path': '', 'gsi_installed': False, 'gsi_cfg_path': ''}
        # Ensure backward-compatible keys
        self.settings.setdefault('update_sources', [self.UPDATE_URL])
        self.settings.setdefault('auto_update', False)
        self.settings.setdefault('update_interval', 3600)
        self.settings.setdefault('version', self.settings.get('version', '1.0'))
        self.settings.setdefault('sound_hit_feedback', True)
        self.settings.setdefault('auto_save_matches', True)
        self.settings.setdefault('accent_color', GOLD)
        self.settings.setdefault('always_on_top', False)
        # Add recommended sources if not present
        recommended = [
            'https://counter-strike.net/news/updates',
            'https://prosettings.net/games/cs2',
            'https://www.hltv.org/',
            'https://leetify.com',
            'https://scope.gg',
            'https://cs2nades.com'
        ]
        for r in recommended:
            if r not in self.settings['update_sources']:
                self.settings['update_sources'].append(r)

    def save_settings(self):
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, indent=4, ensure_ascii=False)

    # ═══════════════════════════════════════════════════════════
    #  OTOMATİK GÜNCELLEME
    # ═══════════════════════════════════════════════════════════
    UPDATE_URL = "https://raw.githubusercontent.com/yourusername/cs2pro-assistant/main/data/latest.json"  # değiştirin

    def _check_for_updates(self):
        """Uzaktaki JSON'dan güncel verileri çeker ve uygulamaya yükler."""
        # Manuel tetikleme: mevcut update kaynaklarından veriyi al
        threading.Thread(target=self._fetch_updates_once, daemon=True).start()

    def _fetch_json_from_url(self, url, timeout=8):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            return {'__error': str(e)}

    def _fetch_text_from_url(self, url, timeout=8):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=timeout) as response:
                data = response.read()
                try:
                    text = data.decode('utf-8')
                except Exception:
                    text = data.decode('latin-1', errors='ignore')
                return text
        except Exception as e:
            return {'__error': str(e)}

    def _parse_html_summary(self, url, html):
        # Very small parser: extract <title>, meta description, first <p>
        def rex(pattern, txt, flags=0):
            m = re.search(pattern, txt, flags)
            return m.group(1).strip() if m else None
        title = rex(r'<title\s*>\s*(.*?)\s*</title>', html, re.I | re.S)
        desc = rex(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', html, re.I | re.S) or \
               rex(r'<meta\s+property=["\']og:description["\']\s+content=["\'](.*?)["\']', html, re.I | re.S)
        p1 = rex(r'<p\s*[^>]*>(.*?)</p>', html, re.I | re.S)
        snippet = desc or (p1 and re.sub('<[^>]+>', '', p1)) or ''
        parsed = urlparse(url)
        domain = parsed.netloc.lower() if parsed.netloc else url
        # Infer a simple source type
        if 'counter-strike.net' in domain:
            src_type = 'official_update'
        elif 'prosettings.net' in domain or 'leetify' in domain or 'scope.gg' in domain:
            src_type = 'pro_config_meta'
        elif 'cs2nades' in domain or 'nades' in domain:
            src_type = 'nade_lineups'
        elif 'hltv' in domain:
            src_type = 'hltv_news'
        else:
            src_type = 'external'
        return {
            'source': url,
            'domain': domain,
            'source_type': src_type,
            'title': title or url,
            'snippet': re.sub(r'\s+', ' ', re.sub('<[^>]+>', '', snippet)).strip(),
            'fetched_at': datetime.utcnow().isoformat()
        }

    def _apply_external_update(self, data):
        # Save parsed external summary into stats_data
        self.stats_data.setdefault('external_updates', [])
        self.stats_data['external_updates'].append(data)
        try:
            self.save_data()
        except Exception:
            pass

    def _fetch_updates_once(self):
        sources = self.settings.get('update_sources', [self.UPDATE_URL])
        any_applied = False
        for src in sources:
            data = self._fetch_json_from_url(src)
            if data is None:
                continue
            if isinstance(data, dict) and data.get('__error'):
                # try HTML fallback
                txt = self._fetch_text_from_url(src)
                if isinstance(txt, dict) and txt.get('__error'):
                    # log hata
                    self.root.after(0, lambda e=txt.get('__error'): self._set_status(f'Güncelleme hata: {e}', RED_ALERT))
                    continue
                # parse HTML for summary
                summary = self._parse_html_summary(src, txt)
                self.root.after(0, self._apply_external_update, summary)
                any_applied = True
                continue
            try:
                # Apply update if it contains known keys
                if any(k in data for k in ('pro_configs', 'weapon_data', 'lineup_db', 'strategies', 'callouts')):
                    self.root.after(0, self._apply_update, data)
                    any_applied = True
                else:
                    # If JSON but doesn't contain known keys, store raw
                    self.root.after(0, self._apply_external_update, {'source': src, 'title': src, 'snippet': str(data), 'fetched_at': datetime.utcnow().isoformat()})
            except Exception as e:
                self.root.after(0, lambda: self._set_status(f'Güncelleme uygulama hatası', RED_ALERT))
        if not any_applied:
            self.root.after(0, lambda: messagebox.showinfo('Güncelleme', 'Uzak kaynaklarda yeni veri bulunamadı.'))

    def _apply_update(self, data):
        """Gelen verileri ilgili veritabanlarına uygula."""
        if 'pro_configs' in data:
            global PRO_CONFIGS
            PRO_CONFIGS.update(data['pro_configs'])
        if 'weapon_data' in data:
            global WEAPON_DATA
            WEAPON_DATA.update(data['weapon_data'])
        if 'lineup_db' in data:
            global LINEUP_DB
            LINEUP_DB.update(data['lineup_db'])
        if 'strategies' in data:
            global STRATEGIES
            STRATEGIES.update(data['strategies'])
        if 'callouts' in data:
            global CALLOUTS
            CALLOUTS.update(data['callouts'])
        self.settings['version'] = data.get('version', '1.0')
        self.save_settings()
        messagebox.showinfo('Başarılı', 'Yeni veriler yüklendi! Uygulamayı yeniden başlatın.')

    # Otomatik güncelleme işçisi
    def _start_auto_update_worker(self):
        if self._update_thread and self._update_thread.is_alive():
            return
        self._update_stop.clear()

        def _worker():
            interval = max(60, int(self.settings.get('update_interval', 3600)))
            while not self._update_stop.is_set():
                if self.settings.get('auto_update', False):
                    try:
                        self._fetch_updates_once()
                    except Exception:
                        pass
                # bekle
                for _ in range(int(interval)):
                    if self._update_stop.is_set():
                        break
                    time.sleep(1)

        self._update_thread = threading.Thread(target=_worker, daemon=True)
        self._update_thread.start()

    def _stop_auto_update_worker(self):
        if self._update_thread and self._update_thread.is_alive():
            self._update_stop.set()
            self._update_thread.join(timeout=2)

# ═══════════════════════════════════════════════════════════════
#  SPLASH SCREEN
# ═══════════════════════════════════════════════════════════════
def show_splash(root):
    splash = tk.Toplevel(root)
    splash.overrideredirect(True)
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    w, h   = 540, 340
    splash.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
    splash.configure(bg='#06060a')
    splash.attributes('-topmost', True)

    # Dekoratif border
    for i, clr in enumerate([GOLD, GOLD_DIM, BG_CARD]):
        tk.Frame(splash, bg=clr, height=2 if i == 0 else 1).pack(fill='x')

    tk.Label(splash, text='◈', bg='#06060a', fg=GOLD_BRIGHT,
             font=('Consolas', 52, 'bold')).pack(pady=(28, 4))
    tk.Label(splash, text='CS2 PRO ASSISTANT', bg='#06060a', fg=GOLD_BRIGHT,
             font=('Consolas', 22, 'bold')).pack()
    tk.Label(splash, text='v5.1  PROFESSIONAL LIVE EDITION', bg='#06060a', fg=GOLD,
             font=('Consolas', 10)).pack()
    tk.Frame(splash, bg=GOLD_DIM, height=1).pack(fill='x', padx=40, pady=14)
    tk.Label(splash, text='Geliştirici  /  Developer', bg='#06060a', fg=TEXT_MUTED,
             font=('Segoe UI', 9)).pack()
    tk.Label(splash, text='Burak  ( r001B )  Aydogdu', bg='#06060a', fg=GOLD_BRIGHT,
             font=('Consolas', 14, 'bold')).pack(pady=6)
    tk.Frame(splash, bg=GOLD_DIM, height=1).pack(fill='x', padx=40, pady=8)

    features = '✅ Otomatik Maç Analizi  ✅ Canlı KDA  ✅ Bomb Timer  ✅ 2026 Güncel'
    tk.Label(splash, text=features, bg='#06060a', fg=TEXT_MUTED,
             font=('Segoe UI', 8)).pack()

    for i, clr in enumerate([BG_CARD, GOLD_DIM, GOLD]):
        tk.Frame(splash, bg=clr, height=1 if i < 2 else 2).pack(fill='x', side='bottom')

    splash.after(3000, splash.destroy)

# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════
def main():
    root = tk.Tk()
    root.withdraw()
    show_splash(root)
    root.after(3100, root.deiconify)
    app = CS2Assistant(root)
    root.mainloop()

if __name__ == '__main__':
    main()