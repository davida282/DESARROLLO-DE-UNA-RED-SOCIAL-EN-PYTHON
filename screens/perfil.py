from textual.screen import Screen
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Button, Header, Footer, Input, Static, Label, ListView, ListItem
from core.database import db_instance
from core.auth import auth
from screens.visitar_perfil import VisitarPerfil
from screens.mural import Mural

class Perfil(Screen):
    CSS = """
    Button#publicar { background: green; color: white; border: none; padding: 1; width: 100%; }
    Button#publicar:hover { background: darkgreen; }
    Button#buscar { background: blue; color: white; border: none; padding: 1; width: 100%; }
    Button#buscar:hover { background: darkblue; }
    Button#mural { background: purple; color: white; border: none; padding: 1; width: 100%; }
    Button#mural:hover { background: darkmagenta; }  /* Cambiado de darkpurple a darkmagenta */
    Button#salir { background: gray; color: white; border: none; padding: 1; width: 100%; }
    Button#salir:hover { background: darkgray; }
    """

    def __init__(self, usuario: str):
        super().__init__()
        self.usuario = usuario

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static(f"## Perfil de {self.usuario}", classes="titulo"),
            Input(placeholder="Escribe tu publicación...", id="publicacion"),
            Button("📢 Publicar", id="publicar"),
            Static("", id="lista_publicaciones"),
            Input(placeholder="Buscar usuario...", id="buscar_usuario"),
            ListView(id="sugerencias_lista"),
            Button("🔍 Buscar", id="buscar"),
            Button("📜 Ver mural", id="mural"),
            Button("🚪 Salir", id="salir"),
            Label("", id="mensaje")
        )
        yield Footer()

    def on_mount(self):
        self.cargar_publicaciones()
        self.cargar_usuarios()

    def cargar_publicaciones(self):
        publicaciones = db_instance.read(f"usuarios/{self.usuario}/publicaciones") or {}
        self.query_one("#lista_publicaciones", Static).update("\n".join(publicaciones.values()) if publicaciones else "No hay publicaciones.")

    def cargar_usuarios(self):
        usuarios = db_instance.read("usuarios") or {}
        self.usuarios_disponibles = list(usuarios.keys())

    def on_input_changed(self, event: Input.Changed):
        if event.input.id == "buscar_usuario":
            input_value = event.value.strip().lower()
            sugerencias_lista = self.query_one("#sugerencias_lista", ListView)
            sugerencias_lista.clear()
            if input_value:
                sugerencias = [u for u in self.usuarios_disponibles if input_value in u.lower()]
                for sugerencia in sugerencias:
                    sugerencias_lista.append(ListItem(Label(sugerencia)))

    def on_list_view_selected(self, event: ListView.Selected):
        usuario_seleccionado = event.item.query_one(Label).text
        self.app.push_screen(VisitarPerfil(self.usuario, usuario_seleccionado))

    def on_button_pressed(self, event):
        mensaje = self.query_one("#mensaje", Label)
        publicacion_input = self.query_one("#publicacion", Input)
        buscar_input = self.query_one("#buscar_usuario", Input)

        if event.button.id == "publicar":
            texto = publicacion_input.value.strip()
            if texto:
                db_instance.push(f"usuarios/{self.usuario}/publicaciones", texto)
                publicacion_input.value = ""
                self.cargar_publicaciones()
                mensaje.update("✅ Publicado.")
            else:
                mensaje.update("⚠️ Escribe algo.")
        elif event.button.id == "buscar":
            usuario_a_buscar = buscar_input.value.strip()
            if usuario_a_buscar and db_instance.read(f"usuarios/{usuario_a_buscar}"):
                self.app.push_screen(VisitarPerfil(self.usuario, usuario_a_buscar))
            else:
                mensaje.update("❌ Usuario no encontrado.")
        elif event.button.id == "mural":
            self.app.push_screen(Mural(self.usuario))
        elif event.button.id == "salir":
            auth.logout()
            self.app.pop_screen()