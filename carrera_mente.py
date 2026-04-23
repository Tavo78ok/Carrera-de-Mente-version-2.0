#!/usr/bin/env python3
"""
Carrera de Mente - ArgOS Platinum Edition
Juego de trivia para 1-4 jugadores
App ID: io.openargos.CarreraDeMente
Version: 1.0.0
"""
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib, Gdk, Pango

import threading
import json
import random
import sys
import os

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

APP_ID  = "io.openargos.CarreraDeMente"
VERSION = "1.0.0"

# ─── DATOS DE CATEGORÍAS ──────────────────────────────────────────────────────
CATEGORIES = [
    {"name": "Cultura General",      "emoji": "🧠", "cc": "cat-blue"},
    {"name": "Entretenimiento",      "emoji": "🎬", "cc": "cat-purple"},
    {"name": "Ciencia y Tecnología", "emoji": "🔬", "cc": "cat-green"},
    {"name": "Historia",             "emoji": "📜", "cc": "cat-orange"},
    {"name": "Geografía",            "emoji": "🌍", "cc": "cat-teal"},
    {"name": "Deportes",             "emoji": "⚽",  "cc": "cat-red"},
]

# ─── BANCO DE PREGUNTAS (8 por categoría) ─────────────────────────────────────
BANK = {
    "Cultura General": [
        {"q": "¿Cuál es el idioma más hablado del mundo como lengua materna?",
         "o": ["Inglés","Español","Mandarín","Hindi"], "a": 2},
        {"q": "¿Cuántos continentes tiene la Tierra?",
         "o": ["5","6","7","4"], "a": 2},
        {"q": "¿Cuál es el animal más grande del mundo?",
         "o": ["Elefante africano","Ballena azul","Tiburón ballena","Jirafa"], "a": 1},
        {"q": "¿Cuántos lados tiene un hexágono?",
         "o": ["5","6","7","8"], "a": 1},
        {"q": "¿Cuál es el planeta más grande del sistema solar?",
         "o": ["Saturno","Neptuno","Júpiter","Urano"], "a": 2},
        {"q": "¿Qué instrumento mide la temperatura?",
         "o": ["Barómetro","Termómetro","Higrómetro","Anemómetro"], "a": 1},
        {"q": "¿Cuál es el metal más abundante en la corteza terrestre?",
         "o": ["Hierro","Oro","Aluminio","Cobre"], "a": 2},
        {"q": "¿Cuántos días tiene un año bisiesto?",
         "o": ["364","365","366","367"], "a": 2},
    ],
    "Entretenimiento": [
        {"q": "¿En qué país se originó el K-pop?",
         "o": ["Japón","China","Corea del Sur","Tailandia"], "a": 2},
        {"q": "¿Quién interpretó a Iron Man en el MCU?",
         "o": ["Chris Evans","Robert Downey Jr.","Chris Hemsworth","Mark Ruffalo"], "a": 1},
        {"q": "¿En qué año se estrenó la primera película de Harry Potter?",
         "o": ["1999","2000","2001","2002"], "a": 2},
        {"q": "¿Cuál es el nombre del mayordomo de Batman?",
         "o": ["James","Alfred","Thomas","Edwin"], "a": 1},
        {"q": "¿Quién cantó 'Thriller'?",
         "o": ["Prince","Michael Jackson","Stevie Wonder","James Brown"], "a": 1},
        {"q": "¿Cuántas temporadas tiene Breaking Bad?",
         "o": ["4","5","6","7"], "a": 1},
        {"q": "¿Qué estudio animó 'El Rey León' (1994)?",
         "o": ["Pixar","DreamWorks","Walt Disney","Universal"], "a": 2},
        {"q": "¿De qué ciudad es el grupo musical 'Los Beatles'?",
         "o": ["Londres","Manchester","Liverpool","Birmingham"], "a": 2},
    ],
    "Ciencia y Tecnología": [
        {"q": "¿Cuál es la fórmula química del agua?",
         "o": ["CO2","H2O","O2","NaCl"], "a": 1},
        {"q": "¿Quién inventó el teléfono?",
         "o": ["Thomas Edison","Nikola Tesla","Alexander Graham Bell","Marconi"], "a": 2},
        {"q": "¿Cuántos huesos tiene el cuerpo humano adulto?",
         "o": ["186","196","206","216"], "a": 2},
        {"q": "¿Cuál es el elemento más ligero de la tabla periódica?",
         "o": ["Helio","Litio","Hidrógeno","Boro"], "a": 2},
        {"q": "¿Qué significa CPU?",
         "o": ["Central Processing Unit","Computer Personal Unit","Core Program Unit","Central Program Utility"], "a": 0},
        {"q": "¿En qué año se lanzó el primer iPhone?",
         "o": ["2005","2006","2007","2008"], "a": 2},
        {"q": "¿Cuál es la velocidad de la luz en el vacío?",
         "o": ["300.000 km/s","150.000 km/s","450.000 km/s","200.000 km/s"], "a": 0},
        {"q": "¿Qué planeta es conocido como el planeta rojo?",
         "o": ["Venus","Júpiter","Marte","Saturno"], "a": 2},
    ],
    "Historia": [
        {"q": "¿En qué año comenzó la Segunda Guerra Mundial?",
         "o": ["1937","1938","1939","1940"], "a": 2},
        {"q": "¿Quién fue el primer presidente de los Estados Unidos?",
         "o": ["Abraham Lincoln","Thomas Jefferson","Benjamin Franklin","George Washington"], "a": 3},
        {"q": "¿En qué año llegó Cristóbal Colón a América?",
         "o": ["1490","1491","1492","1493"], "a": 2},
        {"q": "¿Qué civilización construyó el Machu Picchu?",
         "o": ["Azteca","Maya","Inca","Olmeca"], "a": 2},
        {"q": "¿En qué año cayó el Muro de Berlín?",
         "o": ["1987","1988","1989","1990"], "a": 2},
        {"q": "¿Quién fue la reina que financió el viaje de Colón?",
         "o": ["Reina María","Reina Isabel I","Reina Juana","Reina Catalina"], "a": 1},
        {"q": "¿En qué año se firmó la Declaración de Independencia de EE.UU.?",
         "o": ["1774","1775","1776","1777"], "a": 2},
        {"q": "¿Cuánto duró la Primera Guerra Mundial?",
         "o": ["3 años","4 años","5 años","6 años"], "a": 1},
    ],
    "Geografía": [
        {"q": "¿Cuál es el río más largo del mundo?",
         "o": ["Amazonas","Nilo","Yangtsé","Misisipi"], "a": 1},
        {"q": "¿Cuál es el país más grande del mundo?",
         "o": ["China","Canadá","Estados Unidos","Rusia"], "a": 3},
        {"q": "¿Cuál es la capital de Australia?",
         "o": ["Sídney","Melbourne","Canberra","Brisbane"], "a": 2},
        {"q": "¿Cuál es el desierto más grande del mundo?",
         "o": ["Sahara","Gobi","Antártida","Kalahari"], "a": 2},
        {"q": "¿En qué continente está Egipto?",
         "o": ["Asia","Europa","África","Oceanía"], "a": 2},
        {"q": "¿Cuál es el océano más grande del mundo?",
         "o": ["Atlántico","Índico","Ártico","Pacífico"], "a": 3},
        {"q": "¿Cuál es la montaña más alta del mundo?",
         "o": ["K2","Monte Everest","Aconcagua","Mont Blanc"], "a": 1},
        {"q": "¿Cuál es la capital de Brasil?",
         "o": ["São Paulo","Río de Janeiro","Brasilia","Salvador"], "a": 2},
    ],
    "Deportes": [
        {"q": "¿Cuántos jugadores tiene un equipo de fútbol en la cancha?",
         "o": ["9","10","11","12"], "a": 2},
        {"q": "¿Cuántos anillos tiene el símbolo olímpico?",
         "o": ["4","5","6","7"], "a": 1},
        {"q": "¿En qué deporte se usa un 'birdie'?",
         "o": ["Tenis","Golf","Bádminton","Cricket"], "a": 1},
        {"q": "¿Cuántos puntos vale un triple en baloncesto?",
         "o": ["1","2","3","4"], "a": 2},
        {"q": "¿Cuál es el torneo de tenis más antiguo del mundo?",
         "o": ["Roland Garros","US Open","Wimbledon","Australian Open"], "a": 2},
        {"q": "¿Cuántos jugadores hay en un equipo de baloncesto en cancha?",
         "o": ["4","5","6","7"], "a": 1},
        {"q": "¿En qué año se celebraron los primeros Juegos Olímpicos modernos?",
         "o": ["1894","1896","1898","1900"], "a": 1},
        {"q": "¿Cuántos sets necesita ganar en Grand Slam masculino?",
         "o": ["2 de 3","3 de 5","2 de 5","3 de 4"], "a": 1},
    ],
}

# ─── CSS ──────────────────────────────────────────────────────────────────────
CSS = """
.cat-blue   { background-color: #3584e4; border-radius: 12px; }
.cat-purple { background-color: #9141ac; border-radius: 12px; }
.cat-green  { background-color: #2ec27e; border-radius: 12px; }
.cat-orange { background-color: #e66100; border-radius: 12px; }
.cat-teal   { background-color: #0077c2; border-radius: 12px; }
.cat-red    { background-color: #e01b24; border-radius: 12px; }

.cat-blue label, .cat-purple label, .cat-green label,
.cat-orange label, .cat-teal label, .cat-red label { color: white; }

.category-card {
    padding: 10px 6px;
    min-height: 68px;
    min-width: 130px;
}

.cat-name-lbl {
    font-size: 12px;
    font-weight: bold;
}

.answer-btn {
    border-radius: 10px;
    padding: 10px 14px;
    min-height: 48px;
}

.answer-correct { background-color: #2ec27e; color: white; }
.answer-wrong   { background-color: #e01b24; color: white; }

.token-on  { font-size: 13px; }
.token-off { font-size: 13px; opacity: 0.25; }

.player-active-card { border: 2px solid @accent_color; border-radius: 12px; }
.player-idle-card   { border: 2px solid transparent;   border-radius: 12px; }
"""


# ─── APLICACIÓN ───────────────────────────────────────────────────────────────
class CarreraApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id=APP_ID)
        self.connect("activate", self._on_activate)

    def _on_activate(self, _):
        win = MainWindow(application=self)
        win.present()


# ─── VENTANA PRINCIPAL ────────────────────────────────────────────────────────
class MainWindow(Adw.ApplicationWindow):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.set_title("Carrera de Mente")
        self.set_default_size(820, 640)
        self.set_size_request(680, 560)

        # Inyectar CSS
        provider = Gtk.CssProvider()
        provider.load_from_string(CSS)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(), provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # Estado del juego
        self.num_players    = 2
        self.player_names   = []
        self.current_player = 0
        self.scores         = []   # scores[jugador][cat_idx] = bool
        self.used_qs        = {}   # cat_name -> set de índices usados
        self.current_cat    = 0
        self.current_q      = None
        self.answered       = False

        # Toast overlay + stack principal
        self.toast_overlay = Adw.ToastOverlay()
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.toast_overlay.set_child(self.stack)
        self.set_content(self.toast_overlay)

        self._build_welcome()
        self._build_setup()
        self._build_game()
        self._build_question()
        self._build_winner()

        self.stack.set_visible_child_name("welcome")

    # ── PANTALLA: BIENVENIDA ──────────────────────────────────────────────────
    def _build_welcome(self):
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        hb = Adw.HeaderBar()
        hb.add_css_class("flat")
        outer.append(hb)

        scroll = Gtk.ScrolledWindow(vexpand=True)
        outer.append(scroll)

        clamp = Adw.Clamp(valign=Gtk.Align.CENTER, vexpand=True)
        scroll.set_child(clamp)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20,
                      valign=Gtk.Align.CENTER, halign=Gtk.Align.CENTER,
                      margin_top=60, margin_bottom=60,
                      margin_start=24, margin_end=24)

        brain = Gtk.Label()
        brain.set_text("🧠")
        brain.add_css_class("title-1")
        box.append(brain)

        title = Gtk.Label(label="Carrera de Mente")
        title.add_css_class("title-1")
        box.append(title)

        sub = Gtk.Label(label="El clásico juego de trivia para toda la familia")
        sub.add_css_class("dim-label")
        box.append(sub)

        # Badges de categorías
        cats_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6,
                           halign=Gtk.Align.CENTER, margin_top=8)
        for cat in CATEGORIES:
            badge_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
            badge_box.add_css_class(cat["cc"])
            badge_box.set_margin_start(2)
            badge_box.set_margin_end(2)
            inner = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4,
                            margin_start=8, margin_end=8,
                            margin_top=4, margin_bottom=4)
            lbl = Gtk.Label()
            lbl.set_text(cat["emoji"])
            inner.append(lbl)
            badge_box.append(inner)
            cats_box.append(badge_box)
        box.append(cats_box)

        btn = Gtk.Button(label="Comenzar juego", margin_top=12)
        btn.add_css_class("suggested-action")
        btn.add_css_class("pill")
        btn.connect("clicked", lambda _: self.stack.set_visible_child_name("setup"))
        box.append(btn)

        if not HAS_ANTHROPIC:
            note = Gtk.Label(label="Instala 'anthropic' para preguntas generadas por IA")
            note.add_css_class("caption")
            note.add_css_class("dim-label")
            box.append(note)

        clamp.set_child(box)
        self.stack.add_named(outer, "welcome")

    # ── PANTALLA: CONFIGURACIÓN ───────────────────────────────────────────────
    def _build_setup(self):
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        hb = Adw.HeaderBar()
        hb.set_title_widget(Adw.WindowTitle(title="Nueva partida"))
        back = Gtk.Button(label="Volver")
        back.add_css_class("flat")
        back.connect("clicked", lambda _: self.stack.set_visible_child_name("welcome"))
        hb.pack_start(back)
        outer.append(hb)

        scroll = Gtk.ScrolledWindow(vexpand=True)
        outer.append(scroll)

        clamp = Adw.Clamp(maximum_size=480, margin_top=20, margin_bottom=24)
        scroll.set_child(clamp)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16,
                      margin_start=16, margin_end=16)
        clamp.set_child(box)

        # Número de jugadores
        num_grp = Adw.PreferencesGroup(title="Jugadores")
        box.append(num_grp)

        num_row = Adw.ActionRow(title="Número de jugadores")
        self.num_spin = Gtk.SpinButton(valign=Gtk.Align.CENTER)
        self.num_spin.set_adjustment(
            Gtk.Adjustment(value=2, lower=1, upper=4, step_increment=1))
        self.num_spin.connect("value-changed", self._on_num_changed)
        num_row.add_suffix(self.num_spin)
        num_grp.add(num_row)

        # Nombres
        self.names_grp = Adw.PreferencesGroup(title="Nombres")
        box.append(self.names_grp)

        self.name_rows = []
        self._rebuild_names(2)

        # Botón jugar
        play_btn = Gtk.Button(label="¡Jugar!", margin_top=8)
        play_btn.add_css_class("suggested-action")
        play_btn.add_css_class("pill")
        play_btn.connect("clicked", self._on_start)
        box.append(play_btn)

        self.stack.add_named(outer, "setup")

    def _on_num_changed(self, spin):
        self._rebuild_names(int(spin.get_value()))

    def _rebuild_names(self, n):
        for row in self.name_rows:
            self.names_grp.remove(row)
        self.name_rows = []
        for i in range(n):
            row = Adw.EntryRow(title=f"Jugador {i + 1}")
            row.set_text(f"Jugador {i + 1}")
            self.names_grp.add(row)
            self.name_rows.append(row)

    def _on_start(self, _):
        self.num_players  = int(self.num_spin.get_value())
        self.player_names = [r.get_text() or f"Jugador {i+1}"
                             for i, r in enumerate(self.name_rows)]
        self._init_state()
        self._refresh_game()
        self.stack.set_visible_child_name("game")

    # ── PANTALLA: JUEGO ───────────────────────────────────────────────────────
    def _build_game(self):
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        hb = Adw.HeaderBar()
        self._game_title_widget = Adw.WindowTitle(title="Carrera de Mente")
        hb.set_title_widget(self._game_title_widget)
        new_btn = Gtk.Button(icon_name="view-refresh-symbolic",
                             tooltip_text="Nueva partida")
        new_btn.add_css_class("flat")
        new_btn.connect("clicked", lambda _: self.stack.set_visible_child_name("setup"))
        hb.pack_end(new_btn)
        outer.append(hb)

        scroll = Gtk.ScrolledWindow(vexpand=True)
        outer.append(scroll)

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12,
                       margin_top=12, margin_bottom=16,
                       margin_start=16, margin_end=16)
        scroll.set_child(root)

        # Tarjetas de jugadores
        self.players_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,
                                   spacing=8, homogeneous=True)
        root.append(self.players_row)

        # Etiqueta de turno
        self.turn_lbl = Gtk.Label(margin_top=4)
        self.turn_lbl.add_css_class("heading")
        root.append(self.turn_lbl)

        # Grid de categorías
        choose_lbl = Gtk.Label(label="Elige una categoría:", xalign=0)
        choose_lbl.add_css_class("body")
        root.append(choose_lbl)

        self.cat_grid = Gtk.Grid(row_spacing=8, column_spacing=8,
                                 column_homogeneous=True)
        root.append(self.cat_grid)

        self.cat_btns = []
        for i, cat in enumerate(CATEGORIES):
            btn = Gtk.Button()
            btn.add_css_class("flat")
            btn.set_tooltip_text(cat["name"])

            card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4,
                           halign=Gtk.Align.FILL, valign=Gtk.Align.FILL)
            card.add_css_class("category-card")
            card.add_css_class(cat["cc"])

            emoji_lbl = Gtk.Label()
            emoji_lbl.set_text(cat["emoji"])
            emoji_lbl.add_css_class("title-3")
            card.append(emoji_lbl)

            name_lbl = Gtk.Label()
            name_lbl.set_text(cat["name"])
            name_lbl.set_wrap(True)
            name_lbl.set_justify(Gtk.Justification.CENTER)
            name_lbl.add_css_class("cat-name-lbl")
            card.append(name_lbl)

            btn.set_child(card)
            btn.connect("clicked", self._on_cat_clicked, i)
            self.cat_btns.append(btn)
            self.cat_grid.attach(btn, i % 3, i // 3, 1, 1)

        self.stack.add_named(outer, "game")

    # ── PANTALLA: PREGUNTA ────────────────────────────────────────────────────
    def _build_question(self):
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.q_hb = Adw.HeaderBar()
        self.q_title = Adw.WindowTitle(title="Pregunta")
        self.q_hb.set_title_widget(self.q_title)
        outer.append(self.q_hb)

        scroll = Gtk.ScrolledWindow(vexpand=True)
        outer.append(scroll)

        clamp = Adw.Clamp(maximum_size=600, margin_top=16, margin_bottom=24)
        scroll.set_child(clamp)

        q_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14,
                        margin_start=16, margin_end=16)
        clamp.set_child(q_box)

        # Spinner de carga
        self.spinner = Gtk.Spinner(halign=Gtk.Align.CENTER,
                                   margin_top=24, margin_bottom=24)
        self.spinner.set_size_request(48, 48)
        q_box.append(self.spinner)

        # Pregunta
        self.q_lbl = Gtk.Label(wrap=True, justify=Gtk.Justification.CENTER)
        self.q_lbl.add_css_class("title-3")
        self.q_lbl.set_margin_top(8)
        self.q_lbl.set_margin_bottom(4)
        q_box.append(self.q_lbl)

        # Opciones de respuesta
        self.ans_btns = []
        letters = ["A", "B", "C", "D"]
        for i in range(4):
            btn = Gtk.Button()
            btn.add_css_class("answer-btn")
            btn.set_hexpand(True)

            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            letter = Gtk.Label(label=f"{letters[i]}.")
            letter.add_css_class("heading")
            row.append(letter)
            self._ans_text_lbls = getattr(self, "_ans_text_lbls", [])
            text_lbl = Gtk.Label(wrap=True, xalign=0, hexpand=True)
            self._ans_text_lbls.append(text_lbl)
            row.append(text_lbl)
            btn.set_child(row)
            btn.connect("clicked", self._on_answer, i)
            self.ans_btns.append(btn)
            q_box.append(btn)

        # Resultado
        self.result_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                                  spacing=10, margin_top=8)
        self.result_lbl = Gtk.Label(wrap=True, justify=Gtk.Justification.CENTER)
        self.result_lbl.add_css_class("title-3")
        self.result_box.append(self.result_lbl)

        self.continue_btn = Gtk.Button(label="Continuar", halign=Gtk.Align.CENTER)
        self.continue_btn.add_css_class("suggested-action")
        self.continue_btn.add_css_class("pill")
        self.continue_btn.connect("clicked", self._on_continue)
        self.result_box.append(self.continue_btn)
        q_box.append(self.result_box)

        # Badge IA
        self.ai_badge = Gtk.Label(halign=Gtk.Align.CENTER, margin_top=4)
        self.ai_badge.set_text("✨ Pregunta generada por IA")
        self.ai_badge.add_css_class("caption")
        self.ai_badge.add_css_class("dim-label")
        q_box.append(self.ai_badge)

        self.stack.add_named(outer, "question")

    # ── PANTALLA: GANADOR ─────────────────────────────────────────────────────
    def _build_winner(self):
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        hb = Adw.HeaderBar()
        hb.set_title_widget(Adw.WindowTitle(title="Fin del juego"))
        outer.append(hb)

        scroll = Gtk.ScrolledWindow(vexpand=True)
        outer.append(scroll)

        clamp = Adw.Clamp(valign=Gtk.Align.CENTER, vexpand=True)
        scroll.set_child(clamp)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16,
                      valign=Gtk.Align.CENTER, halign=Gtk.Align.CENTER,
                      margin_top=48, margin_bottom=48,
                      margin_start=24, margin_end=24)

        trophy = Gtk.Label()
        trophy.set_text("🏆")
        trophy.add_css_class("title-1")
        box.append(trophy)

        self.winner_lbl = Gtk.Label(wrap=True, justify=Gtk.Justification.CENTER)
        self.winner_lbl.add_css_class("title-1")
        box.append(self.winner_lbl)

        self.winner_sub = Gtk.Label(wrap=True, justify=Gtk.Justification.CENTER)
        self.winner_sub.add_css_class("body")
        self.winner_sub.add_css_class("dim-label")
        box.append(self.winner_sub)

        # Tokens ganados
        self.winner_tokens = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,
                                     spacing=8, halign=Gtk.Align.CENTER,
                                     margin_top=8)
        box.append(self.winner_tokens)

        again_btn = Gtk.Button(label="Jugar de nuevo", margin_top=16)
        again_btn.add_css_class("suggested-action")
        again_btn.add_css_class("pill")
        again_btn.connect("clicked", lambda _: self.stack.set_visible_child_name("setup"))
        box.append(again_btn)

        clamp.set_child(box)
        self.stack.add_named(outer, "winner")

    # ─── LÓGICA DEL JUEGO ─────────────────────────────────────────────────────
    def _init_state(self):
        self.current_player = 0
        self.scores = [[False] * len(CATEGORIES) for _ in range(self.num_players)]
        self.used_qs = {cat["name"]: set() for cat in CATEGORIES}
        self.answered = False
        self.current_q = None

    def _refresh_game(self):
        # Reconstruir tarjetas de jugadores
        while child := self.players_row.get_first_child():
            self.players_row.remove(child)

        for i in range(self.num_players):
            card = self._make_player_card(i)
            self.players_row.append(card)

        name = self.player_names[self.current_player]
        self.turn_lbl.set_text(f"Turno de {name}")
        self._game_title_widget.set_subtitle(
            f"Jugador {self.current_player + 1} de {self.num_players}")

        for btn in self.cat_btns:
            btn.set_sensitive(True)

    def _make_player_card(self, idx):
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4,
                        margin_start=2, margin_end=2,
                        margin_top=4, margin_bottom=4)
        if idx == self.current_player:
            outer.add_css_class("player-active-card")
        else:
            outer.add_css_class("player-idle-card")

        name_lbl = Gtk.Label()
        name_lbl.set_text(self.player_names[idx])
        name_lbl.add_css_class("caption-heading")
        name_lbl.set_ellipsize(Pango.EllipsizeMode.END)
        outer.append(name_lbl)

        tokens = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,
                         spacing=3, halign=Gtk.Align.CENTER)
        for ci, cat in enumerate(CATEGORIES):
            dot = Gtk.Label()
            if self.scores[idx][ci]:
                dot.set_text("●")
                dot.add_css_class("token-on")
                # Color via hack: use accent on filled
            else:
                dot.set_text("○")
                dot.add_css_class("token-off")
            tokens.append(dot)
        outer.append(tokens)

        return outer

    # ── Selección de categoría ────────────────────────────────────────────────
    def _on_cat_clicked(self, _, cat_idx):
        self.current_cat = cat_idx
        cat_name = CATEGORIES[cat_idx]["name"]

        # IA si está disponible y hay API key (40% de probabilidad)
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        use_ai = HAS_ANTHROPIC and bool(api_key) and random.random() < 0.4

        # Leer todos los valores de widgets ANTES de crear el thread
        player_name = self.player_names[self.current_player]
        cat_display = CATEGORIES[cat_idx]["name"]

        self._show_loading(cat_idx, player_name)

        if use_ai:
            thread = threading.Thread(
                target=self._ai_generate,
                args=(cat_name, api_key, cat_idx),
                daemon=True
            )
            thread.start()
        else:
            q = self._pick_from_bank(cat_name)
            GLib.idle_add(self._show_question, q, cat_idx, False)

    def _show_loading(self, cat_idx, player_name):
        self.q_title.set_title(CATEGORIES[cat_idx]["name"])
        self.q_title.set_subtitle(f"Turno de {player_name}")
        self.spinner.set_spinning(True)
        self.spinner.set_visible(True)
        self.q_lbl.set_visible(False)
        for btn in self.ans_btns:
            btn.set_visible(False)
        self.result_box.set_visible(False)
        self.ai_badge.set_visible(False)
        self.answered = False
        self.stack.set_visible_child_name("question")

    def _pick_from_bank(self, cat_name):
        bank = BANK[cat_name]
        used = self.used_qs[cat_name]
        avail = [i for i in range(len(bank)) if i not in used]
        if not avail:
            self.used_qs[cat_name] = set()
            avail = list(range(len(bank)))
        idx = random.choice(avail)
        self.used_qs[cat_name].add(idx)
        entry = bank[idx]
        return {"question": entry["q"], "options": entry["o"], "answer": entry["a"]}

    # ── Generación de pregunta por IA (hilo secundario) ───────────────────────
    def _ai_generate(self, cat_name, api_key, cat_idx):
        """NO acceder a ningún widget GTK aquí."""
        try:
            client = anthropic.Anthropic(api_key=api_key)
            prompt = (
                f"Genera una pregunta de trivia sobre '{cat_name}' en español de América Latina. "
                f"Responde ÚNICAMENTE con un objeto JSON con este formato exacto, sin texto adicional:\n"
                f'{{"question": "...", "options": ["A","B","C","D"], "answer": 0}}\n'
                f"Donde 'answer' es el índice (0-3) de la opción correcta. "
                f"Las opciones deben ser creíbles, distintas y sin ambigüedades."
            )
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=350,
                messages=[{"role": "user", "content": prompt}]
            )
            raw = response.content[0].text.strip()
            raw = raw.replace("```json", "").replace("```", "").strip()
            data = json.loads(raw)
            assert "question" in data
            assert isinstance(data.get("options"), list) and len(data["options"]) == 4
            assert isinstance(data.get("answer"), int) and 0 <= data["answer"] <= 3
            GLib.idle_add(self._show_question, data, cat_idx, True)
        except Exception:
            # Fallback al banco
            q = self._pick_from_bank(CATEGORIES[cat_idx]["name"])
            GLib.idle_add(self._show_question, q, cat_idx, False)

    # ── Mostrar pregunta ──────────────────────────────────────────────────────
    def _show_question(self, q_data, cat_idx, is_ai):
        self.current_q = q_data
        self.answered  = False

        self.spinner.set_spinning(False)
        self.spinner.set_visible(False)

        self.q_lbl.set_text(q_data["question"])
        self.q_lbl.set_visible(True)

        for i, btn in enumerate(self.ans_btns):
            self._ans_text_lbls[i].set_text(q_data["options"][i])
            btn.set_sensitive(True)
            btn.remove_css_class("answer-correct")
            btn.remove_css_class("answer-wrong")
            btn.set_visible(True)

        self.result_box.set_visible(False)
        self.ai_badge.set_visible(is_ai)
        self.continue_btn.set_label("Continuar")

        self.stack.set_visible_child_name("question")
        return False  # para GLib.idle_add

    # ── Responder ─────────────────────────────────────────────────────────────
    def _on_answer(self, _, choice):
        if self.answered or self.current_q is None:
            return
        self.answered = True

        correct   = self.current_q["answer"]
        is_right  = (choice == correct)

        for btn in self.ans_btns:
            btn.set_sensitive(False)

        self.ans_btns[correct].add_css_class("answer-correct")
        if not is_right:
            self.ans_btns[choice].add_css_class("answer-wrong")

        if is_right:
            self.scores[self.current_player][self.current_cat] = True
            self.result_lbl.set_text("¡Correcto! +1 ficha")
        else:
            right_text = self.current_q["options"][correct]
            self.result_lbl.set_text(f"Incorrecto. La respuesta era:\n{right_text}")

        # ¿Ya ganó?
        if all(self.scores[self.current_player]):
            self.continue_btn.set_label("Ver ganador 🏆")

        self.result_box.set_visible(True)

    # ── Continuar / siguiente turno ───────────────────────────────────────────
    def _on_continue(self, _):
        if all(self.scores[self.current_player]):
            self._show_winner(self.current_player)
            return
        self.current_player = (self.current_player + 1) % self.num_players
        self._refresh_game()
        self.stack.set_visible_child_name("game")

    # ── Pantalla de ganador ───────────────────────────────────────────────────
    def _show_winner(self, pidx):
        name = self.player_names[pidx]
        self.winner_lbl.set_text(f"¡{name} gana!")
        self.winner_sub.set_text(
            f"{name} respondió correctamente\nen las 6 categorías.")

        while child := self.winner_tokens.get_first_child():
            self.winner_tokens.remove(child)
        for ci, cat in enumerate(CATEGORIES):
            dot_box = Gtk.Box(margin_start=2, margin_end=2)
            dot_box.add_css_class(cat["cc"])
            inner = Gtk.Box(margin_start=6, margin_end=6,
                            margin_top=4, margin_bottom=4)
            lbl = Gtk.Label()
            lbl.set_text(cat["emoji"])
            inner.append(lbl)
            dot_box.append(inner)
            self.winner_tokens.append(dot_box)

        self.stack.set_visible_child_name("winner")

    def _toast(self, msg):
        self.toast_overlay.add_toast(Adw.Toast(title=msg))


# ─── ENTRY POINT ──────────────────────────────────────────────────────────────
def main():
    app = CarreraApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
