# Istruzioni per l'esecuzione
É necessario eseguire il sia il programma Client che il programma Server all'interno delle cartelle contenenti i file da inviare. 
Un file in download/upload verrá salvato all'interno della cartella di esecuzione del reciever. 
É necessario eseguire il programma ServerUDP prima di inviare richeste. 

# Comandi client
- **list** 
Visualizza sul terminale di esecuzione del Client i file presenti all’interno della cartella di esecuzione del programma Server

- **get** *filename* 
	Trasferisce il file selezionato dalla cartella del server nella cartella del client
- **put** *filename*
	 Trasferisce il file selezionato dalla cartella del server nella cartella del server
- **removelocal** *filename* 
	elimina il file selezionato dalla cartella del client 
- **removeserver** *filename* 
	elimina il file selezionato dalla cartella del client
- **exit** 
	Termina l’esecuzione del programma Client 
- **exitserver** 
	Termina l’esecuzione del programma Server
