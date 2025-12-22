# Guida Rapida

## 🚀 Installazione in 5 minuti

### 1. Download

Scarica i file dalla repository:
- `analisi_quantitativa_mattoni_v1_0.py`
- `analisi_quantitativa_componenti_a_secco_v1_0.py`
- `analisi_quantitativa_altri_componenti_v1_0.py`

### 2. Installazione in QGIS

**Windows**:
```
C:\Users\[TUO_UTENTE]\AppData\Roaming\QGIS\QGIS3\profiles\default\processing\scripts\
```

**macOS**:
```
~/Library/Application Support/QGIS/QGIS3/profiles/default/processing/Script/
```

**Linux**:
```
~/.local/share/QGIS/QGIS3/profiles/default/processing/Script/
```

### 3. Plugin DataPlotly

1. `Plugins` → `Manage and Install Plugins`
2. Cerca "DataPlotly"
3. Installa

### 4. Riavvia QGIS

Riavvia QGIS o ricarica gli script dal Processing Toolbox.

---

## 📊 Primo Utilizzo

### Opzione A: Usa i Dati di Test (Consigliato)

Il modo più rapido per iniziare è usare i dati di esempio già pronti:

1. Nella cartella **Data/** del repository trovi:
   - `TEST_Analisi_campioni.gpkg` - GeoPackage con layer già configurati

2. In QGIS:
   - `Layer` → `Add Layer` → `Add Vector Layer`
   - Seleziona `TEST_Analisi_campioni.gpkg`
   - Carica i layer "campioni" e "rilievo"

3. Vai direttamente alla sezione [Esecuzione](#esecuzione)

### Opzione B: Prepara i Tuoi Dati

Se vuoi usare i tuoi dati, crea due layer poligonali:

#### Layer "campioni"
```
Campi obbligatori:
- fid (Integer)
- campione (String)
- sito (String)
- ambiente (String)
- usm (String)
- area_campione (Double)
```

#### Layer "rilievo"
```
Campi obbligatori:
- fid (Integer)
- tipo (String)
- superficie (String)  ← "intera" o "parziale"
- area_componente (Double)
- num_componente (Integer)
```

### Esecuzione

1. Apri **Processing Toolbox** (Ctrl+Alt+T)
2. Cerca "Analisi quantitative"
3. Seleziona lo script appropriato:
   - **Mattoni**: per laterizi romani
   - **Componenti a secco**: per elementi modulari
   - **Altri componenti**: per materiali misti

4. Configura i parametri:
   - Layer rilievo: seleziona il tuo layer
   - Layer campioni: seleziona il tuo layer
   - Altri: lascia i default per il primo test

5. Clicca "Run"

### Verifica Output

Controlla che siano stati generati 6 output:
- ✓ Min oriented bbox
- ✓ Analisi rilievo
- ✓ Analisi campioni (tabella)
- ✓ Analisi campioni (layer)
- ✓ Conteggio range larghezza
- ✓ Conteggio range altezza

---

## 🎯 Esempi di Configurazione

### Analisi mattoni romani standard
```
Script: Analisi Quantitativa Mattoni
Layer rilievo: rilievo
Layer campioni: campioni
Tipo materiale: laterizio
Includi non classificati: NO
Step larghezza: 0.002 m (2mm)
Step altezza: 0.001 m (1mm)
```

### Analisi con piede romano
```
Script: Analisi Quantitativa Componenti a Secco
Layer rilievo: rilievo
Layer campioni: campioni
Tipo materiale: (vuoto = tutti)
Valore modulo: 0.296 m
Step larghezza: 0.01 m
Step altezza: 0.01 m
```

### Analisi multi-materiale
```
Script: Analisi Quantitativa Altri Componenti
Layer rilievo: rilievo
Layer campioni: campioni
Tipo materiale: tufo,laterizio,pietra
Includi non classificati: SI
Valore modulo: 0.296 m
```

---

## ⚠️ Problemi Comuni

### "Il layer non contiene i campi obbligatori"
**Soluzione**: Verifica che tutti i campi richiesti siano presenti e con il nome corretto (case-sensitive).

### "Sistema di riferimento non valido"
**Soluzione**: Usa un sistema di riferimento metrico (non WGS84). Esempio: EPSG:3003, EPSG:32633.

### "Nessun output generato"
**Soluzione**: 
1. Verifica che ci siano features nei layer
2. Controlla che il campo "superficie" contenga "intera" per almeno alcuni elementi
3. Verifica la validità delle geometrie

### Script non visibili nel Processing Toolbox
**Soluzione**:
1. Verifica il percorso di installazione
2. Riavvia QGIS completamente
3. Controlla che i file abbiano estensione `.py`

---

## 📋 Checklist Pre-Esecuzione

Prima di eseguire l'analisi, verifica:

- [ ] Sistema di riferimento cartografico/locale attivo
- [ ] Layer "campioni" presente con tutti i campi
- [ ] Layer "rilievo" presente con tutti i campi
- [ ] Campo "superficie" compilato correttamente
- [ ] Campo "tipo" compilato (se usi filtri)
- [ ] Geometrie valide (no errori topologici)
- [ ] Area dei campioni calcolata nel campo `area_campione`
- [ ] Plugin DataPlotly installato

---

## 🎓 Risorse Aggiuntive

- **README completo**: [README.md](README.md)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)
- **Documentazione campi**: [GUIDA_CAMPI.md](GUIDA_CAMPI.md)
- **Issues**: [GitHub Issues](link-issues)

---
