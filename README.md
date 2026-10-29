# Perudo

Perudo, il gioco di dadi e bluff delle Ande, contro avversari controllati dal computer.

## Versione web (Streamlit)

```
pip install -r requirements.txt
streamlit run streamlit_app.py
```

- Da 1 a 6 avversari, tre livelli di difficoltà (Facile, Normale, Difficile)
- Tavolo in panno verde, dadi disegnati, lame (gli 1) in oro
- Alla chiamata di «Bugiardo!» o «Calza!» si scoprono tutti i dadi e si evidenziano quelli che contano
- Aiuto facoltativo: probabilità che una puntata sia vera, calcolata solo sui tuoi dadi

Le regole e gli avversari sono in `perudo_engine.py`, separati dall'interfaccia.

## Regole

- Ognuno ha 5 dadi nascosti. A turno si dichiara quanti dadi di un valore ci sono in tutto sul tavolo.
- Le lame (gli 1) sono jolly, tranne quando si punta proprio sulle lame.
- Si rilancia con più dadi, oppure con gli stessi dadi e un valore più alto. Per passare alle lame bastano metà dei dadi (per eccesso); per tornare dalle lame ne servono il doppio + 1.
- «Bugiardo!»: si scoprono i dadi e perde un dado chi ha torto.
- «Calza!»: se la puntata è esatta si guadagna un dado (massimo 5), altrimenti se ne perde uno. Chi è rimasto senza dadi può calzare una volta per rientrare.
- Vince l'ultimo giocatore con dei dadi. La regola del «palifico» non è inclusa.

[Regole complete su Wikipedia](https://it.wikipedia.org/wiki/Perudo)

## Versione originale

`Perudo.py` è la prima versione del gioco, con interfaccia tkinter da avviare da terminale (`python Perudo.py`).
