from database.regione_DAO import RegioneDAO
from database.tour_DAO import TourDAO
from database.attrazione_DAO import AttrazioneDAO

class Model:
    def __init__(self):
        self.tour_map = {} # Mappa ID tour -> oggetti Tour
        self.attrazioni_map = {} # Mappa ID attrazione -> oggetti Attrazione

        self._pacchetto_ottimo = []
        self._valore_ottimo: int = -1
        self._costo = 0

        # Caricamento
        self.load_tour()
        self.load_attrazioni()
        self.load_relazioni()

    @staticmethod
    def load_regioni():
        """ Restituisce tutte le regioni disponibili """
        return RegioneDAO.get_regioni()

    def load_tour(self):
        """ Carica tutti i tour in un dizionario [id, Tour]"""
        self.tour_map = TourDAO.get_tour()

    def load_attrazioni(self):
        """ Carica tutte le attrazioni in un dizionario [id, Attrazione]"""
        self.attrazioni_map = AttrazioneDAO.get_attrazioni()


# funzione che gestisce la relazione molti a molti
    def load_relazioni(self):
        """
            Interroga il database per ottenere tutte le relazioni fra tour e attrazioni e salvarle nelle strutture dati
            Collega tour <-> attrazioni.
            --> Ogni Tour ha un set di Attrazione.
            --> Ogni Attrazione ha un set di Tour.
        """

        # ricavo la lista di relazioni tra Tour e Attrazioni (prese dal database usando il DAO)
        relazioni = TourDAO.get_tour_attrazioni()
        for relazione in relazioni:
            # per ogni tour appendo l'oggetto attrazione contenente set usando come chiave id_attrazione
            self.tour_map[relazione['id_tour']].attrazioni.add(self.attrazioni_map[relazione['id_attrazione']])
            # per ogni attrazione appendo l'oggetto tour contenente set usando come chiave id_tour
            self.attrazioni_map[relazione['id_attrazione']].tour.add(self.tour_map[relazione['id_tour']])


# funzione che genera il pacchetto tramite ricorsione
    def genera_pacchetto(self, id_regione: str, max_giorni: int = None, max_budget: float = None):
        """
        Calcola il pacchetto turistico ottimale per una regione rispettando i vincoli di durata, budget e attrazioni uniche.
        :param id_regione: id della regione
        :param max_giorni: numero massimo di giorni (può essere None --> nessun limite)
        :param max_budget: costo massimo del pacchetto (può essere None --> nessun limite)

        :return: self._pacchetto_ottimo (una lista di oggetti Tour)
        :return: self._costo (il costo del pacchetto)
        :return: self._valore_ottimo (il valore culturale del pacchetto)
        """
        self._pacchetto_ottimo = []
        self._costo = 0
        self._valore_ottimo = -1

        # valori di inizializzazione
        self._id_regione = id_regione
        self._max_giorni = max_giorni if max_giorni is not None else float('inf')
        self._max_budget = max_budget if max_budget is not None else float('inf')

        # richiamo della funzione di ricorsione
        self._ricorsione(0, [], 0, 0, 0, set())
        return self._pacchetto_ottimo, self._costo, self._valore_ottimo


    def _ricorsione(self, start_index: int, pacchetto_parziale: list, durata_corrente: int, costo_corrente: float, valore_corrente: int, attrazioni_usate: set):
        """ Algoritmo di ricorsione che deve trovare il pacchetto che massimizza il valore culturale"""

        # condizione di esistenza del problema (sorta di vincolo iniziale per limitare la lunghezza delle soluzioni parziali)
        if costo_corrente > self._max_budget or durata_corrente > self._max_giorni:
            return

        # condizione di uscita
        if valore_corrente > self._valore_ottimo:
            self._valore_ottimo = valore_corrente
            self._costo = costo_corrente
            self._pacchetto_ottimo = pacchetto_parziale.copy()

        # condizione di ricorsione
        tours = self.tour_disponibili()
        for i in range(start_index, len(tours)):
            tour = tours[i]
            attrazioni_tour = set([rel["id_attrazione"] for rel in self.relazioni_map if rel['id_tour'] == tour.id])
            attrazioni_non_usate = attrazioni_tour - attrazioni_usate
            if attrazioni_non_usate:
                nuovo_costo = costo_corrente + tour.costo
                nuova_durata = durata_corrente + tour.durata
                nuovo_valore = valore_corrente + max(self.attrazioni_map[a].valore_culturale for a in attrazioni_non_usate)
                # back tracking
                nuovo_attrazioni_usate = attrazioni_tour - attrazioni_non_usate
                self._ricorsione(i+1, pacchetto_parziale + [tour], nuova_durata, nuovo_costo, nuovo_valore, nuovo_attrazioni_usate)


    def tour_disponibili(self):
        return [tour for tour in self.tour_map.values() if tour.id_regione == self._id_regione]