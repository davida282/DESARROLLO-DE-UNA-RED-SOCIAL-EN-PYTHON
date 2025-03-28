import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db

from textual.app import App, ComposeResult
from textual.widgets import Button, Header, Footer, Static, Input, ListView, ListItem
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.message import Message
from textual import on

# Inicializa Firebase
cred = credentials.Certificate("Base de datos.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://red-social-python-default-rtdb.firebaseio.com/"
})

def cargar_publicaciones():
    ref = db.reference("publicaciones")
    data = ref.get()
    return [{"id": k, **v} for k, v in data.items()] if isinstance(data, dict) else []

def guardar_publicacion(publicacion):
    ref = db.reference("publicaciones").push()
    ref.set(publicacion)
    return ref.key

def eliminar_publicacion(pub_id):
    ref = db.reference(f"publicaciones/{pub_id}")
    ref.delete()

def agregar_comentario(pub_id, comentario, autor):
    ref = db.reference(f"publicaciones/{pub_id}/comentarios")
    nuevo_comentario = {
        "contenido": comentario,
        "autor": autor,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    ref.push().set(nuevo_comentario)

def dar_like(pub_id, user):
    ref = db.reference(f"publicaciones/{pub_id}")
    publicacion = ref.get()
    likes_users = publicacion.get("like_users", [])
    
    if user not in likes_users:
        # Add like
        likes_users.append(user)
        publicacion["likes"] = len(likes_users)
        publicacion["like_users"] = likes_users
    else:
        # Remove like if already liked
        likes_users.remove(user)
        publicacion["likes"] = len(likes_users)
        publicacion["like_users"] = likes_users
    
    ref.set(publicacion)

class ComentariosScreen(Screen):
    def __init__(self, pub_id):
        super().__init__()
        self.pub_id = pub_id

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("💬 Comentarios")
        
        # Area para mostrar comentarios existentes
        self.comentarios_container = Vertical(id="comentarios_container")
        yield self.comentarios_container
        
        # Input para nuevo comentario
        yield Input(placeholder="Escribe un comentario...", id="comentario_input")
        yield Horizontal(
            Button("📤 Enviar comentario", id="enviar_comentario"),
            Button("🔙 Volver", id="volver_comentarios")
        )
        yield Footer()

    def on_mount(self) -> None:
        # Cargar y mostrar comentarios existentes
        ref = db.reference(f"publicaciones/{self.pub_id}")
        publicacion = ref.get()
        comentarios = publicacion.get("comentarios", {})
        
        if comentarios:
            for comentario_id, comentario in comentarios.items():
                self.comentarios_container.mount(
                    Static(f"{comentario.get('autor', 'Anónimo')}: {comentario.get('contenido', '')}")
                )
        else:
            self.comentarios_container.mount(Static("No hay comentarios aún."))

    def on_button_pressed(self, event) -> None:
        if event.button.id == "enviar_comentario":
            comentario_input = self.query_one("#comentario_input", Input)
            comentario_texto = comentario_input.value.strip()
            
            if comentario_texto:
                # Agregar comentario usando la función existente
                agregar_comentario(self.pub_id, comentario_texto, self.app.user)
                comentario_input.value = ""  # Limpiar input
                self.app.pop_screen()
                self.app.current_app.publicaciones = cargar_publicaciones()
                self.app.current_app.actualizar_mural()
        
        elif event.button.id == "volver_comentarios":
            self.app.pop_screen()

class PublicacionScreen(Screen):
    class PublicarMensaje(Message):
        def __init__(self, publicacion: dict) -> None:
            self.publicacion = publicacion
            super().__init__()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("📝 Escribe tu publicación")
        yield Input(placeholder="Escribe aquí...", id="entrada")
        yield Horizontal(
            Button("📢 Publicar", id="publicar"),
            Button("🔙 Volver", id="volver_publicacion")
        )
        yield Footer()

    def on_button_pressed(self, event) -> None:
        if event.button.id == "publicar":
            texto = self.query_one("#entrada", Input).value.strip()
            if texto:
                nueva_publicacion = {
                    "contenido": texto,
                    "likes": 0,
                    "comentarios": {},
                    "like_users": [],
                    "autor": self.app.user,
                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                self.app.post_message(self.PublicarMensaje(nueva_publicacion))
            self.app.pop_screen()
        
        elif event.button.id == "volver_publicacion":
            self.app.pop_screen()

class InterfazInicial(App):
    CSS = """
    ListView {
        height: 100%;
        border: tall $background;
    }
    
    .publicacion {
        padding: 1 2;
        border: tall $background;
        margin-bottom: 1;
    }
    
    .publicacion-contenido {
        color: $text;
    }
    
    .publicacion-meta {
        color: $text-muted;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("🎵 BIENVENIDO A WATCHPUBAPP 🎵")
        yield Button("📝 Crear una publicación", id="boton_publicar")
        
        self.lista_publicaciones = ListView(id="lista_publicaciones")
        yield self.lista_publicaciones
        
        yield Footer()

    def on_mount(self) -> None:
        self.current_app = self
        self.publicaciones = cargar_publicaciones()
        self.actualizar_mural()

    def on_button_pressed(self, event) -> None:
        if event.button.id == "boton_publicar":
            self.push_screen(PublicacionScreen())
        elif event.button.id.startswith("eliminar_"):
            pub_id = event.button.id.split("_")[1]
            # Verificar que solo el autor pueda eliminar
            publicacion = next((p for p in self.publicaciones if p["id"] == pub_id), None)
            if publicacion and publicacion["autor"] == self.user:
                self.publicaciones = [p for p in self.publicaciones if p["id"] != pub_id]
                eliminar_publicacion(pub_id)
                self.actualizar_mural()
        elif event.button.id.startswith("like_"):
            pub_id = event.button.id.split("_")[1]
            dar_like(pub_id, self.user)
            self.publicaciones = cargar_publicaciones()
            self.actualizar_mural()
        elif event.button.id.startswith("ver_"):
            pub_id = event.button.id.split("_")[1]
            self.push_screen(ComentariosScreen(pub_id))

    @on(PublicacionScreen.PublicarMensaje)
    def recibir_publicacion(self, message: PublicacionScreen.PublicarMensaje) -> None:
        message.publicacion["id"] = guardar_publicacion(message.publicacion)
        self.publicaciones.append(message.publicacion)
        self.actualizar_mural()

    def actualizar_mural(self) -> None:
        # Limpiamos la lista antes de agregar nuevos elementos
        self.lista_publicaciones.clear()
        
        if self.publicaciones:
            for pub in reversed(self.publicaciones):  # Mostramos de más reciente a más antiguo
                # Contar comentarios
                num_comentarios = len(pub.get('comentarios', {}) if pub.get('comentarios') else [])
                
                # Personalizar botones para el autor
                botones = [
                    Button(f"👍 {pub['likes']}", id=f"like_{pub['id']}"),
                    Button(f"💬 Comentarios ({num_comentarios})", id=f"ver_{pub['id']}")
                ]
                
                # Solo mostrar botón de eliminar si es el autor
                if pub["autor"] == self.user:
                    botones.append(Button("🗑 Eliminar", id=f"eliminar_{pub['id']}"))
                
                # Creamos un ListItem con toda la información de la publicación
                publicacion_widget = Container(
                    Static(pub["contenido"], classes="publicacion-contenido"),
                    Static(f"👍 {pub['likes']} 💬 {num_comentarios} | Autor: {pub['autor']} | Fecha: {pub['fecha']}", classes="publicacion-meta"),
                    Horizontal(*botones),
                    classes="publicacion"
                )
                
                self.lista_publicaciones.append(ListItem(publicacion_widget))
        else:
            self.lista_publicaciones.append(ListItem(Static("(Sin publicaciones)")))

    @property
    def user(self) -> str:
        return "usuario_demo"

if __name__ == "__main__":
    InterfazInicial().run()