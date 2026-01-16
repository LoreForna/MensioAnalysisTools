# Mensio Analysis Tools

[![QGIS](https://img.shields.io/badge/QGIS-%3E%3D3.16-green)](https://qgis.org)
[![Python](https://img.shields.io/badge/Python-%3E%3D3.8-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-GPL--3.0-orange)]
[![Version](https://img.shields.io/badge/Version-1.1-brightgreen)](https://github.com/LoreForna/MensioAnalysisTools/releases)

**Suite di strumenti QGIS per l'analisi quantitativa di murature storiche**

Collezione di algoritmi di processing QGIS progettati per l'analisi dimensionale e statistica di componenti murari in contesti archeologici e architettonici, con particolare focus sulle tecniche edilizie antiche.

---

## 📋 Indice

- [Caratteristiche](#-caratteristiche)
- [Versioni Disponibili](#-versioni-disponibili)
- [Suite di Strumenti](#-suite-di-strumenti)
- [Installazione](#-installazione)
- [Requisiti](#-requisiti)
- [Struttura Dati](#-struttura-dati)
- [Utilizzo](#-utilizzo)
- [Output](#-output)
- [Differenze tra Versioni](#-differenze-tra-versioni)
- [Metodologia](#-metodologia)
- [Esempio](#-esempio)
- [Contributi](#-contributi)
- [Crediti](#-crediti)
- [Licenza](#-licenza)

---

## ✨ Caratteristiche

- **Analisi automatizzata** di componenti murari con calcolo di statistiche dimensionali complete
- **Sistema modulare configurabile** per analisi metrologiche basate su diverse unità di misura storiche
- **Separazione intelligente** tra componenti interi e parziali per analisi accurate
- **Calcolo del poligono minimo orientato** (Minimum Oriented Bounding Box) per ogni elemento
- **Statistiche avanzate**: media, deviazione standard, range, distribuzioni
- **Due modalità di analisi**: per campione (v1.0) o aggregate globali (v1.1)
- **Output multipli** organizzati: layer geometrici, tabelle statistiche, distribuzioni per range
- **Validazione robusta** dei dati in input con messaggi di errore dettagliati
- **Campo superficie opzionale** (v1.1): adattamento automatico se presente o assente

---

## 🔄 Versioni Disponibili

La suite è disponibile in due versioni principali:

### Versione 1.0 - Con Area Campione
**Modalità**: Analisi per campione  
**Requisiti**: Layer rilievo + Layer campioni  
**Ideale per**: Analisi comparative tra diverse aree campionate

**File**:
- `analisi_quantitativa_mattoni_v1_0.py`
- `analisi_quantitativa_componenti_a_secco_v1_0.py`
- `analisi_quantitativa_altri_componenti_v1_0.py`

### Versione 1.1 - Senza Area Campione
**Modalità**: Analisi aggregate globali  
**Requisiti**: Solo layer rilievo  
**Ideale per**: Analisi rapide per murature non campionate

**File**:
- `analisi_quantitativa_mattoni_senza_campione_v1_1.py`
- `analisi_altri_componenti_senza_campione_v1_1.py`
- `analisi_componenti_a_secco_senza_campione_v1_1.py`

**Vantaggi v1.1**:
- ✅ Workflow semplificato (11 step invece di 19)
- ✅ Non richiede layer campioni
- ✅ Campo `superficie` opzionale con comportamento adattivo
- ✅ Più veloce da eseguire
- ✅ Output ridotti (5 invece di 6)

---

## 🛠️ Suite di Strumenti

### 1. Analisi Quantitativa Mattoni

Analisi specializzata per murature in laterizi di età romana.

#### Versione 1.0 (Con Campione)
**File**: `analisi_quantitativa_mattoni_v1_0.py`

**Caratteristiche**:
- Ottimizzato per opus latericium
- Range di precisione: 4mm (larghezza), 2mm (altezza)
- Calcolo del rapporto mattoni/malta per campione
- Stima del numero di mattoni interi per campione
- Statistiche per ogni area campionata

#### Versione 1.1 (Senza Campione)
**File**: `analisi_quantitativa_mattoni_senza_campione_v1_1.py`

**Caratteristiche**:
- Statistiche aggregate globali
- Campo `superficie` opzionale
- Nessun layer campioni richiesto
- Output semplificati
- Tabella unica con statistiche: Componenti interi, Componenti parziali, Totale, Larghezza, Altezza, Area

**Ideale per**: Murature in opera laterizia e/o opere miste in laterizi

---

### 2. Analisi Quantitativa Componenti a Secco

Analisi per elementi strutturali assemblati senza legante.

#### Versione 1.0 (Con Campione)
**File**: `analisi_quantitativa_componenti_a_secco_v1_0.py`

**Caratteristiche**:
- Calcoli metrologici con modulo configurabile (default: piede romano 0.296m)
- Campi modulo solo per superficie='intera'
- Statistiche per campione
- Range personalizzabili (default 1cm)

#### Versione 1.1 (Senza Campione)
**File**: `analisi_componenti_a_secco_senza_campione_v1_1.py`

**Caratteristiche**:
- Campi modulo per **TUTTI i componenti** (non solo interi)
- Campo `superficie` opzionale
- Statistiche aggregate globali
- Variabile `@modulo` aggiunta al layer

**Campi virtuali** (sempre presenti per tutti):
- `width_modulo`, `Δwidth_modulo`
- `height_modulo`, `Δheight_modulo`

**Ideale per**: Murature a secco

---

### 3. Analisi Quantitativa Altri Componenti

Analisi generica per componenti eterogenei o materiali speciali.

#### Versione 1.0 (Con Campione)
**File**: `analisi_quantitativa_altri_componenti_v1_0.py`

**Caratteristiche**:
- Flessibilità massima nei parametri
- Supporto per tipologie multiple di materiali
- Calcoli metrologici per campione
- Filtri avanzati per classificazione materiali

#### Versione 1.1 (Senza Campione)
**File**: `analisi_altri_componenti_senza_campione_v1_1.py`

**Caratteristiche**:
- Campi modulo per **TUTTI i componenti**
- Campo `superficie` opzionale
- Statistiche aggregate globali
- Workflow semplificato

**Ideale per**: Murature in opera incerta, reticolata, e mista

---

## 📥 Installazione

### Metodo 1: Copia diretta (consigliato)

1. Scarica i file `.py` dalla repository
2. Apri QGIS e vai in:
   ```
   Settings → User Profiles → Open Active Profile Folder
   ```
3. Naviga nella cartella:
   ```
   processing/scripts/
   ```
4. Copia gli script scaricati nella cartella
5. Riavvia QGIS o ricarica gli script dal Processing Toolbox

### Metodo 2: Da Processing Toolbox

1. Apri il **Processing Toolbox** in QGIS
2. Clicca sull'icona Python in alto → "Add Script to Toolbox..."
3. Seleziona il file `.py` desiderato
4. Lo script apparirà nel gruppo "Analisi quantitative"

### Installazione Plugin DataPlotly

Necessario per la visualizzazione dei grafici (solo v1.0):

1. In QGIS: `Plugins` → `Manage and Install Plugins`
2. Cerca "DataPlotly"
3. Installa il plugin

---

## 📧 Requisiti

### Software
- **QGIS**: versione ≥ 3.16 (LTR o superiore)
- **Python**: versione ≥ 3.8
- **Plugin**: DataPlotly (opzionale, solo per v1.0)

### Dati
- Sistema di riferimento **cartografico o locale** (NO geografico WGS84)
- Layer vettoriali poligonali con struttura dati specifica (vedi sotto)

### Sistema Operativo
- Windows, macOS, Linux (qualsiasi OS supportato da QGIS)

---

## 📊 Struttura Dati

### Versione 1.0 - Con Campione

Richiede due layer poligonali:

#### Layer "campioni"
Poligoni delle aree campionate (generalmente 1 m²)

| Campo | Tipo | Descrizione | Obbligatorio |
|-------|------|-------------|--------------|
| `fid` | Integer | ID univoco | ✗ |
| `campione` | String | Identificativo campione | ✓ |
| `sito` | String | Nome sito archeologico | ✗ |
| `ambiente` | String | Identificativo ambiente | ✗ |
| `usm` | String | Unità Stratigrafica Muraria | ✗ |
| `area_campione` | Double | Area del campione (m²) | ✗ |

#### Layer "rilievo"
Poligoni dei singoli componenti murari

| Campo | Tipo | Descrizione | Obbligatorio |
|-------|------|-------------|--------------|
| `fid` | Integer | ID univoco | ✗ |
| `tipo` | String | Tipologia materiale | ✗ |
| `superficie` | String | "intera" o "parziale" | ✗ |
| `area_componente` | Double | Area del componente (m²) | ✗ |
| `num_componente` | Integer | Numero progressivo | ✗ |
| `usm` | String | Unità Stratigrafica Muraria | ✗ |

---

### Versione 1.1 - Senza Campione

Richiede **solo** un layer:

#### Layer "rilievo"
Poligoni dei singoli componenti murari

| Campo | Tipo | Descrizione | Obbligatorio | Note v1.1 |
|-------|------|-------------|--------------|-----------|
| `fid` | Integer | ID univoco | ✗ | |
| `tipo` | String | Tipologia materiale | ✗ | |
| `superficie` | String | "intera" o "parziale" | ✗ | Se assente, tutti i componenti sono usati per statistiche |
| `area_componente` | Double | Area del componente (m²) | ✗ | |
| `num_componente` | Integer | Numero progressivo | ✗ | |
| `usm` | String | Unità Stratigrafica Muraria | ✗ | 

**⚠️ Comportamento campo `superficie` (v1.1)**:
- **Se PRESENTE**: Statistiche calcolate solo su componenti "interi"
- **Se ASSENTE o NULL**: Statistiche calcolate su **TUTTI** i componenti

---

## 🚀 Utilizzo

### Quale Versione Usare?

**Usa Versione 1.0** se:
- ✓ Hai definito aree campione specifiche
- ✓ Vuoi statistiche separate per ogni campione
- ✓ Devi confrontare diverse zone della muratura
- ✓ Segui metodologia con campionamento 1m²

**Usa Versione 1.1** se:
- ✓ Vuoi analisi rapide senza campionamento
- ✓ Hai rilievo completo senza divisione in campioni
- ✓ Hai bisogno solo di statistiche globali
- ✓ Il campo "superficie" non è compilato o manca

---

### Workflow Versione 1.0 (Con Campione)

1. **Preparazione dati**
   - Crea layer "campioni" e "rilievo"
   - Verifica sistema di riferimento cartografico
   - Assicurati che tutti i campi obbligatori siano presenti

2. **Esecuzione analisi**
   - Apri Processing Toolbox
   - Cerca "Analisi quantitative"
   - Seleziona lo strumento v1.0 appropriato
   - Configura parametri

3. **Parametri v1.0**:
   - `Layer rilievo`: layer componenti
   - `Layer campioni`: layer aree campionate
   - `Tipo di materiale`: filtro opzionale
   - `Includi non classificati`: include elementi con tipo=NULL
   - `Step range larghezza/altezza`: intervalli per distribuzioni
   - `Valore del modulo`: (solo Componenti a secco/Altri)

---

### Workflow Versione 1.1 (Senza Campione)

1. **Preparazione dati**
   - Crea **solo** layer "rilievo"
   - Verifica sistema di riferimento cartografico
   - Campo `superficie` è **opzionale**

2. **Esecuzione analisi**
   - Apri Processing Toolbox
   - Cerca "Analisi quantitative"
   - Seleziona lo strumento "senza campione" appropriato
   - Configura parametri

3. **Parametri v1.1**:
   - `Layer rilievo`: layer componenti
   - `Tipo di materiale`: filtro opzionale
   - `Includi non classificati`: include elementi con tipo=NULL
   - `Step range larghezza/altezza`: intervalli per distribuzioni
   - `Valore del modulo`: (solo Componenti a secco/Altri)

---

## 📈 Output

### Output Versione 1.0 (6 file)

1. **Min Oriented Bbox** - Rettangoli orientati minimi
2. **Analisi Rilievo** - Layer rilievo arricchito
3. **Analisi Campioni (Tabella)** - Statistiche per campione
4. **Analisi Campioni (Layer)** - Campioni con statistiche
5. **Conteggio Range Larghezza** - Distribuzioni per campione
6. **Conteggio Range Altezza** - Distribuzioni per campione

---

### Output Versione 1.1 (5 file)

1. **Min Oriented Bbox** - Rettangoli orientati minimi
2. **Analisi Rilievo** - Layer rilievo arricchito
3. **Statistiche Aggregate** - Tabella unica globale
   - **6 righe**:
     1. Componenti interi (count)
     2. Componenti parziali (count)
     3. Totale (count)
     4. Larghezza (count, min, max, range, mean, stddev)
     5. Altezza (count, min, max, range, mean, stddev)
     6. Area (count, min, max, range, mean, stddev)
4. **Conteggio Range Larghezza** - Distribuzione globale
5. **Conteggio Range Altezza** - Distribuzione globale

---

## 🔄 Differenze tra Versioni

### Tabella Comparativa

| Caratteristica | v1.0 (Con Campione) | v1.1 (Senza Campione) |
|----------------|---------------------|------------------------|
| **Layer richiesti** | Rilievo + Campioni | Solo Rilievo |
| **Campo `superficie`** | Obbligatorio | Opzionale |
| **Campo `usm`** | Solo layer campioni | Solo layer rilievo |
| **Step elaborazione** | 19 | 11 |
| **Output generati** | 6 | 5 |
| **Statistiche** | Per campione | Aggregate globali |
| **Campi modulo** (a secco/altri) | Solo superficie='intera' | **Tutti i componenti** |
| **Rapporto mattoni/malta** | Per campione | Non calcolato |
| **Complessità codice** | ~1119 righe | ~757 righe |

---

### Quando NON sono compatibili

❌ **Non puoi sostituire direttamente v1.0 con v1.1** se:
- Hai bisogno di statistiche per singolo campione
- Devi calcolare rapporti mattoni/malta per area
- Usi i layer campioni poligonali con statistiche
- La metodologia richiede campionamento su 1m²

✅ **Puoi usare v1.1 invece di v1.0** se:
- Vuoi solo statistiche globali
- Non hai definito aree campione
- Hai un rilievo completo senza divisioni
- Vuoi un'analisi più rapida

---

## 📬 Metodologia

### Pipeline di Elaborazione v1.0

```
INPUT
  ├─ Layer campioni (poligoni aree)
  └─ Layer rilievo (poligoni componenti)
     │
     ▼
VALIDAZIONE
  ├─ Verifica campi obbligatori
  ├─ Controllo geometrie valide
  └─ Validazione sistema riferimento
     │
     ▼
SPATIAL JOIN
  └─ Associazione componenti → campioni
     │
     ▼
GEOMETRIC ANALYSIS
  ├─ Calcolo Minimum Oriented Bounding Box
  ├─ Estrazione dimensioni (width/height)
  └─ Calcolo metriche geometriche
     │
     ▼
FILTERING
  ├─ Separazione interi/parziali
  ├─ Filtro per tipologia materiale
  └─ Gestione valori NULL
     │
     ▼
STATISTICS PER CAMPIONE
  ├─ Aggregazione per campione
  ├─ Calcolo statistiche descrittive
  └─ Creazione distribuzioni per range
     │
     ▼
OUTPUT (6 file)
```

---

### Pipeline di Elaborazione v1.1 

```
INPUT
  └─ Layer rilievo (poligoni componenti)
     │
     ▼
VALIDAZIONE
  ├─ Verifica campi obbligatori
  ├─ Campo 'superficie' opzionale
  └─ Validazione sistema riferimento
     │
     ▼
GEOMETRIC ANALYSIS
  ├─ Calcolo Minimum Oriented Bounding Box
  ├─ Aggiunta campi usm e num_componente al bbox
  └─ Join bbox con rilievo
     │
     ▼
FILTERING (se campo superficie presente)
  ├─ Separazione interi/parziali
  └─ Scelta layer per statistiche
     │
     ▼
STATISTICS GLOBALI
  ├─ Calcolo statistiche aggregate
  ├─ Tabella unica (6 righe)
  └─ Distribuzioni globali
     │
     ▼
METROLOGICAL ANALYSIS (a secco/altri)
  └─ Campi modulo per TUTTI i componenti
     │
     ▼
OUTPUT (5 file)
```

---

## 💡 Esempio

**Nota**: I dati di esempio per testare gli script si trovano nella cartella **Data/** del repository:
- `TEST_Analisi_campioni.gpkg` - GeoPackage con layer di test già configurati

### Esempio v1.0 - Analisi muratura con campionamento

```
1. Carica il geopackage "TEST_Analisi_campioni.gpkg"
2. Usa layer "campioni" e "rilievo"
3. Esegui "Analisi Quantitativa Mattoni" v1.0
   - Layer rilievo: "rilievo"
   - Layer campioni: "campioni"
   - Tipo materiale: "laterizio"
   - Step larghezza: 0.004 m
   - Step altezza: 0.002 m
4. Ottieni 6 output con statistiche per campione
```

### Esempio v1.1 - Analisi rapida senza campioni 

```
1. Carica solo il layer "rilievo"
2. Esegui "Mattoni senza campione" v1.1
   - Layer rilievo: "rilievo"
   - Tipo materiale: "laterizio"
   - Step larghezza: 0.004 m
   - Step altezza: 0.002 m
3. Ottieni 5 output con statistiche globali
4. Verifica tabella "statistiche_aggregate" (6 righe)
```

---

## 📚 Riferimenti Metodologici

Gli script si basano sulla metodologia proposta da:

**Medri, M.** et al. - *"Metodi di analisi quantitativa delle murature romane in opera laterizia"*
[PDF](https://pdfs.semanticscholar.org/373e/c1a3bf317c3216612f4c63d9802da5d67ce0.pdf)

La metodologia prevede:
- Campionamento su aree standard (generalmente 1 m²) - **v1.0**
- Analisi globali senza campionamento - **v1.1**
- Distinzione tra elementi interi e parziali
- Analisi dimensionale basata su Minimum Oriented Bounding Box
- Calcolo di statistiche descrittive
- Studio delle distribuzioni dimensionali

---

## 🎯 Best Practices

### Acquisizione dati
- ✓ Usa un sistema di riferimento metrico appropriato
- ✓ Digitalizza accuratamente i contorni dei componenti
- ✓ Marca correttamente il campo `superficie` (intera/parziale) se presente
- ✓ Classifica i materiali in modo coerente nel campo `tipo`
- ✓ Compila il campo `usm` in modo coerente
- ✓ Mantieni la topologia pulita (no overlap, no gap)

### Scelta della versione
- ✓ Usa **v1.0** per analisi comparative tra campioni
- ✓ Usa **v1.1** per analisi rapide e statistiche globali
- ✓ Documenta sempre quale versione hai usato

### Configurazione parametri
- ✓ Scegli step range appropriati alla scala di analisi
- ✓ Per analisi metrologiche, ricerca il valore di modulo storicamente documentato
- ✓ Usa filtri materiali quando necessario per analisi separate
- ✓ Documenta sempre i parametri utilizzati nei metadati

### Interpretazione risultati
- ✓ Verifica visivamente i bbox generati
- ✓ Controlla le statistiche per valori anomali
- ✓ Confronta i risultati con campioni analoghi
- ✓ Documenta le osservazioni e le interpretazioni

---

## 📖 Citazione

Fornaciari, L. (2024). MensioAnalysisTools: Suite di strumenti QGIS per l'analisi quantitativa delle murature storiche (Versione 1.1) [Software]. 
> GitHub. https://github.com/LoreForna/MensioAnalysisTools

---

## 📄 Licenza

Questo progetto è rilasciato sotto licenza **GNU General Public License v3.0**.

---

