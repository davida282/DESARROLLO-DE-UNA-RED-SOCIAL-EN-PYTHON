from textual.app import App
from screens.inicio import Inicio
from screens.registro import Registro
from screens.login import Login
from screens.perfil import Perfil
from screens.visitar_perfil import VisitarPerfil
from screens.mural import Mural

class WatchPubApp(App):
    def on_mount(self):
        self.install_screen(Inicio(), "inicio")
        self.install_screen(Registro(), "registro")
        self.install_screen(Login(), "login")
        self.install_screen(Perfil, "perfil")
        self.install_screen(VisitarPerfil, "visitar_perfil")
        self.install_screen(Mural, "mural")
        self.push_screen("inicio")

if __name__ == "__main__":
    WatchPubApp().run()