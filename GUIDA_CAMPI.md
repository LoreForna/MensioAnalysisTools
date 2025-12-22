# Guida ai Campi

Documentazione completa di tutti i campi utilizzati dagli script di analisi quantitativa.

---

## Campi Input Obbligatori

### Layer "campioni"

| Campo | Tipo | Lunghezza | Descrizione | Esempio |
|-------|------|-----------|-------------|---------|
| `fid` | Integer | - | Identificatore univoco del feature | 1, 2, 3... |
| `campione` | String | 50 | Codice identificativo del campione | "C001", "CAMP_A" |
| `sito` | String | 100 | Nome del sito archeologico | "Foro Romano", "Villa Adriana" |
| `ambiente` | String | 100 | Identificativo dell'ambiente analizzato | "AMB1", "Vano Nord" |
| `usm` | String | 50 | Unità Stratigrafica Muraria | "USM100", "US_MUR_01" |
| `area_campione` | Double | 10,3 | Area del campione in m² | 1.000, 0.950 |

**Note**:
- `fid` viene generato automaticamente da QGIS
- `area_campione` deve essere calcolato con field calculator: `$area`
- Tutti i campi stringa sono case-sensitive

---

### Layer "rilievo"

| Campo | Tipo | Lunghezza | Descrizione | Valori Ammessi | Esempio |
|-------|------|-----------|-------------|----------------|---------|
| `fid` | Integer | - | Identificatore univoco del componente | - | 1, 2, 3... |
| `tipo` | String | 50 | Tipologia del materiale | Qualsiasi | "laterizio", "tufo", "travertino" |
| `superficie` | String | 10 | Stato di conservazione | **"intera"** o **"parziale"** | "intera" |
| `area_componente` | Double | 10,3 | Area del componente in m² | - | 0.045 |
| `num_componente` | Integer | - | Numero progressivo nel campione | - | 1, 2, 3... |

**Note critiche**:
- ⚠️ `superficie` deve contenere **esattamente** "intera" o "parziale" (lowercase)
- Solo componenti con `superficie = "intera"` vengono usati per le statistiche dimensionali
- Componenti "parziali" vengono contati ma esclusi dalle misure
- `tipo` può essere NULL se si attiva il parametro "Includi non classificati"

---

## Campi Output - Bbox

Generati dal calcolo del Minimum Oriented Bounding Box.

### Nel layer "Min Oriented Bbox"

| Campo | Tipo | Decimali | Unità | Descrizione |
|-------|------|----------|-------|-------------|
| `width_bbox` | Double | 3 | m | Larghezza del rettangolo minimo orientato |
| `height_bbox` | Double | 3 | m | Altezza del rettangolo minimo orientato |
| `angle_bbox` | Double | 2 | gradi | Angolo di rotazione del rettangolo (0-360°) |
| `area_bbox` | Double | 6 | m² | Area del rettangolo minimo |
| `perimeter_bbox` | Double | 3 | m | Perimetro del rettangolo minimo |

**Formule**:
```python
width_bbox = MAX(lato1, lato2)  # lato più lungo
height_bbox = MIN(lato1, lato2)  # lato più corto
area_bbox = width_bbox * height_bbox
perimeter_bbox = 2 * (width_bbox + height_bbox)
```

**Interpretazione**:
- `width_bbox` rappresenta sempre la dimensione maggiore
- `height_bbox` rappresenta sempre la dimensione minore
- L'angolo indica l'orientamento del componente
- Utile per identificare pattern di posa

---

## Campi Output - Metrologici

**Disponibili solo in**: Componenti a Secco e Altri Componenti

Questi campi analizzano le dimensioni rispetto a un'unità di misura storica (modulo).

### Campi Width (Larghezza)

| Campo | Tipo | Descrizione | Formula | Esempio |
|-------|------|-------------|---------|---------|
| `width_modulo` | Integer | Numero di moduli interi nella larghezza | `floor(width_bbox / @modulo)` | 3 |
| `Δwidth_modulo` | Double (3 dec) | Resto della larghezza in metri | `width_bbox % @modulo` | 0.002 |

### Campi Height (Altezza)

| Campo | Tipo | Descrizione | Formula | Esempio |
|-------|------|-------------|---------|---------|
| `height_modulo` | Integer | Numero di moduli interi nell'altezza | `floor(height_bbox / @modulo)` | 1 |
| `Δheight_modulo` | Double (3 dec) | Resto dell'altezza in metri | `height_bbox % @modulo` | 0.154 |

### Simbolo Δ (Delta)

Il simbolo **Δ** (delta maiuscolo greco) indica una **variazione** o **differenza**.

- `Δwidth_modulo` = quanto "avanza" dopo aver tolto i moduli interi dalla larghezza
- `Δheight_modulo` = quanto "avanza" dopo aver tolto i moduli interi dall'altezza

**Interpretazione pratica**:

```
width_bbox = 0.890 m
modulo = 0.296 m (piede romano)

width_modulo = 3        → "3 piedi interi"
Δwidth_modulo = 0.002   → "più 2 millimetri"

Lettura: "3 piedi e 2 millimetri"
```

### Variabile @modulo

La variabile `@modulo` è una **variabile di layer** che contiene il valore del modulo configurato dall'utente.

- Default: 0.296 m (piede attico/romano)
- Configurabile da interfaccia
- Valori comuni: 0.275m (piede osco), 0.308m (piede greco), 0.326m (piede dorico)

---

## Campi Output - Statistiche

### Tabella "Analisi Campioni"

Campi presenti nella tabella di riepilogo per ogni campione.

#### Identificativi

| Campo | Tipo | Descrizione |
|-------|------|-------------|
| `fid` | Integer | ID campione |
| `sito` | String | Nome sito |
| `usm` | String | Unità stratigrafica |
| `ambiente` | String | Ambiente |
| `campione` | String | Codice campione |
| `area_campione` | Double | Area totale campione |

---

#### Conteggi (Script: Mattoni)

| Campo | Tipo | Descrizione | Formula |
|-------|------|-------------|---------|
| `num_mattoni_interi` | Integer | N° mattoni con superficie intera | COUNT WHERE superficie='intera' |
| `num_mattoni_parziali` | Integer | N° mattoni con superficie parziale | COUNT WHERE superficie='parziale' |
| `num_mattoni_interi_calcolati` | Integer | Equivalenti interi stimati | round(totale_area_mattoni / media_area_mattoni_interi) |
| `totale_mattoni_interi_calcolati` | Integer | Totale equivalenti | num_mattoni_interi + num_mattoni_interi_calcolati |

---

#### Conteggi (Script: Componenti a Secco / Altri)

| Campo | Tipo | Descrizione |
|-------|------|-------------|
| `num_componenti_interi` | Integer | N° componenti con superficie intera |
| `num_componenti_parziali` | Integer | N° componenti con superficie parziale |
| `num_componenti_interi_calcolati` | Integer | Equivalenti interi stimati |
| `totale_componenti_interi_calcolati` | Integer | Totale equivalenti |

---

#### Statistiche Area

| Campo | Tipo | Decimali | Unità | Descrizione |
|-------|------|----------|-------|-------------|
| `totale_area_[tipo]_interi` | Double | 3 | m² | Somma aree componenti interi |
| `media_area_[tipo]_interi` | Double | 3 | m² | Media aree componenti interi |
| `totale_area_[tipo]_parziali` | Double | 3 | m² | Somma aree componenti parziali |
| `totale_area_[tipo]` | Double | 3 | m² | Somma totale (interi + parziali) |
| `totale_area_malta` | Double | 3 | m² | Area rimanente (area_campione - totale_area_componenti) |

**Nota**: `[tipo]` viene sostituito con "mattoni" o "componenti" a seconda dello script.

---

#### Rapporti (Solo Script Mattoni)

| Campo | Tipo | Decimali | Descrizione |
|-------|------|----------|-------------|
| `rapporto_mattoni/malta` | Double | 2 | Rapporto percentuale tra area mattoni e area malta |

Formula:
```python
rapporto_mattoni/malta = (totale_area_mattoni / totale_area_malta) * 100
```

Interpretazione:
- Valore > 100: prevale il mattone
- Valore < 100: prevale la malta
- Valore ≈ 100: proporzioni equilibrate

---

#### Statistiche Dimensionali - Larghezza

| Campo | Tipo | Decimali | Unità | Descrizione |
|-------|------|----------|-------|-------------|
| `width_min` | Double | 3 | m | Larghezza minima |
| `width_max` | Double | 3 | m | Larghezza massima |
| `width_range` | Double | 3 | m | Range (max - min) |
| `width_mean` | Double | 3 | m | Media larghezze |
| `width_stddev` | Double | 3 | m | Deviazione standard larghezze |

**Formule**:
```python
width_range = width_max - width_min
width_mean = SUM(width_bbox) / COUNT(*)
width_stddev = √(Σ(width_bbox - width_mean)² / (n-1))
```

---

#### Statistiche Dimensionali - Altezza

| Campo | Tipo | Decimali | Unità | Descrizione |
|-------|------|----------|-------|-------------|
| `height_min` | Double | 3 | m | Altezza minima |
| `height_max` | Double | 3 | m | Altezza massima |
| `height_range` | Double | 3 | m | Range (max - min) |
| `height_mean` | Double | 3 | m | Media altezze |
| `height_stddev` | Double | 3 | m | Deviazione standard altezze |

---

### Tabelle "Conteggio Range"

#### Conteggio Range Larghezza

| Campo | Tipo | Descrizione | Esempio |
|-------|------|-------------|---------|
| `campione` | String | Codice campione | "C001" |
| `sito` | String | Nome sito | "Foro Romano" |
| `ambiente` | String | Ambiente | "AMB1" |
| `usm` | String | USM | "USM100" |
| `width_bbox_range` | String | Classe dimensionale | "0.280-0.282" |
| `count` | Integer | N° elementi nella classe | 5 |

**Interpretazione**:
La tabella mostra quanti componenti ricadono in ogni classe dimensionale di larghezza.

---

#### Conteggio Range Altezza

Struttura identica a "Conteggio Range Larghezza", ma con:
- Campo `height_bbox_range` invece di `width_bbox_range`
- Classi basate sull'altezza

---

## 🔤 Convenzioni di Nomenclatura

### Prefissi dei Campi

- Nessun prefisso: campi grezzi o identificativi
- `num_`: contatori (interi)
- `totale_`: somme cumulative
- `media_`: valori medi
- Suffissi `_min`, `_max`, `_mean`, `_stddev`, `_range`: statistiche descrittive

### Suffissi Dimensionali

- `_bbox`: derivato dal bounding box
- `_componente`: riferito al singolo componente
- `_campione`: riferito all'intero campione
- `_modulo`: relativo all'unità metrologica

### Simboli Speciali

- **Δ** (delta): indica resto/variazione
- **/** (slash): indica rapporto (es. `mattoni/malta`)

---

## ⚠️ Valori Speciali e NULL

### Quando un campo è NULL

I campi metrologici (`width_modulo`, `Δwidth_modulo`, etc.) sono NULL quando:
- `superficie = "parziale"` (calcolati solo per componenti interi)
- Il componente non soddisfa i filtri impostati
- Errori di calcolo geometrico

### Gestione dei NULL

Gli script gestiscono automaticamente i NULL:
- Esclusi dai calcoli statistici
- Non contati nelle somme
- Segnalati nei log di esecuzione

---

## 📐 Conversioni Utili

### Unità di Misura

```
1 m = 100 cm = 1000 mm
1 m² = 10000 cm² = 1000000 mm²

1 piede romano = 0.296 m = 29.6 cm
1 piede greco = 0.308 m = 30.8 cm
1 piede dorico = 0.326 m = 32.6 cm
```
