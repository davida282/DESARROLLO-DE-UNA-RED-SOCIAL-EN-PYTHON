from textual.app import App
from pantalla_inicio import PantallaInicio
from pantalla_registro import PantallaRegistro
from pantalla_login import PantallaLogin

class WatchPubApp(App):
    """Aplicación principal de WatchPub."""
    
    def on_mount(self):
        """Registra y muestra la pantalla de inicio."""
        self.install_screen(PantallaInicio(), "pantalla_inicio")
        self.install_screen(PantallaRegistro(), "pantalla_registro")
        self.install_screen(PantallaLogin(), "pantalla_login")
        self.push_screen("pantalla_inicio")

if __name__ == "__main__":
    app = WatchPubApp()
    app.run()
