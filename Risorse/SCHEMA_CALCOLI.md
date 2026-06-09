# Schema dei calcoli — Statistiche avanzate & Analisi dei corsi

Riferimento sintetico di **tutti i valori calcolati** dai due script della suite
MensioAnalysisTools, con spiegazione e caso d'uso archeologico per ciascuno.

I due strumenti rispondono a domande opposte e complementari:

| | Statistiche avanzate | Analisi dei corsi |
|---|---|---|
| **Domanda** | *quali pezzi sono anomali?* (reimpiego) | *dove cambia la costruzione?* (giornate) |
| **Logica** | outlier in una **nuvola** (ignora la posizione) | rotture in una **sequenza** (rispetta l'ordine) |
| **Metodo di gruppo** | clustering gerarchico di Ward | change-point detection (PELT) |
| **Input** | componenti con dimensioni + angolo + area | componenti dimensionati di un rilievo raddrizzato |

---

# PARTE 1 — Statistiche avanzate (pattern e reimpiego)

Obiettivo: individuare elementi di **reimpiego (spolia)** e pattern di posa,
incrociando indizi di forma, dimensione, orientamento, posizione spaziale e
(opzionale) modulo metrologico. Lavora su una nuvola di componenti senza ordine.

## A. Analisi del paramento (sempre attiva)

### `R_fill` — fattore di riempimento
- **Calcolo:** `area_reale / (lunghezza × spessore)`. Quanto il pezzo riempie il
  suo ingombro rettangolare.
- **Valori:** ≈1 = pezzo squadrato; basso = irregolare, scheggiato, obliquo.
- **Caso d'uso:** un mattone di reimpiego scheggiato ha R_fill ≈ 0,67 contro ≈
  0,98 dei pezzi integri → forma anomala, candidato al riuso.

### `mahal` — distanza di Mahalanobis
- **Calcolo:** distanza dal centroide della nuvola su lunghezza+spessore+area+
  R_fill standardizzati, pesata con l'inversa della covarianza (considera le
  variabili **insieme** e correlate).
- **Valori:** relativi; alto = combinazione dimensionale insolita.
- **Caso d'uso:** un pezzo 25×5,5 cm in mezzo a mattoni 29×4,3 cm spicca per
  `mahal` anche se nessuna singola misura è estrema → outlier dimensionale.

### `PC1`, `PC2` — componenti principali
- **Calcolo:** PCA sulle 4 variabili lineari; PC1 ≈ taglia generale, PC2 ≈
  forma/proporzione.
- **Valori:** coordinate in spazio ridotto, si leggono come scatter PC1–PC2.
- **Caso d'uso:** i reimpieghi si staccano dalla nuvola principale, tipicamente
  lungo PC2 (forma diversa) → diagramma colorato per `reuse_score`.

### `dev_glob` — scarto angolare dalla media globale (0–90°)
- **Calcolo:** differenza **assiale** tra l'orientamento del pezzo e
  l'orientamento medio dell'intero paramento.
- **Valori:** 0–5° regolare; >15–20° nettamente fuori asse.
- **Caso d'uso:** `dev_glob` alto ma `dev_loc` basso = il pezzo segue i suoi
  vicini ma non il paramento → settore/corso ruotato, non anomalia isolata.

### `dev_loc_rad`, `dev_loc_knn` — scarto angolare locale (0–90°)
- **Calcolo:** differenza assiale tra il pezzo e la media dei suoi vicini, con
  due definizioni di vicinato: raggio fisso (`rad`) e k-nearest (`knn`).
- **Valori:** alto = il pezzo è fuori asse rispetto a chi gli sta intorno.
- **Caso d'uso:** `dev_loc` alto = anomalia di posa locale vera (rattoppo,
  reimpiego). Dove `rad` e `knn` divergono c'è un effetto di densità/pezzatura.

### `disp_loc_rad`, `disp_loc_knn` — dispersione circolare locale (0–1)
- **Calcolo:** `1 − R̄` sugli orientamenti dei vicini. Quanto è disordinato
  l'intorno di ogni pezzo.
- **Valori:** ≈0 intorno ordinato; ≈1 intorno caotico.
- **Caso d'uso:** una **mappa** di questo campo evidenzia le zone di disordine
  (tamponature, rifacimenti) a prescindere dal singolo pezzo.

### `n_rad` — numero di vicini (raggio fisso)
- **Calcolo:** conteggio dei componenti entro il raggio.
- **Valori:** diagnostico di densità/pezzatura.
- **Caso d'uso:** un'area con `n_rad` anomalo = cambio di pezzatura (es. rappezzo
  di mattoni piccoli in muratura di blocchi).

### `cluster` — clustering gerarchico (Ward)
- **Calcolo:** `AgglomerativeClustering`/`linkage` di Ward sulle variabili
  lineari standardizzate + scarto angolare locale. Numero di cluster fissato o
  stimato (taglio del dendrogramma al 70% dell'altezza max). **Ignora posizione
  e ordine: raggruppa per sola somiglianza.**
- **Valori:** etichetta intera senza ordine (0, 1, 2…).
- **Caso d'uso:** cluster grande omogeneo = muratura coerente; cluster piccolo a
  CV alto = gruppo di reimpiego o fase diversa. È lo strumento per il **reimpiego
  diffuso** (pezzi sparsi ma dimensionalmente simili tra loro).

### CV — coefficiente di variazione (solo nel log)
- **Calcolo:** `stddev/media`, globale e **per cluster**, su lunghezza, spessore,
  area, R_fill.
- **Valori:** basso (0,01–0,03) = standardizzato; alto (>0,10) = eterogeneo.
- **Caso d'uso:** il cluster con CV 10× più alto del principale è il gruppo di
  reimpiego → conferma quantitativa del cluster anomalo.

### `reuse_score` — indicatore sintetico (0–1)
- **Calcolo:** media dei **ranghi percentili** degli indizi: basso R_fill + alto
  Mahalanobis + alto scarto angolare (3 indizi, mattoni); + alto scarto modulare
  (4 indizi, altri componenti).
- **Valori:** lettura per ranghi — <0,5 tipico, 0,5–0,7 da osservare, >0,7
  sospetto.
- **Caso d'uso:** ordina i pezzi per `reuse_score` decrescente → lista dei
  candidati al riuso. È **relativo al campione** (un rango), non una prova.

### `lisa_I`, `lisa_p`, `lisa_clust` — autocorrelazione spaziale (LISA)
- **Calcolo:** Local Moran's I sul `reuse_score` con significatività per
  permutazione (default 999). Classi: HH, LL, HL, LH, ns.
- **Valori:** HH = hotspot (sospetto tra sospetti); LL = zona sana; HL = sospetto
  isolato; LH = sano in zona disturbata.
- **Caso d'uso:** gruppo compatto di **HH** = tamponatura/rifacimento (reimpiego
  **concentrato**); **HL** sparsi = spolia occasionali. Complementare al
  clustering: LISA = concentrato, cluster = diffuso.

## B. Analisi metrologica (opzionale, solo "altri componenti")

### `w_phase`, `h_phase` — fase modulare (0–1)
- **Calcolo:** posizione di larghezza/altezza entro il modulo (resto circolare).
- **Valori:** ≈0 (o ≈1) conforme a un multiplo intero; ≈0,5 a metà tra due
  multipli (non conforme).
- **Caso d'uso:** un blocco con `w_phase` ≈ 0,5 non rispetta il modulo testato.

### `w_resid`, `h_resid` — scarto dal modulo (metri)
- **Calcolo:** scarto con segno dal multiplo di modulo più vicino.
- **Valori:** ≈0 modulare; grande = fuori modulo.
- **Caso d'uso:** con modulo 0,297 m, un blocco da 0,52 m ha `w_resid` ≈ −0,074 m
  (7,4 cm fuori) → fortemente sospetto di provenienza diversa.

### Valori nel log metrologico
- **R̄ + Rayleigh** per dimensione: aderenza al modulo dato e sua significatività.
- **Cosine quantogram di Kendall:** cerca il modulo che meglio spiega le misure
  (picco di Φ). Caso d'uso: picco netto a 0,297 = piede romano; picco intermedio
  = due produzioni mescolate (reimpiego).
- **Validazione Monte Carlo:** stabilisce se il picco è reale o casuale (p<0,05 /
  p<0,01).
- **Guardia di scala:** esclude le dimensioni < 1 modulo, non informative
  (evita falsi positivi sui ritagli sottili).

---

# PARTE 2 — Analisi dei corsi del paramento

Obiettivo: ricostruire i **corsi** (filari) di un paramento raddrizzato e
leggerne la regolarità, fino a individuare le **discontinuità costruttive**
(giornate, riprese, lotti di materiale). Lavora su una sequenza ordinata.

## A. Riconoscimento dei corsi (sempre attivo)

### `corso_id` — filare di appartenenza
- **Calcolo:** raggruppamento incrementale "a catena" (logica TagLab): si parte
  dal pezzo più a sinistra e si estende a destra agganciando il primo pezzo
  compatibile per gap, continuità di quota, allineamento dei bordi e somiglianza
  di altezza. Corsi numerati **dal basso verso l'alto**.
- **Valori:** intero ≥1 (1 = corso più basso); nullo se il pezzo non ha
  dimensioni valide.
- **Caso d'uso:** colorare i componenti per `corso_id` per leggere la tessitura;
  base per ogni analisi successiva di giornata/fase.

### `pos_in_corso` — posizione nel filare
- **Calcolo:** ordine del pezzo nel corso, da sinistra.
- **Caso d'uso:** ricostruire la sequenza di posa lungo un corso; localizzare un
  pezzo specifico.

### `corso_n_pezzi` — numero di pezzi del corso
- **Caso d'uso:** corsi con pochissimi pezzi sono spesso frammenti o corsi
  spezzati dall'algoritmo (da rivedere con `x_gap_factor`).

### `quota_media`, `altezza_corso`, `lunghezza_corso` — descrittori del corso (metri)
- **Calcolo:** rispettivamente la Y media dei centroidi, l'altezza
  rappresentativa (mediana delle altezze dei pezzi) e l'estensione orizzontale
  del corso. Sono nella tabella di sintesi per corso.
- **Caso d'uso:** `altezza_corso` confronta la pezzatura tra filari (un cambio
  segnala un altro lotto di materiale); `quota_media` ordina i corsi e alimenta
  il calcolo del letto di malta; `lunghezza_corso` misura l'estensione conservata
  del filare.

### `inclinaz_deg` — inclinazione del corso (gradi)
- **Calcolo:** fit ai minimi quadrati `y = m·x + b` sui centroidi; angolo
  `atan(m)`. + = sale verso destra.
- **Valori:** ±2° orizzontale; oltre ±5° nettamente inclinato.
- **Caso d'uso:** un cambio brusco di inclinazione tra corsi vicini segnala
  cedimenti o un giunto di ripresa.

## B. Analisi dei giunti (opzionale, flag attivo di default)

### `letto_malta_sup` — letto di malta orizzontale (metri, per corso)
- **Calcolo:** `bordo_inf(corso sopra) − bordo_sup(corso k)`, da quota media e
  altezza mediana del corso.
- **Valori:** spessore del giunto di allettamento; negativo = corsi sovrapposti
  (irregolarità). Ultimo corso = nullo.
- **Caso d'uso:** la **serie** letta dal basso verso l'alto è la firma della
  cadenza costruttiva; i salti sono i candidati alle **giornate di lavoro**.

### `giunto_vert` — giunto verticale di testa (metri, per pezzo)
- **Calcolo:** spazio libero verso il pezzo a destra nello stesso corso.
- **Valori:** spessore del giunto verticale; negativo = pezzi a contatto/serrati.
- **Caso d'uso:** una **colonna** verticale di giunti anomali su più corsi =
  cesura costruttiva tra settori.

### `sfalso_giunti_sup` — ammorsatura (0–0,5, per corso)
- **Calcolo:** sfalsamento medio dei giunti verticali rispetto al corso sopra,
  in frazioni di passo.
- **Valori:** ≈0,5 ammorsatura regolare (mattone copre il giunto sotto); ≈0
  giunti allineati.
- **Caso d'uso:** un crollo verso 0 su più corsi = **cesura verticale** (settori
  affiancati, tamponatura) — ciò che la sola analisi dei letti non vedrebbe.

## C. Rilevamento delle discontinuità (opzionale, flag attivo di default)

### `segmento` — tratto costruttivo omogeneo
- **Calcolo:** **change-point detection** (PELT di `ruptures`, o fallback numpy
  equivalente) sulla serie ordinata dei corsi. Segnale selezionabile: letto di
  malta (default con sfalsamento), altezza, sfalsamento, o multivariato. **NON è
  un clustering: divide una sequenza ordinata in tratti contigui.**
- **Valori:** intero dal basso; ogni segmento è un blocco di corsi consecutivi.
- **Caso d'uso:** colorare i componenti per `segmento` per leggere le presunte
  **giornate/fasi** sulla mappa. È lo strumento per *segmentare la produzione*.

### `cesura` — confine di segmento (0/1)
- **Calcolo:** 1 sul primo corso di ogni nuovo segmento (dove cade la rottura).
- **Caso d'uso:** localizza i candidati **giunti di giornata, riprese o cambi di
  lotto**. Solido quando converge con un salto di `letto_malta_sup`, un crollo di
  `sfalso_giunti_sup` o un cambio di `inclinaz_deg`.

### Valori nel log
- numero di corsi riconosciuti, corsi con letto negativo;
- segnale usato, numero di cesure e segmenti, e per segmento: n. corsi, letto
  medio e CV.

---

# Pattern di posa vs riconoscimento dei filari

I due script sembrano sovrapporsi sul tema della "posa", ma misurano due cose
geometricamente **indipendenti**. È la chiave per capire perché non sono
intercambiabili.

## Due nozioni diverse di "posa"

- **Analisi corsi** ricostruisce la **struttura topologica**: chi sta accanto a
  chi, chi sta sopra a chi. È un problema di *adiacenza e connessione*. Risponde
  a "come sono organizzati i pezzi nello spazio del muro".
- **Statistiche avanzate** misura la **coerenza direzionale**: quanto sono
  allineati tra loro gli assi di posa. È un problema di *direzione*. Risponde a
  "i pezzi guardano tutti nella stessa direzione".

Sono assi indipendenti: un muro può avere corsi nettissimi (struttura ordinata)
ma pezzi ruotati dentro i corsi (direzione incoerente), e viceversa.

## Come l'analisi corsi *riconosce* un filare

Il filare non è misurato, è **costruito per adiacenza**. L'algoritmo non calcola
una statistica e poi decide: segue fisicamente la fila, agganciando il pezzo a
destra se passa i quattro test di vicinato (gap, quota, bordi, altezza). Il
"pattern" è **emergente e locale**, nasce dal concatenarsi di decisioni di
adiacenza, e il risultato è un'**appartenenza discreta** (`corso_id`): un fatto
topologico, non un grado di qualità.

> In una frase: l'analisi corsi **non coglie un pattern, lo segue**. È un
> tracciatore di file, non un misuratore di regolarità.

## Come le statistiche avanzate *colgono* un pattern di posa

Qui il pattern è una **grandezza misurata**, di natura *circolare* perché
riguarda gli angoli (`angle_bbox`). Si calcola la **coerenza R̄** (vettore medio
degli angoli raddoppiati): R̄→1 = orientamenti concordi (posa ordinata); R̄→0 =
sparsi (disordine). E per ogni pezzo si misura lo **scarto angolare locale**
(`dev_loc`): quanto il suo orientamento devia da quello medio dei vicini.

> Il pattern è colto **per deviazione, non per appartenenza**: il pezzo "è in
> linea o devia" da una direzione dominante — l'opposto logico del "appartiene o
> no" a una fila.

## L'esempio che chiarisce tutto: opus reticulatum

I tasselli sono posati a 45°, in una rete diagonale ordinatissima.

- **Analisi corsi:** *fallisce o dà filari spezzati* — non ci sono file
  orizzontali, la struttura topologica non è a corsi.
- **Statistiche avanzate:** trovano *R̄ altissimo* — tutti i tasselli sono
  concordi nell'orientamento diagonale.

Il pattern di posa è fortissimo; il "corso" non esiste. Due strumenti, due
risposte opposte, entrambe corrette.

All'inverso, un muro a corsi regolari ma con mattoni di reimpiego rimessi un po'
come capita: l'analisi corsi riconosce benissimo i filari (`corso_id` puliti), ma
lo scarto angolare locale delle statistiche avanzate si accende dentro i corsi —
il corso c'è, ma il pattern di posa fine è disturbato (indizio di rilavorazione).

## Pattern vs corso normale, in tabella

| | Analisi corsi | Statistiche avanzate |
|---|---|---|
| **Cosa intende per "posa"** | organizzazione topologica (file) | coerenza direzionale (angoli) |
| **Natura del calcolo** | costruzione per adiacenza | misura statistica circolare |
| **Cosa produce** | appartenenza discreta (`corso_id`) | gradiente continuo (R̄, `dev_loc`) |
| **Coglie il pattern…** | seguendolo (lo traccia) | misurandolo (lo quantifica) |
| **Anomalia =** | pezzo non agganciabile ad alcuna fila | pezzo che devia dalla direzione dei vicini |
| **Caso che lo manda in crisi** | opus reticulatum (nessuna fila) | paramento con un solo pezzo (nessuna direzione media) |

In pratica: l'analisi corsi dà la **griglia** del muro (le righe in cui leggerlo);
le statistiche avanzate dicono **quanto ogni pezzo rispetta la regola** dentro
quella griglia. Per questo si usano in sequenza — vedi sotto.

---

# Quando usare quale

- **Cerchi pezzi estranei (spolia, rattoppi)?** → Statistiche avanzate.
  `reuse_score` + `lisa_clust` per i candidati; `cluster` + CV per i gruppi
  eterogenei.
- **Cerchi l'organizzazione del cantiere (giornate, riprese, fasi)?** → Analisi
  dei corsi. `letto_malta_sup`/`sfalso_giunti_sup` come segnali, `segmento`/
  `cesura` come risultato.
- **Entrambi?** I due si completano: l'analisi dei corsi dà la **struttura
  verticale** (chi ha costruito cosa, quando), le statistiche avanzate dicono
  **quali pezzi** dentro quella struttura sono estranei. Un reimpiego concentrato
  (LISA HH) che cade dentro un singolo `segmento` racconta una storia coerente:
  una ripresa fatta con materiale di recupero.
- **In sequenza (consigliato):** prima l'analisi corsi per ricostruire la
  griglia (`corso_id`), poi le statistiche avanzate. Sapendo a quale corso
  appartiene ogni pezzo, le anomalie di orientamento (`dev_loc`) diventano molto
  più interpretabili: se cadono tutte nello stesso filare indicano una ripresa
  localizzata, se sono sparse indicano reimpiego diffuso.

---

*Schema di riferimento per gli script `statistiche_avanzate_pattern_reimpiego.py`
e `analisi_corsi_paramento.py`, suite MensioAnalysisTools.*
