# -*- coding: utf-8 -*-
"""
***************************************************************************
    Analisi dei corsi del paramento
    -------------------------------
    Riconoscimento automatico dei CORSI (filari orizzontali) in un paramento
    murario gia' segmentato in componenti poligonali, con calcolo per corso
    di: numero di pezzi, quota media, altezza, lunghezza, inclinazione, e
    (opzionale) spessore del letto di malta verso il corso superiore.

    METODO:
    Porta in ambiente QGIS Processing la logica incrementale "a catena" di
    TagLab (source/QtCourseAnalysis.py, detectCoursesIncremental). L'algoritmo
    NON e' un clustering: costruisce ogni corso partendo dal pezzo piu' a
    sinistra ed estendendolo verso destra, agganciando di volta in volta il
    primo componente compatibile con l'ultimo gia' inserito. La compatibilita'
    e' valutata con quattro test, tre dei quali RELATIVI all'altezza del pezzo
    (cosi' la scala si adatta da sola a laterizi sottili o blocchi alti):

      1) gap orizzontale  <= larghezza media del corso * x_gap_factor
      2) continuita' del centroide Y      <= height * y_tolerance_factor
      3) continuita' dei bordi alto/basso <= height * ytb_tolerance_factor
      4) somiglianza di altezza: rapporto in [1-h, 1+h], h = height_tolerance_factor

    DIFFERENZE RISPETTO A TagLab:
      * TagLab lavora in pixel immagine con Y verso il BASSO e bbox
        [top, left, w, h]. Qui i rilievi sono raddrizzati in coordinate mappa
        con Y verso l'ALTO: il "bordo alto" di un pezzo e' centroid_y + h/2 e
        il "bordo basso" e' centroid_y - h/2. La logica e' identica, cambiano
        i segni.
      * L'altezza del pezzo NON e' presa dal bbox dell'immagine ma dal campo
        height_bbox di MensioAnalysisTools (lato minore del minimum oriented
        bounding box), e la larghezza dal campo width_bbox (lato maggiore).
      * Il segno dell'inclinazione non e' negato (Y gia' verso l'alto):
        positivo = corso che sale verso destra.

    INTEGRAZIONE CON MensioAnalysisTools:
    Si concatena all'output 'analisi_rilievo'. Campi usati:
        lunghezza <- width_bbox    (lato maggiore del bbox orientato)
        altezza   <- height_bbox   (lato minore del bbox orientato)
        id        <- (campo identificativo scelto, di norma fid)
    Il centroide e' calcolato dalla geometria del poligono.

    OUTPUT:
      1) Componenti con corso (poligoni): copia del layer in ingresso con i
         campi aggiunti corso_id, pos_in_corso, corso_n_pezzi e, con l'analisi
         dei giunti attiva, giunto_vert (giunto verticale di testa verso il
         pezzo a destra nello stesso corso).
      2) Sintesi per corso (tabella): una riga per corso con corso_id,
         n_pezzi, quota_media, altezza_corso, lunghezza_corso, inclinaz_deg
         e, se attiva l'analisi dei giunti:
           - letto_malta_sup  = spessore del letto di malta orizzontale verso
                                il corso superiore (cadenza verticale);
           - sfalso_giunti_sup = sfalsamento medio dei giunti verticali
                                rispetto al corso superiore, indice di
                                ammorsatura (0 = giunti allineati / cesura;
                                0.5 = sfalsamento di mezzo pezzo).
         Con il rilevamento delle discontinuita' attivo, sia la sintesi sia
         i componenti ricevono 'segmento' (id del tratto costruttivo omogeneo,
         dal basso) e la sintesi anche 'cesura' (1 sul primo corso di ogni
         nuovo segmento). I segmenti sono tratti costruttivi omogenei; le
         cesure (candidate a giornate di lavoro, riprese o lotti diversi di
         materiale)
         sono individuate dove cambia il regime costruttivo (letto di malta,
         altezza, ammorsatura) con change-point detection lungo la serie dei
         corsi.

    DIPENDENZE:
      Obbligatoria: numpy (sempre presente in QGIS).
      Opzionale: ruptures (algoritmo PELT) per il rilevamento delle
        discontinuita'. Se non e' installata, lo script ricade automaticamente su un
        rilevatore interno in puro numpy (binary segmentation) con criterio L2
        e scala log(N) equivalente, che produce gli stessi risultati a parita'
        di penalita'. ruptures conviene solo per la velocita' su serie molto
        lunghe. Installazione (OSGeo4W Shell): python -m pip install ruptures
***************************************************************************
"""

import math
import numpy as np

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterField,
    QgsProcessingParameterNumber,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFeatureSink,
    QgsField,
    QgsFields,
    QgsFeature,
    QgsFeatureSink,
    QgsWkbTypes,
)


class CourseAnalysis(QgsProcessingAlgorithm):

    INPUT = 'INPUT'
    FIELD_ID = 'FIELD_ID'
    FIELD_LEN = 'FIELD_LEN'
    FIELD_HGT = 'FIELD_HGT'
    Y_TOL = 'Y_TOL'
    YTB_TOL = 'YTB_TOL'
    H_TOL = 'H_TOL'
    X_GAP = 'X_GAP'
    DO_JOINTS = 'DO_JOINTS'
    DO_DAYS = 'DO_DAYS'
    DAYS_SERIES = 'DAYS_SERIES'
    DAYS_PEN = 'DAYS_PEN'
    OUTPUT = 'OUTPUT'
    OUTPUT_COURSES = 'OUTPUT_COURSES'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return CourseAnalysis()

    def name(self):
        return 'analisi_corsi_paramento'

    def displayName(self):
        return 'Analisi dei corsi del paramento'

    def group(self):
        return 'Analisi quantitative'

    def groupId(self):
        return 'analisi'

    def shortHelpString(self):
        return self.tr(
            "Riconosce i corsi (filari orizzontali) di un paramento gia' "
            "segmentato in componenti poligonali, adattando la logica "
            "incrementale di TagLab (QtCourseAnalysis).\n\n"
            "Richiede un rilievo RADDRIZZATO con Y verso l'alto. Usa i campi "
            "width_bbox (lunghezza) e height_bbox (altezza) prodotti da "
            "MensioAnalysisTools; il centroide e' ricavato dalla geometria.\n\n"
            "Un componente si aggancia al corso se, rispetto all'ultimo pezzo "
            "gia' inserito: il gap in X non supera la larghezza media del corso "
            "per x_gap_factor; il centroide Y, e i bordi alto e basso, restano "
            "entro le rispettive tolleranze (relative all'altezza); e l'altezza "
            "e' simile (rapporto entro 1+-h_tol).\n\n"
            "Output: i componenti con corso_id/pos_in_corso/corso_n_pezzi (e, "
            "con l'analisi dei giunti attiva, giunto_vert per ogni pezzo) e una "
            "tabella di sintesi per corso (n. pezzi, quota, altezza, lunghezza, "
            "inclinazione e, se richiesto, letto_malta_sup = spessore del letto "
            "di malta verso il corso superiore, e sfalso_giunti_sup = sfalsamento "
            "dei giunti verticali rispetto al corso superiore, indice di "
            "ammorsatura).\n\n"
            "DIPENDENZE: numpy (sempre presente in QGIS) e' sufficiente. Il "
            "rilevamento delle discontinuita' usa, se installata, la libreria "
            "'ruptures' (algoritmo PELT); in sua assenza ricade automaticamente "
            "su un rilevatore interno in puro numpy che fornisce risultati "
            "equivalenti. 'ruptures' e' quindi OPZIONALE: conviene solo per "
            "velocizzare l'analisi su serie molto lunghe (centinaia di corsi). "
            "Per installarla, dalla OSGeo4W Shell: python -m pip install ruptures"
        )

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.INPUT, self.tr('Layer poligonale dei componenti'),
            [QgsProcessing.TypeVectorPolygon]))
        self.addParameter(QgsProcessingParameterField(
            self.FIELD_ID, self.tr('Campo identificativo univoco'),
            parentLayerParameterName=self.INPUT))
        self.addParameter(QgsProcessingParameterField(
            self.FIELD_LEN, self.tr('Campo lunghezza (width_bbox)'),
            parentLayerParameterName=self.INPUT,
            type=QgsProcessingParameterField.Numeric))
        self.addParameter(QgsProcessingParameterField(
            self.FIELD_HGT, self.tr('Campo altezza (height_bbox)'),
            parentLayerParameterName=self.INPUT,
            type=QgsProcessingParameterField.Numeric))
        self.addParameter(QgsProcessingParameterNumber(
            self.Y_TOL, self.tr('Tolleranza centroide Y (frazione dell\'altezza)'),
            type=QgsProcessingParameterNumber.Double, defaultValue=0.3, minValue=0.0))
        self.addParameter(QgsProcessingParameterNumber(
            self.YTB_TOL, self.tr('Tolleranza bordi alto/basso (frazione dell\'altezza)'),
            type=QgsProcessingParameterNumber.Double, defaultValue=0.3, minValue=0.0))
        self.addParameter(QgsProcessingParameterNumber(
            self.H_TOL, self.tr('Tolleranza somiglianza di altezza (frazione)'),
            type=QgsProcessingParameterNumber.Double, defaultValue=0.3, minValue=0.0))
        self.addParameter(QgsProcessingParameterNumber(
            self.X_GAP, self.tr('Fattore gap massimo in X (x larghezza media del corso)'),
            type=QgsProcessingParameterNumber.Double, defaultValue=1.5, minValue=0.0))
        self.addParameter(QgsProcessingParameterBoolean(
            self.DO_JOINTS,
            self.tr('Analisi dei giunti (letti orizzontali, giunti verticali, ammorsatura)'),
            defaultValue=True))
        self.addParameter(QgsProcessingParameterBoolean(
            self.DO_DAYS,
            self.tr('Rilevamento discontinuità nei giunti (change-point)'),
            defaultValue=True))
        self.addParameter(QgsProcessingParameterEnum(
            self.DAYS_SERIES,
            self.tr('Segnale per il rilevamento delle discontinuità'),
            options=['letto di malta', 'altezza corso', 'sfalsamento giunti',
                     'letto + sfalsamento (multivariato)',
                     'letto + sfalsamento + altezza (multivariato completo)'],
            defaultValue=3))
        self.addParameter(QgsProcessingParameterNumber(
            self.DAYS_PEN,
            self.tr('Sensibilita\': alta = poche cesure nette, bassa = piu\' cesure'),
            type=QgsProcessingParameterNumber.Double, defaultValue=2.5, minValue=0.0))
        self.addParameter(QgsProcessingParameterFeatureSink(
            self.OUTPUT, self.tr('Componenti con corso')))
        self.addParameter(QgsProcessingParameterFeatureSink(
            self.OUTPUT_COURSES, self.tr('Sintesi per corso')))

    # ----------------------------------------------------------------------
    #  Raggruppamento incrementale (adattato da TagLab detectCoursesIncremental)
    # ----------------------------------------------------------------------
    @staticmethod
    def _detect_courses(items, y_tol_f, ytb_tol_f, h_tol_f, x_gap_f):
        """
        items: lista di dict con chiavi cx, cy, w, h, idx.
               Convenzione coordinate mappa, Y verso l'ALTO:
                 top    = cy + h/2   (bordo superiore)
                 bottom = cy - h/2   (bordo inferiore)
        Ritorna una lista di corsi; ogni corso e' una lista di item, ordinata
        per X crescente.
        """
        unassigned = list(items)
        courses = []

        while unassigned:
            # nuovo corso: parte dal pezzo piu' a sinistra
            unassigned.sort(key=lambda b: b['cx'])
            first = unassigned.pop(0)
            course = [first]

            while unassigned:
                last = course[-1]
                last_y = last['cy']
                last_h = last['h']
                last_x = last['cx']
                last_top = last['cy'] + last['h'] / 2.0
                last_bottom = last['cy'] - last['h'] / 2.0

                if last_h <= 0:
                    # altezza non valida: niente tolleranze sensate, chiudi corso
                    break

                y_tol = last_h * y_tol_f
                ytb_tol = last_h * ytb_tol_f
                avg_w = sum(b['w'] for b in course) / len(course)
                x_gap_tol = avg_w * x_gap_f

                best = None
                for b in unassigned:
                    # solo pezzi a DESTRA dell'ultimo
                    if b['cx'] <= last_x:
                        continue
                    # gap in X non troppo grande
                    if (b['cx'] - last_x) > x_gap_tol:
                        continue
                    # continuita' del centroide Y
                    if abs(b['cy'] - last_y) > y_tol:
                        continue
                    # continuita' dei bordi alto e basso
                    b_top = b['cy'] + b['h'] / 2.0
                    b_bottom = b['cy'] - b['h'] / 2.0
                    if abs(b_top - last_top) > ytb_tol:
                        continue
                    if abs(b_bottom - last_bottom) > ytb_tol:
                        continue
                    # somiglianza di altezza
                    if last_h <= 0:
                        continue
                    ratio = b['h'] / last_h
                    if not ((1.0 - h_tol_f) <= ratio <= (1.0 + h_tol_f)):
                        continue
                    # primo compatibile a destra: greedy, lo prendo subito
                    best = b
                    break

                if best is None:
                    break
                course.append(best)
                unassigned.remove(best)

            courses.append(course)

        # ordina i pezzi di ogni corso per X
        for c in courses:
            c.sort(key=lambda b: b['cx'])

        # ordina i corsi: dal basso verso l'alto (Y crescente), con
        # quantizzazione della quota per raggruppare corsi allo stesso livello,
        # poi da sinistra a destra entro lo stesso livello.
        if courses:
            avg_h = sum(
                (sum(b['h'] for b in c) / len(c)) for c in courses
            ) / len(courses)
            y_q = avg_h * 0.5
        else:
            y_q = 0.0

        def sort_key(c):
            cy = sum(b['cy'] for b in c) / len(c)
            min_x = min(b['cx'] - b['w'] / 2.0 for b in c)
            bucket = int(cy / y_q) if y_q > 0 else cy
            return (bucket, min_x)

        courses.sort(key=sort_key)
        return courses

    @staticmethod
    def _inclination_deg(course):
        """Inclinazione del corso: fit y = m x + b sui centroidi, angolo in
        gradi. Y verso l'alto: positivo = corso che sale verso destra.
        Ritorna 0.0 per corsi con meno di 2 pezzi."""
        if len(course) < 2:
            return 0.0
        xs = np.array([b['cx'] for b in course], dtype=float)
        ys = np.array([b['cy'] for b in course], dtype=float)
        # se tutti i centroidi hanno la stessa X il fit e' degenere
        if np.ptp(xs) < 1e-12:
            return 90.0 if np.ptp(ys) > 0 else 0.0
        slope = np.polyfit(xs, ys, 1)[0]
        return math.degrees(math.atan(slope))

    @staticmethod
    def _joint_stagger(joints_lower, joints_upper, avg_w):
        """Sfalsamento medio dei giunti verticali tra due corsi adiacenti.

        Per ogni giunto del corso inferiore misura la distanza orizzontale dal
        giunto piu' vicino del corso superiore, la normalizza sulla larghezza
        media dei pezzi e la riporta alla fase entro un passo [0, 0.5]:
          ~0   = giunti allineati (ammorsatura assente: possibile cesura /
                 giunto passante tra settori o fasi);
          ~0.5 = sfalsamento di mezzo pezzo (ammorsatura regolare).
        Ritorna None se uno dei due corsi non ha giunti (corsi di 1 pezzo).
        """
        if not joints_lower or not joints_upper or avg_w <= 0:
            return None
        up = np.asarray(joints_upper, dtype=float)
        vals = []
        for jx in joints_lower:
            d = np.min(np.abs(up - jx)) / avg_w   # distanza in frazioni di passo
            frac = d - math.floor(d)              # fase entro un passo [0,1)
            if frac > 0.5:
                frac = 1.0 - frac                 # simmetria: 0.5 = max sfalsamento
            vals.append(frac)
        return float(np.mean(vals))

    # ----------------------------------------------------------------------
    #  Change-point detection sulla serie ordinata dei corsi (discontinuita')
    # ----------------------------------------------------------------------
    @staticmethod
    def _changepoints(signal, penalty, feedback=None):
        """Trova i punti di cambio in una serie 1D ordinata (dal basso verso
        l'alto). 'signal' puo' essere (N,) o (N,k) per il caso multivariato.

        Usa ruptures.Pelt (modello a media/varianza costante a tratti) se la
        libreria e' disponibile; altrimenti ricade su una binary segmentation
        interna in pure-numpy con criterio di guadagno penalizzato.

        Ritorna la lista (ordinata) degli indici di INIZIO di ogni nuovo
        segmento dopo il primo, cioe' le posizioni delle cesure (1 <= bkp < N).
        """
        x = np.asarray(signal, dtype=float)
        if x.ndim == 1:
            x = x.reshape(-1, 1)
        N = x.shape[0]
        if N < 4:
            return []
        # normalizzazione per colonna (z-score) cosi' la penalita' e' comparabile
        mu = np.nanmean(x, axis=0)
        sd = np.nanstd(x, axis=0)
        sd[sd < 1e-12] = 1.0
        xz = (x - mu) / sd

        # tentativo con ruptures (PELT). Si usa il modello 'l2' (costo = somma
        # degli scarti quadratici dalla media), lo STESSO criterio del fallback
        # interno: cosi' la penalita' ha significato equivalente con o senza
        # ruptures. La penalita' e' scalata come penalty*log(N) per coerenza e
        # indipendenza dalla lunghezza della serie.
        try:
            import ruptures as rpt
            pen_eff = float(penalty) * math.log(max(N, 2))
            algo = rpt.Pelt(model='l2', min_size=2, jump=1).fit(xz)
            bkps = algo.predict(pen=pen_eff)
            # ruptures include N come ultimo breakpoint: lo si toglie
            return [b for b in bkps if 0 < b < N]
        except Exception as e:
            if feedback is not None:
                feedback.pushInfo(
                    "ruptures non disponibile (%s): uso il rilevatore interno "
                    "(binary segmentation)." % type(e).__name__)
            return CourseAnalysis._binseg(xz, float(penalty))

    @staticmethod
    def _seg_cost(x):
        """Costo di un segmento = somma degli scarti quadratici dalla media
        (per colonna, sommata). 0 per segmenti costanti."""
        if x.shape[0] == 0:
            return 0.0
        return float(np.sum((x - x.mean(axis=0)) ** 2))

    @staticmethod
    def _binseg(xz, penalty, min_size=2):
        """Binary segmentation in pure-numpy. Divide ricorsivamente la serie
        nel punto che massimizza la riduzione di costo (varianza), accettando
        la divisione solo se il guadagno supera la penalita'. La penalita'
        effettiva e' scalata come penalty * k * log(N) (criterio tipo BIC su
        dati gia' standardizzati, varianza ~1): cosi' su serie di puro rumore
        il guadagno casuale non supera la soglia, e il parametro 'penalty'
        resta indipendente dalla lunghezza della serie."""
        N, k = xz.shape
        pen = penalty * k * math.log(max(N, 2))
        bkps = set()

        def recurse(a, b):
            seg = xz[a:b]
            if seg.shape[0] < 2 * min_size:
                return
            base = CourseAnalysis._seg_cost(seg)
            best_gain = 0.0
            best_t = -1
            for t in range(a + min_size, b - min_size + 1):
                gain = base - (CourseAnalysis._seg_cost(xz[a:t])
                               + CourseAnalysis._seg_cost(xz[t:b]))
                if gain > best_gain:
                    best_gain = gain
                    best_t = t
            if best_t > 0 and best_gain > pen:
                bkps.add(best_t)
                recurse(a, best_t)
                recurse(best_t, b)

        recurse(0, N)
        return sorted(bkps)

    @staticmethod
    def _segments_from_bkps(n, bkps):
        """Assegna a ciascuno degli n elementi (ordinati) un id di segmento
        1-based, dai breakpoint (indici di inizio dei nuovi segmenti)."""
        labels = np.ones(n, dtype=int)
        seg = 1
        bset = set(bkps)
        for i in range(n):
            if i in bset:
                seg += 1
            labels[i] = seg
        return labels

    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        f_id = self.parameterAsString(parameters, self.FIELD_ID, context)
        f_len = self.parameterAsString(parameters, self.FIELD_LEN, context)
        f_hgt = self.parameterAsString(parameters, self.FIELD_HGT, context)
        y_tol_f = self.parameterAsDouble(parameters, self.Y_TOL, context)
        ytb_tol_f = self.parameterAsDouble(parameters, self.YTB_TOL, context)
        h_tol_f = self.parameterAsDouble(parameters, self.H_TOL, context)
        x_gap_f = self.parameterAsDouble(parameters, self.X_GAP, context)
        do_joints = self.parameterAsBool(parameters, self.DO_JOINTS, context)
        do_days = self.parameterAsBool(parameters, self.DO_DAYS, context)
        days_series = self.parameterAsInt(parameters, self.DAYS_SERIES, context)
        days_pen = self.parameterAsDouble(parameters, self.DAYS_PEN, context)
        # il rilevamento delle discontinuita' sui letti/sfalsamento richiede
        # l'analisi dei giunti: se l'utente chiede una serie che dipende da quei
        # campi ma non ha attivato i giunti, li attiviamo implicitamente.
        if do_days and days_series in (0, 2, 3, 4) and not do_joints:
            do_joints = True
            feedback.pushInfo(
                "Il segnale scelto richiede l'analisi dei giunti: "
                "attivata automaticamente.")

        # --- lettura dati ---
        feats = list(source.getFeatures())
        n = len(feats)
        if n < 2:
            raise Exception("Servono almeno 2 componenti per l'analisi dei corsi.")

        items = []
        for i, ft in enumerate(feats):
            try:
                w = float(ft[f_len])
                h = float(ft[f_hgt])
            except (TypeError, ValueError):
                w = h = float('nan')
            c = ft.geometry().centroid().asPoint()
            items.append({
                'cx': c.x(), 'cy': c.y(),
                'w': w, 'h': h,
                'idx': i, 'fid': ft[f_id],
            })

        # scarta i componenti senza dimensioni valide (non raggruppabili)
        valid = [it for it in items if not (math.isnan(it['w']) or math.isnan(it['h']))]
        n_skip = n - len(valid)
        if n_skip:
            feedback.pushWarning(
                "%d componenti privi di dimensioni valide: esclusi dai corsi "
                "(corso_id = NULL)." % n_skip)
        if len(valid) < 2:
            raise Exception("Meno di 2 componenti con dimensioni valide.")

        # --- riconoscimento corsi ---
        feedback.pushInfo("Riconoscimento corsi in corso...")
        courses = self._detect_courses(valid, y_tol_f, ytb_tol_f, h_tol_f, x_gap_f)
        feedback.pushInfo("Trovati %d corsi (su %d componenti validi)." % (
            len(courses), len(valid)))

        # --- mappa idx -> (corso_id, pos_in_corso) e metadati per corso ---
        course_of = {}      # idx componente -> corso_id (1-based, dal basso)
        pos_of = {}         # idx componente -> posizione nel corso (1-based, da sx)
        joint_of = {}       # idx componente -> giunto verticale verso il pezzo a destra
        course_meta = []    # lista di dict di sintesi per corso

        for ci, course in enumerate(courses, start=1):
            hs = [b['h'] for b in course]
            ws = [b['w'] for b in course]
            cys = [b['cy'] for b in course]
            xs_left = [b['cx'] - b['w'] / 2.0 for b in course]
            xs_right = [b['cx'] + b['w'] / 2.0 for b in course]

            quota = float(np.mean(cys))
            alt = float(np.median(hs))            # altezza rappresentativa (mediana)
            lung = float(max(xs_right) - min(xs_left))
            incl = self._inclination_deg(course)

            for pos, b in enumerate(course, start=1):
                course_of[b['idx']] = ci
                pos_of[b['idx']] = pos

            # giunto verticale (di testa) tra pezzi contigui dello stesso corso:
            # spazio libero tra il bordo destro di un pezzo e il bordo sinistro
            # del successivo. L'ultimo pezzo del corso non ha pezzo a destra.
            # Si memorizzano anche le posizioni X dei giunti (punto medio del gap)
            # per il calcolo dello sfalsamento tra corsi.
            joint_xs = []
            if do_joints:
                for pp in range(len(course)):
                    b = course[pp]
                    if pp + 1 < len(course):
                        nb = course[pp + 1]
                        right_b = b['cx'] + b['w'] / 2.0
                        left_nb = nb['cx'] - nb['w'] / 2.0
                        gap = left_nb - right_b
                        joint_of[b['idx']] = float(gap)
                        joint_xs.append((right_b + left_nb) / 2.0)
                    else:
                        joint_of[b['idx']] = None  # ultimo pezzo del corso

            course_meta.append({
                'corso_id': ci,
                'n_pezzi': len(course),
                'quota_media': quota,
                'altezza_corso': alt,
                'lunghezza_corso': lung,
                'inclinaz_deg': incl,
                # bordi rappresentativi per il calcolo del letto di malta
                '_sup': quota + alt / 2.0,
                '_inf': quota - alt / 2.0,
                # posizioni X dei giunti verticali e larghezza media (per ammorsatura)
                '_joint_xs': joint_xs,
                '_avg_w': float(np.mean(ws)),
            })

        # --- analisi dei giunti tra corsi (opzionale) ---
        # I corsi sono gia' ordinati dal basso verso l'alto in course_meta.
        if do_joints:
            for k in range(len(course_meta)):
                if k + 1 < len(course_meta):
                    sopra = course_meta[k + 1]
                    # letto di malta orizzontale verso il corso superiore
                    letto = sopra['_inf'] - course_meta[k]['_sup']
                    course_meta[k]['letto_malta_sup'] = float(letto)
                    # sfalsamento dei giunti verticali rispetto al corso superiore
                    course_meta[k]['sfalso_giunti_sup'] = self._joint_stagger(
                        course_meta[k]['_joint_xs'], sopra['_joint_xs'],
                        course_meta[k]['_avg_w'])
                else:
                    course_meta[k]['letto_malta_sup'] = None    # ultimo corso
                    course_meta[k]['sfalso_giunti_sup'] = None
            neg = sum(1 for c in course_meta
                      if c.get('letto_malta_sup') is not None and c['letto_malta_sup'] < 0)
            if neg:
                feedback.pushInfo(
                    "Nota: %d corsi hanno letto_malta_sup negativo (sovrapposizione "
                    "verticale dei corsi: zone irregolari, rincocci o assegnazioni "
                    "di corso da verificare)." % neg)

        # --- rilevamento delle discontinuita' (change-point sui corsi) ---
        # default: ogni corso appartiene al segmento 1, nessuna cesura.
        for c in course_meta:
            c['segmento'] = 1
            c['cesura'] = 0
        if do_days and len(course_meta) >= 4:
            # costruisci la serie ordinata (course_meta e' gia' dal basso in alto)
            def col(key):
                return [c.get(key) for c in course_meta]
            if days_series == 1:
                raw = [[v] for v in col('altezza_corso')]
                label = 'altezza_corso'
            elif days_series == 2:
                raw = [[v] for v in col('sfalso_giunti_sup')]
                label = 'sfalso_giunti_sup'
            elif days_series == 3:
                raw = [[a, b] for a, b in zip(col('letto_malta_sup'),
                                              col('sfalso_giunti_sup'))]
                label = 'letto + sfalsamento'
            elif days_series == 4:
                raw = [[a, b, h] for a, b, h in zip(col('letto_malta_sup'),
                                                    col('sfalso_giunti_sup'),
                                                    col('altezza_corso'))]
                label = 'letto + sfalsamento + altezza'
            else:
                raw = [[v] for v in col('letto_malta_sup')]
                label = 'letto_malta_sup'

            # i campi di giunto sono NULL sull'ultimo corso (e su eventuali corsi
            # di 1 pezzo per lo sfalsamento): si considera solo il prefisso di
            # corsi con valori tutti validi, su cui il change-point e' definito.
            valid_len = len(raw)
            for i, row in enumerate(raw):
                if any(v is None or (isinstance(v, float) and math.isnan(v)) for v in row):
                    valid_len = i
                    break
            if valid_len >= 4:
                sig = np.array(raw[:valid_len], dtype=float)
                bkps = self._changepoints(sig, days_pen, feedback)
                labels = self._segments_from_bkps(valid_len, bkps)
                for i in range(valid_len):
                    course_meta[i]['segmento'] = int(labels[i])
                    course_meta[i]['cesura'] = 1 if i in set(bkps) else 0
                # i corsi di coda senza segnale valido ereditano l'ultimo segmento
                last_seg = int(labels[-1]) if valid_len > 0 else 1
                for i in range(valid_len, len(course_meta)):
                    course_meta[i]['segmento'] = last_seg
                    course_meta[i]['cesura'] = 0

                nseg = len(set(c['segmento'] for c in course_meta))
                feedback.pushInfo(
                    "Discontinuita' (segnale: %s): %d cesure -> %d segmenti."
                    % (label, len(bkps), nseg))
                # statistica per segmento
                for s in sorted(set(c['segmento'] for c in course_meta)):
                    membri = [c for c in course_meta if c['segmento'] == s]
                    vals = [c.get('letto_malta_sup') for c in membri
                            if c.get('letto_malta_sup') is not None]
                    if len(vals) >= 2:
                        mu = float(np.mean(vals)); sd = float(np.std(vals, ddof=1))
                        cv = sd / mu if abs(mu) > 1e-12 else float('nan')
                        feedback.pushInfo(
                            "  segmento %d: %d corsi, letto medio=%.4f CV=%.3f"
                            % (s, len(membri), mu, cv))
                    else:
                        feedback.pushInfo(
                            "  segmento %d: %d corsi" % (s, len(membri)))
            else:
                feedback.pushInfo(
                    "Rilevamento discontinuita' saltato: meno di 4 corsi con segnale valido.")
        elif do_days:
            feedback.pushInfo(
                "Rilevamento discontinuita' saltato: servono almeno 4 corsi.")

        # ===== OUTPUT 1: componenti con corso =====
        out_fields = QgsFields()
        for fld in source.fields():
            out_fields.append(fld)
        existing = [f.name() for f in out_fields]
        new_comp = [('corso_id', QVariant.Int),
                    ('pos_in_corso', QVariant.Int),
                    ('corso_n_pezzi', QVariant.Int)]
        if do_joints:
            new_comp.append(('giunto_vert', QVariant.Double))
        if do_days:
            new_comp.append(('segmento', QVariant.Int))
        for nm, tp in new_comp:
            if nm in existing:
                feedback.pushWarning("Campo '%s' gia' presente: verra' duplicato." % nm)
            out_fields.append(QgsField(nm, tp))

        (sink, dest_id) = self.parameterAsSink(
            parameters, self.OUTPUT, context, out_fields,
            source.wkbType(), source.sourceCrs())

        seg_by_course = {c['corso_id']: c['segmento'] for c in course_meta}
        n_pezzi_by_course = {c['corso_id']: c['n_pezzi'] for c in course_meta}
        for i, ft in enumerate(feats):
            g = QgsFeature(out_fields)
            g.setGeometry(ft.geometry())
            cid = course_of.get(i)
            pos = pos_of.get(i)
            npz = n_pezzi_by_course.get(cid) if cid is not None else None
            attrs = list(ft.attributes()) + [
                int(cid) if cid is not None else None,
                int(pos) if pos is not None else None,
                int(npz) if npz is not None else None,
            ]
            if do_joints:
                gv = joint_of.get(i)
                attrs.append(float(gv) if gv is not None else None)
            if do_days:
                seg = seg_by_course.get(cid) if cid is not None else None
                attrs.append(int(seg) if seg is not None else None)
            g.setAttributes(attrs)
            sink.addFeature(g, QgsFeatureSink.FastInsert)
            if n:
                feedback.setProgress(int(60.0 * i / n))

        # ===== OUTPUT 2: sintesi per corso =====
        cfields = QgsFields()
        cfields.append(QgsField('corso_id', QVariant.Int))
        cfields.append(QgsField('n_pezzi', QVariant.Int))
        cfields.append(QgsField('quota_media', QVariant.Double, len=12, prec=4))
        cfields.append(QgsField('altezza_corso', QVariant.Double, len=12, prec=4))
        cfields.append(QgsField('lunghezza_corso', QVariant.Double, len=12, prec=4))
        cfields.append(QgsField('inclinaz_deg', QVariant.Double, len=10, prec=3))
        if do_joints:
            cfields.append(QgsField('letto_malta_sup', QVariant.Double, len=12, prec=4))
            cfields.append(QgsField('sfalso_giunti_sup', QVariant.Double, len=8, prec=3))
        if do_days:
            cfields.append(QgsField('segmento', QVariant.Int))
            cfields.append(QgsField('cesura', QVariant.Int))

        (csink, cdest_id) = self.parameterAsSink(
            parameters, self.OUTPUT_COURSES, context, cfields,
            QgsWkbTypes.NoGeometry)

        for c in course_meta:
            f = QgsFeature(cfields)
            attrs = [
                int(c['corso_id']), int(c['n_pezzi']),
                float(c['quota_media']), float(c['altezza_corso']),
                float(c['lunghezza_corso']), float(c['inclinaz_deg']),
            ]
            if do_joints:
                attrs.append(c['letto_malta_sup'])
                attrs.append(c['sfalso_giunti_sup'])
            if do_days:
                attrs.append(int(c['segmento']))
                attrs.append(int(c['cesura']))
            f.setAttributes(attrs)
            csink.addFeature(f, QgsFeatureSink.FastInsert)

        feedback.pushInfo("Analisi dei corsi completata.")
        return {self.OUTPUT: dest_id, self.OUTPUT_COURSES: cdest_id}
