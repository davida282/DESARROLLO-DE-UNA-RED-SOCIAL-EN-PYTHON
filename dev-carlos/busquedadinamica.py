import firebase_admin
from firebase_admin import db
from textual.screen import Screen
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Button, Header, Footer, Static, Label, Input, ListView, ListItem

class VisitarPerfil(Screen):
    """Pantalla para visitar el perfil de otro usuario en WatchPub."""

    def __init__(self, usuario_actual: str):
        super().__init__()
        self.usuario_actual = usuario_actual  # Guardar el usuario que inició sesión
        self.usuarios_disponibles = []  # Lista de usuarios disponibles en la base de datos

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Buscar usuario:", id="buscar_titulo"),
            Input(placeholder="Escribe un nombre de usuario...", id="buscar_input"),
            ListView(id="sugerencias_lista"),  # Lista para mostrar sugerencias
            Label("", id="mensaje"),  # Mensaje de feedback
            Button("⬅ Volver a mi perfil", id="volver_perfil"),
        )
        yield Footer()

    def on_mount(self):
        """Carga la lista de usuarios disponibles al montar la pantalla."""
        mensaje = self.query_one("#mensaje", Label)
        try:
            # Obtener todos los usuarios de la base de datos
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
        self.app.push_screen(VisitarPerfil(self.usuario_actual, usuario_seleccionado))

    def on_button_pressed(self, event):
        """Maneja las acciones de los botones."""
        if event.button.id == "volver_perfil":
            from mi_perfil import MiPerfil  # Importación diferida para evitar import circular
            self.app.push_screen(MiPerfil(self.usuario_actual))  # Regresa al perfil principal

# Exportar la clase correctamente
__all__ = ["VisitarPerfil"]