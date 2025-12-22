# Mensio Analysis Tools

[![QGIS](https://img.shields.io/badge/QGIS-%3E%3D3.16-green)](https://qgis.org)
[![Python](https://img.shields.io/badge/Python-%3E%3D3.8-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-GPL--3.0-orange)]
[![Version](https://img.shields.io/badge/Version-1.0-brightgreen)](https://github.com/LoreForna/MensioAnalysisTools/releases)

**Suite di strumenti QGIS per l'analisi quantitativa di murature storiche**

Collezione di algoritmi di processing QGIS progettati per l'analisi dimensionale e statistica di componenti murari in contesti archeologici e architettonici, con particolare focus sulle tecniche edilizie romane.

---

## 📋 Indice

- [Caratteristiche](#-caratteristiche)
- [Suite di Strumenti](#-suite-di-strumenti)
- [Installazione](#-installazione)
- [Requisiti](#-requisiti)
- [Struttura Dati](#-struttura-dati)
- [Utilizzo](#-utilizzo)
- [Output](#-output)
- [Metodologia](#-metodologia)
- [Esempi](#-esempi)
- [Contributi](#-contributi)
- [Crediti](#-crediti)
- [Licenza](#-licenza)

---

## ✨ Caratteristiche

- **Analisi automatizzata** di componenti murari con calcolo di statistiche dimensionali complete
- **Sistema modulare configurabile** per analisi metrologiche basate su diverse unità di misura storiche
- **Separazione intelligente** tra componenti interi e parziali per analisi accurate
- **Calcolo del poligono minimo orientato** (Minimum Oriented Bounding Box) per ogni elemento
- **Statistiche avanzate** per campione: media, deviazione standard, range, distribuzioni
- **Output multipli** organizzati: layer geometrici, tabelle statistiche, distribuzioni per range
- **Validazione robusta** dei dati in input con messaggi di errore dettagliati
- **Generazione automatica** di schede campione con grafici DataPlotly

---

## 🛠️ Suite di Strumenti

La suite comprende tre algoritmi specializzati per diverse tipologie di analisi:

### 1. Analisi Quantitativa Mattoni
**File**: `analisi_quantitativa_mattoni_v1_0.py`

Analisi specializzata per murature in laterizi di età romana.

**Caratteristiche specifiche**:
- Ottimizzato per opera laterizia
- Range di precisione: 2mm (larghezza), 1mm (altezza)
- Calcolo del rapporto mattoni/malta
- Stima del numero di mattoni equivalenti interi

**Ideale per**: Murature in opus latericium, analisi di laterizi romani

---

### 2. Analisi Quantitativa Componenti a Secco
**File**: `analisi_quantitativa_componenti_a_secco_v1_0.py`

Analisi per elementi strutturali assemblati senza legante.

**Caratteristiche specifiche**:
- Calcoli metrologici con modulo configurabile (default: piede romano 0.296m)
- Campi aggiuntivi: `width_modulo`, `Δwidth_modulo`, `height_modulo`, `Δheight_modulo`
- Analisi delle variazioni rispetto al modulo base
- Range personalizzabili (default 1cm)

**Ideale per**: Murature in opus quadratum, strutture a secco, analisi metrologiche in generale

---

### 3. Analisi Quantitativa Altri Componenti
**File**: `analisi_quantitativa_altri_componenti_v1_0.py`

Analisi generica per componenti eterogenei o materiali speciali.

**Caratteristiche specifiche**:
- Flessibilità massima nei parametri
- Supporto per tipologie multiple di materiali
- Calcoli metrologici configurabili
- Filtri avanzati per classificazione materiali

**Ideale per**: Murature miste, elementi lapidei irregolari, componenti non standard

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
   processing/Script/
   ```
4. Copia gli script scaricati nella cartella
5. Riavvia QGIS o ricarica gli script dal Processing Toolbox

### Metodo 2: Da Processing Toolbox

1. Apri il **Processing Toolbox** in QGIS
2. Clicca sull'icona Python in alto → "Add Script to Toolbox..."
3. Seleziona il file `.py` desiderato
4. Lo script apparirà nel gruppo "Analisi quantitative"

### Installazione Plugin DataPlotly

Necessario per la visualizzazione dei grafici:

1. In QGIS: `Plugins` → `Manage and Install Plugins`
2. Cerca "DataPlotly"
3. Installa il plugin

---

## 🔧 Requisiti

### Software
- **QGIS**: versione ≥ 3.16 (LTR o superiore)
- **Python**: versione ≥ 3.8
- **Plugin**: DataPlotly

### Dati
- Sistema di riferimento **cartografico o locale** (NO geografico WGS84)
- Layer vettoriali poligonali con struttura dati specifica (vedi sotto)

### Sistema Operativo
- Windows, macOS, Linux (qualsiasi OS supportato da QGIS)

---

## 📊 Struttura Dati

Gli script richiedono due layer poligonali con struttura predefinita:

### Layer "campioni"
Poligoni delle aree campionate (generalmente 1 m²)

| Campo | Tipo | Descrizione | Obbligatorio |
|-------|------|-------------|--------------|
| `fid` | Integer | ID univoco | ✓ |
| `campione` | String | Identificativo campione | ✓ |
| `sito` | String | Nome sito archeologico | ✓ |
| `ambiente` | String | Identificativo ambiente | ✓ |
| `usm` | String | Unità Stratigrafica Muraria | ✓ |
| `area_campione` | Double | Area del campione (m²) | ✓ |

### Layer "rilievo"
Poligoni dei singoli componenti murari all'interno dei campioni

| Campo | Tipo | Descrizione | Obbligatorio |
|-------|------|-------------|--------------|
| `fid` | Integer | ID univoco | ✓ |
| `tipo` | String | Tipologia materiale (es. "laterizio", "tufo") | ✓ |
| `superficie` | String | "intera" o "parziale" | ✓ |
| `area_componente` | Double | Area del componente (m²) | ✓ |
| `num_componente` | Integer | Numero progressivo componente | ✓ |

**Nota importante**: Il campo `superficie` determina se il componente viene incluso nelle statistiche dimensionali (solo elementi "interi" sono considerati per le misure).

---

## 🚀 Utilizzo

### Workflow Base

1. **Preparazione dati**
   - Crea o importa i layer "campioni" e "rilievo"
   - Verifica che il sistema di riferimento sia cartografico
   - Assicurati che tutti i campi obbligatori siano presenti

2. **Esecuzione analisi**
   - Apri Processing Toolbox
   - Cerca "Analisi quantitative"
   - Seleziona lo strumento appropriato (Mattoni/Componenti a secco/Altri componenti)
   - Configura i parametri

3. **Configurazione parametri**

   **Parametri comuni a tutti gli script**:
   - `Layer rilievo`: seleziona il layer dei componenti
   - `Layer campioni`: seleziona il layer dei campioni
   - `Tipo di materiale`: filtro opzionale (es. "laterizio,tufo" o vuoto=tutti)
   - `Includi non classificati`: include elementi con tipo=NULL
   - `Step range larghezza`: intervallo per range larghezza
   - `Step range altezza`: intervallo per range altezza

   **Parametri specifici** (Componenti a secco / Altri componenti):
   - `Valore del modulo`: unità di misura base (default 0.296m = piede romano)

4. **Analisi risultati**
   - Esamina i layer di output generati
   - Verifica le statistiche nelle tabelle
   - Utilizza i layout Atlas per la reportistica

---

## 📈 Output

Ogni script genera 6 output principali:

### 1. Min Oriented Bbox
**Tipo**: Layer poligonale

Rettangoli minimi orientati per ogni componente. Utile per verificare visivamente la qualità dell'analisi geometrica.

**Campi principali**: `width_bbox`, `height_bbox`, `angle_bbox`, `area_bbox`, `perimeter_bbox`

---

### 2. Analisi Rilievo
**Tipo**: Layer poligonale

Layer originale arricchito con tutte le metriche calcolate.

**Campi aggiuntivi**:
- Dimensioni bbox: `width_bbox`, `height_bbox`, `angle_bbox`
- Metriche area: `area_bbox`, `perimeter_bbox`
- **[Solo Componenti a secco/Altri]**: `width_modulo`, `Δwidth_modulo`, `height_modulo`, `Δheight_modulo`

---

### 3. Analisi Campioni (Tabella)
**Tipo**: Tabella (no geometria)

Statistiche complete aggregate per ogni campione.

**Statistiche incluse**:
- Conteggi: numero componenti interi/parziali
- Aree: totale, media, deviazione standard
- Dimensioni: min, max, range, media, stddev per larghezza e altezza
- **[Solo Mattoni]**: rapporto mattoni/malta, equivalenti interi

---

### 4. Analisi Campioni (Layer)
**Tipo**: Layer poligonale

Geometrie dei campioni con attributi statistici per visualizzazione cartografica.

**Utile per**: Tematizzazioni, mappe di distribuzione, analisi spaziali

---

### 5. Conteggio Range Larghezza
**Tipo**: Tabella

Distribuzione delle frequenze per classi di larghezza.

**Struttura**:
- `width_bbox_range`: classe dimensionale
- `count`: numero di elementi nella classe
- Campi identificativi: `campione`, `sito`, `ambiente`, `usm`

---

### 6. Conteggio Range Altezza
**Tipo**: Tabella

Distribuzione delle frequenze per classi di altezza.

**Struttura**: analoga a Conteggio Range Larghezza

---

## 🔬 Metodologia

### Pipeline di Elaborazione

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
STATISTICS
  ├─ Aggregazione per campione
  ├─ Calcolo statistiche descrittive
  └─ Creazione distribuzioni per range
     │
     ▼
METROLOGICAL ANALYSIS [Componenti a secco/Altri]
  ├─ Calcolo multipli del modulo
  └─ Calcolo variazioni (Δ)
     │
     ▼
OUTPUT
  ├─ Layer geometrici
  ├─ Tabelle statistiche
  └─ Distribuzioni frequenze
```

### Calcolo del Modulo (Componenti a secco / Altri)

Per ogni componente intero:

```python
width_modulo = floor(width_bbox / valore_modulo)
Δwidth_modulo = width_bbox % valore_modulo

height_modulo = floor(height_bbox / valore_modulo)
Δheight_modulo = height_bbox % valore_modulo
```

**Esempio pratico**:
- `width_bbox` = 0.890 m
- `valore_modulo` = 0.296 m (piede romano)
- → `width_modulo` = 3 (tre piedi interi)
- → `Δwidth_modulo` = 0.002 m (resto di 2mm)

### Statistiche Calcolate

Per ogni campione vengono calcolate:

- **Count**: n° elementi interi, n° elementi parziali
- **Area**: min, max, mean, sum, stddev
- **Width**: min, max, mean, range, stddev
- **Height**: min, max, mean, range, stddev
- **Rapporti**: area componenti/area malta (solo Mattoni)

---

## 💡 Esempi

**Nota**: I dati di esempio per testare gli script si trovano nella cartella **Data/** del repository:
- `TEST_Analisi_campioni.gpkg` - GeoPackage con layer di test già configurati

### Esempio 1: Analisi muratura in opus latericium

```
1. Carica il geopackage "TEST_Analisi_campioni.gpkg" dalla cartella Data/
2. Apri il progetto QGIS predisposto (se presente)
3. Esegui "Analisi Quantitativa Mattoni"
   - Layer rilievo: "rilievo"
   - Layer campioni: "campioni"
   - Tipo materiale: "laterizio"
   - Step larghezza: 0.002 m
   - Step altezza: 0.001 m
4. Esamina gli output
5. Carica il layout "scheda_campione"
6. Attiva modalità Atlas per report automatico
```

### Esempio 2: Analisi metrologica con piede romano

```
1. Prepara i layer con le geometrie
2. Esegui "Analisi Quantitativa Componenti a Secco"
   - Valore modulo: 0.296 m (piede romano)
   - Altri parametri: default
3. Analizza i campi "width_modulo" e "Δwidth_modulo"
4. Verifica la coerenza dimensionale rispetto al modulo
```

### Esempio 3: Confronto tra diversi sistemi metrologici

```
# Analizza lo stesso dataset con diversi moduli
- Esecuzione 1: modulo = 0.296 m (piede romano)
- Esecuzione 2: modulo = 0.308 m (piede greco)
- Esecuzione 3: modulo = 0.275 m (piede osco-italico)

# Confronta i risultati per identificare il sistema più probabile
```

---

## 📚 Riferimenti Metodologici

Gli script si basano sulla metodologia proposta da:

**Medri, M.** et al. - *"Metodi di analisi quantitativa delle murature romane in opera laterizia"*
[PDF](https://pdfs.semanticscholar.org/373e/c1a3bf317c3216612f4c63d9802da5d67ce0.pdf)

La metodologia prevede:
- Campionamento su aree standard (generalmente 1 m²)
- Distinzione tra elementi interi e parziali all'interno del campione
- Analisi dimensionale basata su Minimum Oriented Bounding Box
- Calcolo di statistiche descrittive
- Studio delle distribuzioni dimensionali

---

## 🎯 Best Practices

### Acquisizione dati
- ✓ Usa un sistema di riferimento metrico appropriato
- ✓ Digitalizza accuratamente i contorni dei componenti
- ✓ Marca correttamente il campo `superficie` (intera/parziale)
- ✓ Classifica i materiali in modo coerente nel campo `tipo`
- ✓ Mantieni la topologia pulita (no overlap, no gap)

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

## 🤝 Contributi

I contributi sono benvenuti! Per contribuire:

1. Fai fork del repository
2. Crea un branch per la tua feature (`git checkout -b feature/AmazingFeature`)
3. Commit delle modifiche (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request

### Linee guida
- Mantieni lo stile di codifica esistente
- Aggiungi docstring per nuove funzioni
- Aggiorna la documentazione
- Testa le modifiche con diversi dataset

---

## 📖 Citazione

Fornaciari, L. (2024). MensioAnalysisTools: Suite di strumenti QGIS per l'analisi quantitativa delle murature storiche (Versione 1.0) [Software]. 
> GitHub. https://github.com/LoreForna/MensioAnalysisTools

---

## 📄 Licenza

Questo progetto è rilasciato sotto licenza **GNU General Public License v3.0**.
