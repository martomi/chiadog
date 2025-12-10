# Guida all'aggiornamento di Chiadog

Questa guida spiega come aggiornare Chiadog all'ultima versione con supporto per Chia 2.5.7.

---

## Aggiornamento su Windows Server

### Prerequisiti
- Git installato
- Python 3.7+ installato
- Chiadog attualmente funzionante

### Passaggi

1. **Ferma Chiadog se in esecuzione**
   
   Se Chiadog gira come servizio o in background, fermalo prima:
   ```powershell
   # Se gira in una finestra PowerShell, premi Ctrl+C
   # Se gira come Task Scheduler, disabilita temporaneamente il task
   ```

2. **Naviga nella cartella di Chiadog**
   ```powershell
   cd C:\path\to\chiadog
   ```

3. **Salva la configurazione attuale**
   ```powershell
   Copy-Item config.yaml config.yaml.backup
   ```

4. **Aggiorna il repository**
   ```powershell
   git fetch origin
   git pull origin main
   ```

5. **Aggiorna le dipendenze**
   ```powershell
   # Se usi un virtual environment
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

6. **Verifica che la configurazione sia intatta**
   ```powershell
   # Controlla che config.yaml esista ancora
   Get-Item config.yaml
   ```

7. **Riavvia Chiadog**
   ```powershell
   python main.py --config config.yaml
   ```

8. **Verifica il funzionamento**
   
   Dopo qualche minuto, controlla che non ci siano warning "harvester appears to be offline".

---

## Aggiornamento su Ubuntu Server (Harvester)

### Prerequisiti
- Git installato
- Python 3.7+ installato
- Accesso SSH al server

### Passaggi

1. **Connettiti al server**
   ```bash
   ssh user@harvester-ip
   ```

2. **Ferma Chiadog**
   ```bash
   # Se gira come servizio systemd
   sudo systemctl stop chiadog
   
   # Se gira con screen/tmux, chiudi la sessione
   # screen -r chiadog poi Ctrl+C
   ```

3. **Naviga nella cartella di Chiadog**
   ```bash
   cd /path/to/chiadog
   # Tipicamente: cd ~/chiadog
   ```

4. **Salva la configurazione**
   ```bash
   cp config.yaml config.yaml.backup
   ```

5. **Aggiorna il repository**
   ```bash
   git fetch origin
   git pull origin main
   ```

6. **Aggiorna le dipendenze**
   ```bash
   # Se usi un virtual environment
   source venv/bin/activate
   pip install -r requirements.txt
   ```

7. **Riavvia Chiadog**
   
   **Se usi systemd:**
   ```bash
   sudo systemctl start chiadog
   sudo systemctl status chiadog
   ```

   **Se usi screen:**
   ```bash
   screen -S chiadog
   python main.py --config config.yaml
   # Premi Ctrl+A poi D per uscire da screen
   ```

   **Se usi tmux:**
   ```bash
   tmux new -s chiadog
   python main.py --config config.yaml
   # Premi Ctrl+B poi D per uscire da tmux
   ```

8. **Verifica i log**
   ```bash
   # Se usi systemd
   journalctl -u chiadog -f
   
   # Oppure controlla direttamente l'output
   tail -f /path/to/chiadog/chiadog.log
   ```

---

## Cosa cambia in questa versione

### Supporto Chia 2.5.7
Il parser ora riconosce il nuovo formato dei log:
```
2025-12-09T12:02:10.467 2.5.7 harvester chia.harvester.harvester: INFO challenge_hash: xxx ...72 plots were eligible for farming challengeFound 0 V1 proofs and 0 V2 qualities. Time: 0.53 s. Total 18321 plots
```

### Nuovi campi disponibili
- `found_v1_proofs_count`: Prove V1 trovate
- `found_v2_qualities_count`: Qualita V2 trovate

### Compatibilita
Il vecchio formato log continua a funzionare. Non sono necessarie modifiche alla configurazione.

---

## Risoluzione problemi

### L'aggiornamento git fallisce con conflitti
```bash
# Salva le modifiche locali
git stash
git pull origin main
git stash pop
```

### Errore "module not found"
```bash
pip install -r requirements.txt --force-reinstall
```

### Chiadog non parte dopo l'aggiornamento
1. Verifica che config.yaml sia valido:
   ```bash
   python -c "import yaml; yaml.safe_load(open('config.yaml'))"
   ```
2. Controlla i permessi del file di log Chia
3. Verifica la versione di Python: `python --version`

---

## Rollback

Se qualcosa va storto, puoi tornare alla versione precedente:

```bash
# Trova il commit precedente
git log --oneline -5

# Torna alla versione precedente
git checkout <commit-hash>

# Ripristina la configurazione
cp config.yaml.backup config.yaml
```
