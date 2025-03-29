from textual.screen import Screen
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Header, Footer, Static, ListView, ListItem, Input
from core.database import db_instance
from core.auth import auth
from datetime import datetime
from screens.visitar_perfil import VisitarPerfil

class ComentariosScreen(Screen):
    def __init__(self, pub_id, usuario):
        super().__init__()
        self.pub_id = pub_id
        self.usuario = usuario

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("💬 Comentarios")
        
        self.comentarios_container = Vertical(id="comentarios_container")
        yield self.comentarios_container
        
        yield Input(placeholder="Escribe un comentario...", id="comentario_input")
        yield Horizontal(
            Button("📤 Enviar comentario", id="enviar_comentario"),
            Button("🔙 Volver", id="volver_comentarios")
        )
        yield Footer()

    def on_mount(self) -> None:
        pub = db_instance.read(f"publicaciones/{self.pub_id}")
        if not pub:
            self.comentarios_container.mount(Static("Error: La publicación no existe."))
            return
        
        comentarios = pub.get("comentarios", {})
        if comentarios:
            for comentario_id, comentario in comentarios.items():
                self.comentarios_container.mount(
                    Static(f"{comentario.get('autor', 'Anónimo')}: {comentario.get('texto', '')}")
                )
        else:
            self.comentarios_container.mount(Static("No hay comentarios aún."))

    def on_button_pressed(self, event) -> None:
        if event.button.id == "enviar_comentario":
            comentario_input = self.query_one("#comentario_input", Input)
            comentario_texto = comentario_input.value.strip()
            
            if not comentario_texto:
                self.app.notify("Por favor, escribe un comentario.", severity="warning")
                return

            pub = db_instance.read(f"publicaciones/{self.pub_id}")
            if pub:
                comentarios = pub.get("comentarios", {})
                comentario_data = {
                    "texto": comentario_texto,
                    "autor": self.usuario,
                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                comentario_id = db_instance.push(f"publicaciones/{self.pub_id}/comentarios", comentario_data)
                comentarios[comentario_id] = comentario_data
                pub["comentarios"] = comentarios
                db_instance.update(f"publicaciones/{self.pub_id}", pub)
                db_instance.update(f"usuarios/{pub['autor']}/publicaciones/{self.pub_id}", pub)
                comentario_input.value = ""
                self.app.notify("Comentario enviado con éxito.", severity="info")
                self.app.pop_screen()
            else:
                self.app.notify("Error: No se pudo enviar el comentario. La publicación no existe.", severity="error")
        elif event.button.id == "volver_comentarios":
            self.app.pop_screen()

class Mural(Screen):
    CSS = """
    ListView { height: 65%; border: tall $background; }
    .publicacion { padding: 1 2; border: tall $background; margin-bottom: 1; }
    .publicacion-contenido { color: $text; }
    .publicacion-meta { color: $text-muted; margin-top: 1; }
    Button#publicar { background: purple; color: white; border: none; padding: 1; width: 100%; }
    Button#publicar:hover { background: darkmagenta; }
    Button#buscar { background: blue; color: white; border: none; padding: 1; width: 100%; }
    Button#buscar:hover { background: darkblue; }
    Button#salir { background: gray; color: white; border: none; padding: 1; width: 100%; }
    Button#salir:hover { background: darkgray; }
    Input#nueva_publicacion_input { width: 100%; margin-bottom: 1; }
    Input#buscar_usuario_input { width: 100%; margin-bottom: 1; }
    """

    def __init__(self, usuario: str):
        super().__init__()
        self.usuario = usuario

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("📜 Mural de WatchPub")
        yield Input(placeholder="Escribe tu publicación aquí...", id="nueva_publicacion_input")
        yield Button("📝 Publicar", id="publicar")
        self.lista_publicaciones = ListView(id="lista_publicaciones")
        yield self.lista_publicaciones
        yield Input(placeholder="Buscar usuario...", id="buscar_usuario_input")
        yield Button("🔍 Buscar", id="buscar")
        yield Button("🚪 Salir", id="salir")
        yield Footer()

    def on_mount(self):
        self.actualizar_mural()

    def actualizar_mural(self):
        self.lista_publicaciones.clear()
        publicaciones = db_instance.read("publicaciones") or {}
        for pub_id, pub in publicaciones.items():
            likes = pub.get("likes", 0)
            comentarios = len(pub.get("comentarios", {}))
            botones = [
                Button(f"👍 {likes}", id=f"like_{pub_id}"),
                Button(f"💬 {comentarios}", id=f"comentar_{pub_id}")
            ]
            if pub["autor"] == self.usuario:
                botones.append(Button("🗑 Eliminar", id=f"eliminar_{pub_id}"))
            publicacion_widget = Container(
                Static(pub["contenido"], classes="publicacion-contenido"),
                Static(f"Autor: {pub['autor']} | Fecha: {pub['fecha']}", classes="publicacion-meta"),
                Horizontal(*botones),
                classes="publicacion"
            )
            self.lista_publicaciones.append(ListItem(publicacion_widget))

    def on_button_pressed(self, event):
        if event.button.id == "publicar":
            texto = self.query_one("#nueva_publicacion_input", Input).value.strip()
            if texto:
                pub_data = {
                    "contenido": texto,
                    "autor": self.usuario,
                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "likes": 0,
                    "like_users": [],
                    "comentarios": {}
                }
                pub_id = db_instance.push("publicaciones", pub_data)
                db_instance.write(f"usuarios/{self.usuario}/publicaciones/{pub_id}", pub_data)
                self.query_one("#nueva_publicacion_input", Input).value = ""
                self.actualizar_mural()
        elif event.button.id.startswith("like_"):
            pub_id = event.button.id.split("_")[1]
            pub = db_instance.read(f"publicaciones/{pub_id}")
            if pub:
                like_users = pub.get("like_users", [])
                if self.usuario in like_users:
                    like_users.remove(self.usuario)
                    pub["likes"] = len(like_users)
                else:
                    like_users.append(self.usuario)
                    pub["likes"] = len(like_users)
                pub["like_users"] = like_users
                db_instance.update(f"publicaciones/{pub_id}", pub)
                db_instance.update(f"usuarios/{pub['autor']}/publicaciones/{pub_id}", pub)
                self.actualizar_mural()
            else:
                self.app.notify(f"Error: La publicación {pub_id} no existe.", severity="error")
        elif event.button.id.startswith("comentar_"):
            pub_id = event.button.id.split("_")[1]
            self.app.push_screen(ComentariosScreen(pub_id, self.usuario))
        elif event.button.id.startswith("eliminar_"):
            pub_id = event.button.id.split("_")[1]
            pub = db_instance.read(f"publicaciones/{pub_id}")
            if pub:
                db_instance.delete(f"publicaciones/{pub_id}")
                db_instance.delete(f"usuarios/{self.usuario}/publicaciones/{pub_id}")
                self.actualizar_mural()
        elif event.button.id == "buscar":
            usuario_a_buscar = self.query_one("#buscar_usuario_input", Input).value.strip()
            if usuario_a_buscar and db_instance.read(f"usuarios/{usuario_a_buscar}"):
                self.app.push_screen(VisitarPerfil(self.usuario, usuario_a_buscar))
                self.query_one("#buscar_usuario_input", Input).value = ""
            else:
                self.app.notify("❌ Usuario no encontrado.", severity="error")
        elif event.button.id == "salir":
            auth.logout()
            self.app.pop_screen()