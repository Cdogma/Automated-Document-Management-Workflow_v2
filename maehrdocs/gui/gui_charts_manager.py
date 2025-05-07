"""
Chart-Manager für die Statistikvisualisierung in MaehrDocs
Dient als zentrale Import-Schnittstelle und Koordinationspunkt für alle 
Chart-bezogenen Funktionen.

Diese Datei vereint die Funktionalitäten aller Chart-Module und stellt eine 
konsistente API für andere Teile der Anwendung zur Verfügung, wodurch die 
Integration und Wartung vereinfacht wird.
"""

import logging
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Import der einzelnen Modul-Komponenten
from .gui_charts_core import (
    create_chart_figure,
    apply_dark_theme, 
    handle_empty_data,
    add_tooltip,
    create_detail_dialog
)
from .gui_charts_basic import (
    update_type_chart,
    update_size_chart
)
from .gui_charts_advanced import (
    update_sender_chart,
    update_timeline_chart
)
from .gui_charts_interactive import register_chart_events

# Logger für Chart-Operationen
logger = logging.getLogger(__name__)

class ChartManager:
    """
    Verwaltet die Charts und ihre Aktualisierung.
    
    Diese Klasse dient als zentrale Zugriffsstelle für alle Chart-Operationen
    und koordiniert die verschiedenen Chart-Module.
    """
    
    def __init__(self, app):
        """
        Initialisiert den ChartManager.
        
        Args:
            app: Die GuiApp-Instanz
        """
        self.app = app
        self.charts = {}  # {chart_name: (figure, canvas, axis)}
        self.event_ids = {}  # {chart_name: event_id}
        self.logger = logger
        
    def create_chart(self, parent_frame, chart_name, chart_type):
        """
        Erstellt ein Chart und registriert es beim Manager.
        
        Args:
            parent_frame: Das übergeordnete Frame
            chart_name: Name des Charts für spätere Referenz
            chart_type: Typ des Charts ('type', 'sender', 'size', 'timeline')
            
        Returns:
            tuple: (Figure, Canvas) für manuelle Anpassungen
        """
        try:
            # Chart erstellen
            figure, canvas = create_chart_figure(self.app, parent_frame)
            ax = figure.add_subplot(111)
            
            # Chart registrieren
            self.charts[chart_name] = (figure, canvas, ax, chart_type)
            
            # Interaktivität hinzufügen
            event_id = register_chart_events(figure, canvas, ax, self.app, chart_type)
            self.event_ids[chart_name] = event_id
            
            return figure, canvas
            
        except Exception as e:
            self.logger.error(f"Fehler beim Erstellen des Charts '{chart_name}': {str(e)}")
            # Leeres Figure und Canvas erstellen als Fallback
            empty_figure = Figure(figsize=(5, 4), dpi=100)
            empty_canvas = FigureCanvasTkAgg(empty_figure, master=parent_frame)
            empty_canvas.get_tk_widget().pack(fill="both", expand=True)
            return empty_figure, empty_canvas
    
    def update_chart(self, chart_name, data):
        """
        Aktualisiert ein Chart mit neuen Daten.
        
        Args:
            chart_name: Name des zu aktualisierenden Charts
            data: Die neuen Daten für das Chart
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        try:
            if chart_name not in self.charts:
                self.logger.warning(f"Chart '{chart_name}' nicht gefunden.")
                return False
                
            figure, canvas, ax, chart_type = self.charts[chart_name]
            
            # Chart leeren
            ax.clear()
            
            # Je nach Chart-Typ aktualisieren
            if chart_type == 'type':
                update_type_chart(ax, data, self.app, figure)
            elif chart_type == 'sender':
                update_sender_chart(ax, data, self.app, figure)
            elif chart_type == 'size':
                update_size_chart(ax, data, self.app, figure)
            elif chart_type == 'timeline':
                update_timeline_chart(ax, data, self.app, figure)
            else:
                self.logger.warning(f"Unbekannter Chart-Typ: {chart_type}")
                handle_empty_data(ax, self.app, f"Unbekannter Chart-Typ: {chart_type}")
                return False
            
            # Canvas aktualisieren
            canvas.draw()
            return True
            
        except Exception as e:
            self.logger.error(f"Fehler beim Aktualisieren des Charts '{chart_name}': {str(e)}")
            
            # Fallback: Fehlermeldung im Chart anzeigen
            if chart_name in self.charts:
                figure, canvas, ax, _ = self.charts[chart_name]
                ax.clear()
                handle_empty_data(ax, self.app, f"Fehler: {str(e)}")
                canvas.draw()
                
            return False
    
    def remove_chart(self, chart_name):
        """
        Entfernt ein Chart aus dem Manager.
        
        Args:
            chart_name: Name des zu entfernenden Charts
            
        Returns:
            bool: True bei Erfolg, False wenn das Chart nicht existiert
        """
        if chart_name in self.charts:
            # Event-Handler deregistrieren
            if chart_name in self.event_ids and self.event_ids[chart_name] > 0:
                figure, canvas, _, _ = self.charts[chart_name]
                canvas.mpl_disconnect(self.event_ids[chart_name])
            
            # Chart aus der Registrierung entfernen
            del self.charts[chart_name]
            if chart_name in self.event_ids:
                del self.event_ids[chart_name]
                
            return True
        return False
    
    def get_chart(self, chart_name):
        """
        Gibt ein registriertes Chart zurück.
        
        Args:
            chart_name: Name des Charts
            
        Returns:
            tuple: (Figure, Canvas, Axis, ChartType) oder None wenn nicht gefunden
        """
        return self.charts.get(chart_name)
    
    def update_all_charts(self, data):
        """
        Aktualisiert alle registrierten Charts mit neuen Daten.
        
        Args:
            data: Die neuen Daten für die Charts
            
        Returns:
            int: Anzahl der erfolgreich aktualisierten Charts
        """
        success_count = 0
        for chart_name in self.charts:
            if self.update_chart(chart_name, data):
                success_count += 1
        return success_count

# Integrationsklasse für die bestehende StatisticsPanel-Klasse
class StatisticsPanelManager:
    """
    Manager für das StatisticsPanel in der gui_statistics.py-Datei.
    
    Diese Klasse dient als Adapter zwischen dem alten StatisticsPanel und 
    dem neuen ChartManager, um eine schrittweise Migration zu ermöglichen.
    """
    
    def __init__(self, app, parent_frame):
        """
        Initialisiert den StatisticsPanelManager.
        
        Args:
            app: Die GuiApp-Instanz
            parent_frame: Das übergeordnete Frame
        """
        self.app = app
        self.parent_frame = parent_frame
        self.chart_manager = ChartManager(app)
        
        # UI erstellen
        self.frame = tk.Frame(parent_frame, bg=app.colors["card_background"], padx=15, pady=15)
        self.frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Hier würde die alte Oberfläche erstellt werden...
        # Bei vollständiger Migration sollte dieser Code durch Aufrufe
        # der ChartManager-Methoden ersetzt werden.
    
    def update_charts(self, data):
        """
        Aktualisiert alle Charts mit neuen Daten.
        
        Args:
            data: Die neuen Daten für die Charts
            
        Returns:
            bool: True bei Erfolg
        """
        try:
            return self.chart_manager.update_all_charts(data) > 0
        except Exception as e:
            logger.error(f"Fehler beim Aktualisieren der Charts: {str(e)}")
            return False

# Exportfunktionen als kompatible API zur alten Implementierung
def create_chart_figure(app, parent_frame):
    """
    Kompatibilitätsfunktion für die alte API.
    
    Args:
        app: Die GuiApp-Instanz
        parent_frame: Das übergeordnete Frame
        
    Returns:
        tuple: (Figure, Canvas)
    """
    return create_chart_figure(app, parent_frame)

def update_type_chart(ax, data, app, figure):
    """
    Kompatibilitätsfunktion für die alte API.
    
    Args:
        ax: Die Achse mit dem Chart
        data: Die Daten für das Chart
        app: Die GuiApp-Instanz
        figure: Die Figure
    """
    update_type_chart(ax, data, app, figure)

def update_sender_chart(ax, data, app, figure):
    """
    Kompatibilitätsfunktion für die alte API.
    
    Args:
        ax: Die Achse mit dem Chart
        data: Die Daten für das Chart
        app: Die GuiApp-Instanz
        figure: Die Figure
    """
    update_sender_chart(ax, data, app, figure)

def update_size_chart(ax, data, app, figure):
    """
    Kompatibilitätsfunktion für die alte API.
    
    Args:
        ax: Die Achse mit dem Chart
        data: Die Daten für das Chart
        app: Die GuiApp-Instanz
        figure: Die Figure
    """
    update_size_chart(ax, data, app, figure)

def update_timeline_chart(ax, data, app, figure):
    """
    Kompatibilitätsfunktion für die alte API.
    
    Args:
        ax: Die Achse mit dem Chart
        data: Die Daten für das Chart
        app: Die GuiApp-Instanz
        figure: Die Figure
    """
    update_timeline_chart(ax, data, app, figure)