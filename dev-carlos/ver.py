from textual.screen import Screen
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Button, Header, Footer, Input, Static, Label, ListView, ListItem
import firebase_admin
from firebase_admin import db
from visitar_perfil import VisitarPerfil

class MiPerfil(Screen):
    """Pantalla de perfil del usuario en WatchPub."""

    def __init__(self, usuario: str):
        super().__init__()
        self.usuario = usuario  # Guardar el nombre de usuario
        self.publicaciones = []  # Lista para mostrar publicaciones
        self.usuarios_disponibles = []  # Lista de usuarios disponibles en la base de datos

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static(f"## Perfil de {self.usuario}", classes="titulo"),
            Input(placeholder="Escribe tu publicación...", id="publicacion"),
            Button("📢 Publicar", id="publicar"),
            Static("", id="lista_publicaciones"),  # Área donde se mostrarán las publicaciones
            Input(placeholder="Buscar usuario...", id="buscar_usuario"),
            ListView(id="sugerencias_lista"),  # Lista para mostrar sugerencias dinámicas
            Button("🚪 Salir", id="salir"),  # Cambiado de "Volver" a "Salir"
            Label("", id="mensaje")  # Mensaje de feedback
        )
        yield Footer()

    def on_mount(self):
        """Carga las publicaciones y usuarios disponibles al montar la pantalla."""
        self.cargar_publicaciones()
        self.cargar_usuarios()

    def cargar_publicaciones(self):
        """Carga publicaciones desde la base de datos y las muestra."""
        publicaciones_ref = db.reference(f"usuarios/{self.usuario}/publicaciones").get()
        if publicaciones_ref:
            self.publicaciones = list(publicaciones_ref.values())
        lista_publicaciones = self.query_one("#lista_publicaciones", Static)
        lista_publicaciones.update("\n".join(self.publicaciones) if self.publicaciones else "No hay publicaciones.")

    def cargar_usuarios(self):
        """Carga la lista de usuarios disponibles desde la base de datos."""
        mensaje = self.query_one("#mensaje", Label)
        try:
            ref = db.reference("usuarios").get()
            if ref:
                self.usuarios_disponibles = list(ref.keys())
                mensaje.update("✅ Usuarios cargados correctamente.")
                self.app.log("✅ Lista de usuarios cargada desde la base de datos.")
            else:
                mensaje.update("⚠ No hay usuarios en la base de datos.")
                self.app.log("⚠ No se encontraron usuarios en la base de datos.")
        except Exception as e:
            mensaje.update(f"❌ Error al cargar usuarios: {e}")
            self.app.log(f"❌ Error al cargar usuarios: {e}")

    def on_input_changed(self, event: Input.Changed):
        """Actualiza las sugerencias mientras el usuario escribe."""
        if event.input.id == "buscar_usuario":
            input_value = event.value.strip().lower()
            sugerencias_lista = self.query_one("#sugerencias_lista", ListView)
            sugerencias_lista.clear()  # Limpiar las sugerencias anteriores

            if input_value:
                # Filtrar usuarios que coincidan con el texto ingresado
                sugerencias = [u for u in self.usuarios_disponibles if input_value in u.lower()]
                for sugerencia in sugerencias:
                    sugerencias_lista.append(ListItem(Label(sugerencia)))
            else:
                sugerencias_lista.clear()  # Si no hay texto, no mostrar sugerencias

    def on_list_view_selected(self, event: ListView.Selected):
        """Maneja la selección de un usuario de las sugerencias."""
        usuario_seleccionado = event.item.query_one(Label).text
        self.app.log(f"Usuario seleccionado: {usuario_seleccionado}")
        self.app.push_screen(VisitarPerfil(self.usuario, usuario_seleccionado))

    def on_button_pressed(self, event):
        """Maneja las acciones de los botones."""
        mensaje = self.query_one("#mensaje", Label)
        publicacion_input = self.query_one("#publicacion", Input)
        lista_publicaciones = self.query_one("#lista_publicaciones", Static)

        self.app.log(f"🔘 Botón presionado: {event.button.id}")
        mensaje.update(f"🔘 Botón presionado: {event.button.id}")
        self.refresh()

        if event.button.id == "publicar":
            texto = publicacion_input.value.strip()
            if texto:
                mensaje.update("✅ Publicación enviada.")
                self.app.log(f"✅ Publicación de {self.usuario}: {texto}")
                publicacion_input.value = ""  # Limpiar el campo después de publicar

                # Guardar publicación en la base de datos
                publicaciones_ref = db.reference(f"usuarios/{self.usuario}/publicaciones")
                publicaciones_ref.push(texto)

                # Mostrar la publicación en pantalla
                self.publicaciones.append(texto)
                lista_publicaciones.update("\n".join(self.publicaciones))
            else:
                mensaje.update("⚠️ Escribe algo antes de publicar.")
                self.app.log("⚠️ Intento de publicación vacía.")
            self.refresh()

        elif event.button.id == "salir":
            self.app.exit()  # Cierra la aplicación y regresa al menú principal

# Exportar la clase correctamente
__all__ = ["MiPerfil"]