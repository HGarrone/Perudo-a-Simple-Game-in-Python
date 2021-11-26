
print('''
#################################################################################################
####    Questo programma è stato ideato e sviluppato nella sua interezza da Hobey Garrone    ####
#################################################################################################
''')


#################################################################################################################################################
###################################                        librerie e inizializzazione                      #####################################
#################################################################################################################################################

import random
from random import randint
import tkinter as tk
from functools import wraps
import sys
import os
import subprocess
import gc
import math
from threading import Thread
import time
from functools import partial


giocatori=[]
numero_dadi_iniziali=5
puntata=[0,0]
reset=False
frase_output=""
stato_bottone_avanzare=tk.NORMAL
state_button=tk.DISABLED
#################################################################################################################################################
###################################                      classe Giocatore e istanze                         #####################################
#################################################################################################################################################



class Giocatore:
   numero_giocatori=0
   numero_totale_dadi=0
   def __init__(self, nome, numero_dadi, confidenza):
      self.nome=nome
      self.numero_dadi=numero_dadi
      self.valore_dadi=5*[0]
      self.confidenza=confidenza
      self.rientro=True
      self.frequenza_dadi={}
  
      giocatori.append(self)
      Giocatore.numero_giocatori+=1
      Giocatore.numero_totale_dadi+=5
      
   @property        
   def Scheda(self):                                    
      return f"\nGiocatore:      nome: {self.nome}\n\t\tnumero dadi: {self.numero_dadi}\n\t\tvalore dadi: {self.valore_dadi}\n\t\tconfidenza: {self.confidenza}\n"
  
   @property
   def riscala_confidenza(self):
      self.confidenza=int(self.confidenza*numero_totale_dadi/(5*len(giocatori)))
      return self.confidenza
  
   @property
   def tira_dadi(self):           
      self.frequenza_dadi={}
      for i in range(0,self.numero_dadi):
         self.valore_dadi[i]=randint(1,6)
      for i in range(1,7):
         self.frequenza_dadi.setdefault(i,0)
         for j in range(0,len(self.valore_dadi)):
            if self.valore_dadi[j]==i:
               self.frequenza_dadi[i]+=1
      return self.frequenza_dadi
      
   @property
   def rimuovi_dado(self):
      if self.numero_dadi>0:
         self.numero_dadi-=1
      else:
         self.numero_dadi=0
      try:
         self.valore_dadi.pop()
      except Exception:
         print(f"\n{self.nome} non ha altri dadi da rimuovere.")
      Giocatore.numero_totale_dadi-=1
      
   @property
   def guadagno_dado(self):
      if self.numero_dadi<5:
         self.numero_dadi+=1
         self.valore_dadi.append(0)
         Giocatore.numero_totale_dadi+=1


         

# creazione npc
def creazione_giocatore(nome_giocatore):
    num_dadi_giocatore=numero_dadi_iniziali
    conf_giocatore=int(math.ceil(randint(1,5)/(num_npc)))
    globals()[nome_giocatore]=Giocatore(nome_giocatore, num_dadi_giocatore, conf_giocatore)
    setattr(creazione_giocatore, "nome", globals()[nome_giocatore])
    
#################################################################################################################################################
###################################                         funzioni per il gioco                           #####################################
#################################################################################################################################################
  
def stop():
    global avanzamento
    avanzamento=False
    
def avanza():
    global avanzamento
    avanzamento=True
    
def conta_dadi():
   tutti_dadi=[]
   for g in giocatori:
      tutti_dadi+=g.valore_dadi
   quanti_dadi={}
   for i in range(1,7):
      quanti_dadi.setdefault(i,0)
      for j in range(0,len(tutti_dadi)):
         if tutti_dadi[j]==i:
            quanti_dadi[i]+=1
   #print(f"\nLista totale dadi={tutti_dadi}, \nfrequenza totale dei dadi={quanti_dadi}")
   return quanti_dadi
 
      
def bugiardo(soggetto, oggetto, puntata):
   dadi_freq_dict=conta_dadi()
   tg.mostra_dadi
   print(f"\n{soggetto.nome} da del bugiardo a {oggetto.nome} sulla sua puntata {puntata}...\n")
   if puntata[1]!=1:
      if puntata[0]>dadi_freq_dict[puntata[1]]+dadi_freq_dict[1]:
         oggetto.rimuovi_dado
         print(f"e ha ragione perchè ci sono {dadi_freq_dict[puntata[1]]+dadi_freq_dict[1]} tra lame e dadi da {puntata[1]}.\n {oggetto.nome} perde un dado.\n")
      else:
         soggetto.rimuovi_dado
         print(f", ma si sbaglia perchè ci sono {dadi_freq_dict[puntata[1]]+dadi_freq_dict[1]} tra lame e dadi da {puntata[1]}.\n {soggetto.nome} perde un dado.")
   else:
      if puntata[0]>dadi_freq_dict[puntata[1]]:
         oggetto.rimuovi_dado
         print(f"e ha ragione perchè ci sono {dadi_freq_dict[puntata[1]]} dadi da {puntata[1]}.\n {oggetto.nome} perde un dado.")
      else:
         soggetto.rimuovi_dado
         print(f", ma si sbaglia perchè ci sono {dadi_freq_dict[puntata[1]]} dadi da {puntata[1]}.\n {soggetto.nome} perde un dado.")
   global bugiardo_frase_uscita
   def bugiardo_frase_uscita():
       frase_output=f"\n{soggetto.nome} da del bugiardo a {oggetto.nome} sulla sua puntata {puntata}...\n"
       if puntata[1]!=1:
          if puntata[0]>dadi_freq_dict[puntata[1]]+dadi_freq_dict[1]:
             frase_output=frase_output+f"e ha ragione perchè ci sono {dadi_freq_dict[puntata[1]]+dadi_freq_dict[1]} tra lame e dadi da {puntata[1]}.\n {oggetto.nome} perde un dado."
          else:
             frase_output=frase_output+f", ma si sbaglia perchè ci sono {dadi_freq_dict[puntata[1]]+dadi_freq_dict[1]} tra lame e dadi da {puntata[1]}.\n {soggetto.nome} perde un dado."
       else:
          if puntata[0]>dadi_freq_dict[puntata[1]]:
             frase_output=frase_output+f"e ha ragione perchè ci sono {dadi_freq_dict[puntata[1]]} dadi da {puntata[1]}.\n {oggetto.nome} perde un dado."
          else:
             frase_output=frase_output+f", ma si sbaglia perchè ci sono {dadi_freq_dict[puntata[1]]} dadi da {puntata[1]}.\n {soggetto.nome} perde un dado."
       return frase_output
   return True
   
   
def calza(soggetto, puntata):
   dadi_freq_dict=conta_dadi()
   tg.mostra_dadi
   if puntata[0]==dadi_freq_dict[puntata[1]]:
      if soggetto.numero_dadi>0 and soggetto.numero_dadi<5:
         print(f"\n{soggetto.nome} ha calzato con successo un {puntata} e ottiene un dado!")
         soggetto.guadagno_dado
      elif soggetto.numero_dadi==0 and soggetto.rientro==True:
         print (f"\n{soggetto.nome} ha calzato con successo un {puntata} e rientra in partita con un dado!")
         soggetto.guadagno_dado
         soggetto.rientro=False
      else:
         print(f"\n{soggetto.nome} ha calzato con successo un {puntata} per la gloria!")
   else:
      if soggetto.numero_dadi==0:
         soggetto.rientro=False  
      else:
         print(f"\n{soggetto.nome} ha calzato il {puntata} e ha fallito, quindi perde un dado!")
         soggetto.rimuovi_dado
   global calza_frase_uscita
   def calza_frase_uscita():
      frase_output=""
      if puntata[0]==dadi_freq_dict[puntata[1]]:
          if soggetto.numero_dadi>0 and soggetto.numero_dadi<5:
             frase_output=f"\n{soggetto.nome} ha calzato con successo un {puntata} e ottiene un dado!"
          elif soggetto.numero_dadi==0 and soggetto.rientro==True:
             frase_output=f"\n{soggetto.nome} ha calzato con successo un {puntata} e rientra in partita con un dado!"
          else:
             frase_output=f"\n{soggetto.nome} ha calzato con successo un {puntata} per la gloria!"
      else:
         if soggetto.numero_dadi!=0:
            frase_output=f"\n{soggetto.nome} ha calzato il {puntata} e ha fallito, quindi perde un dado!"   
         else:            
            frase_output=f"\n{soggetto.nome} ha calzato il {puntata} e ha fallito.\n Perde la possibilità di rientrare ed è fuori definitivamente!"
      return frase_output
   return True   
   
def passa_alle_lame(soggetto, puntata):
   if puntata[1]!=1:
       puntata[1]=1
       puntata[0]=int(math.ceil(puntata[0]/2))
   elif puntata[1]==0:
       frase_output=f"Sei il primo a puntare, non puoi passare alle lame!\nL puntata precedente è{puntata}!\n"
       print(f"Sei il primo a puntare, non puoi passare alle lame!\nL puntata precedente è{puntata}!\n")
       tg.giocata.set(frase_output)
       tg.annuncio_giocata
   else:
       frase_output=f"\nSi stanno già giocando le lame.\nL puntata precedente è{puntata}!\n"
       print(f"\nSi stanno già giocando le lame.\nL puntata precedente è{puntata}!\n")
       tg.giocata.set(frase_output)
       tg.annuncio_giocata
   return puntata

def gioca(soggetto, oggetto, puntata):
   reset=False
   dado_massima_frequenza=0
   ng=Giocatore.numero_giocatori
   ntd=Giocatore.numero_totale_dadi
   ndg=soggetto.numero_dadi
   menzogna=randint(2,5)
   if soggetto!=utente:
       if soggetto.numero_dadi>0:
          for i in soggetto.frequenza_dadi.keys():
             if soggetto.frequenza_dadi[i]>dado_massima_frequenza:
                dado_massima_frequenza=i            
          if puntata[0]==0 or puntata[1]==0:
             puntata[0]=int(ng/2)+randint(0,int(ng/2))
             puntata[1]=randint(2,6)
             frase_output=f"\n{soggetto.nome} dice {puntata}!\n"
             print(f"\n{soggetto.nome} dice {puntata}!\n")
          elif soggetto.numero_dadi<3 and soggetto.confidenza>2 and puntata[0]>int((ntd-ndg)/6) + soggetto.frequenza_dadi[puntata[1]] - int(soggetto.confidenza/2) and puntata[0]>int((ntd-ndg)/6) + soggetto.frequenza_dadi[puntata[1]] + int(soggetto.confidenza/2): 
             calza(soggetto, puntata)
             frase_output=calza_frase_uscita()
             reset=True
          elif puntata[0]!=0 and puntata[1]!=0:
             if puntata[1]==6 and puntata[0] <= int(2*(ntd-ndg)/6) + soggetto.frequenza_dadi[6] - soggetto.confidenza:
                puntata[0]=puntata[0]+1
                puntata[1]=6
                frase_output=f"\n{soggetto.nome} dice {puntata}!\n"
                print(f"\n{soggetto.nome} dice {puntata}!\n")
             elif puntata[1]==6 and puntata[0] > int(2*(ntd-ndg)/6) + soggetto.frequenza_dadi[6] and puntata[0] < int(2*(ntd-ndg)/6) + soggetto.frequenza_dadi[6] + soggetto.confidenza:
                passa_alle_lame(soggetto, puntata)
                frase_output=f"\n{soggetto.nome} dice {puntata}!\n"
                print(f"\n{soggetto.nome} dice {puntata}!\n")
             elif puntata[1]==6 and puntata[0] > int(2*(ntd-ndg)/6) + soggetto.frequenza_dadi[6] - soggetto.confidenza and puntata[0] <= int(2*(ntd-ndg)/6) + soggetto.frequenza_dadi[6]:
                puntata[0]=puntata[0]+1
                puntata[1]=random.choice([dado_massima_frequenza,menzogna]) 
                frase_output=f"\n{soggetto.nome} dice {puntata}!\n"
                print(f"\n{soggetto.nome} dice {puntata}!\n")            
             elif puntata[1]==6 and puntata[0] >= int(2*(ntd-ndg)/6) + soggetto.frequenza_dadi[6] + soggetto.confidenza:
                bugiardo(soggetto, oggetto, puntata) 
                frase_output=bugiardo_frase_uscita()
                reset=True       
             elif puntata[1]==1 and puntata[0] <= int((ntd-ndg)/6) + soggetto.frequenza_dadi[1] - soggetto.confidenza/2:
                puntata[0]=puntata[0]+1
                puntata[1]=dado_massima_frequenza
                frase_output=f"\n{soggetto.nome} dice {puntata}!\n"
                print(f"\n{soggetto.nome} dice {puntata}!\n")
             elif puntata[1]==1 and puntata[0] > int((ntd-ndg)/6) + soggetto.frequenza_dadi[1] - soggetto.confidenza/2 and puntata[0] < int((ntd-ndg)/6) + soggetto.frequenza_dadi[1] + soggetto.confidenza/2:
                puntata[0]=puntata[0]+1
                puntata[1]=1
                frase_output=f"\n{soggetto.nome} dice {puntata}!\n"
                print(f"\n{soggetto.nome} dice {puntata}!\n")
             elif puntata[1]==1 and puntata[0] >= int((ntd-ndg)/6) + soggetto.frequenza_dadi[1] + soggetto.confidenza/2:
                bugiardo(soggetto, oggetto, puntata)
                frase_output=bugiardo_frase_uscita()
                reset=True
             elif (puntata[1]==dado_massima_frequenza or puntata[1]==menzogna) and puntata[0] < int(2*(ntd-ndg)/6) + soggetto.frequenza_dadi[puntata[1]] + soggetto.confidenza:
                puntata[0]=puntata[0]+2
                frase_output=f"\n{soggetto.nome} dice {puntata}!\n"
                print(f"\n{soggetto.nome} dice {puntata}!\n")
             elif puntata[0] >= int(2*ntd/6) + soggetto.frequenza_dadi[puntata[1]] + soggetto.confidenza:
                bugiardo(soggetto, oggetto, puntata)
                frase_output=bugiardo_frase_uscita()
                reset=True
             elif puntata[0]>1 and puntata[0]<6:
                puntata[1]=puntata[1]+1
                frase_output=f"\n{soggetto.nome} dice {puntata}!\n"
                print(f"\n{soggetto.nome} dice {puntata}!\n")
             else:
                if puntata[1]==1:
                   puntata[0]=2*puntata[0]+1
                else:
                   puntata[0]=puntata[0]+1
                frase_output=f"\n{soggetto.nome} dice {puntata}!\n"
                print(f"\n{soggetto.nome} dice {puntata}!\n")
          #print(f"\nmax dado di {soggetto.nome}={dado_massima_frequenza}, menzogna={menzogna}")   
       elif soggetto.numero_dadi==0 and soggetto.rientro==True and puntata[0]!=0 and puntata[1]!=0:
          if puntata[0]>int((ntd-ndg)/6) + soggetto.frequenza_dadi[puntata[1]] - soggetto.confidenza/2 and puntata[0]>int((ntd-ndg)/6) + soggetto.frequenza_dadi[puntata[1]] + soggetto.confidenza/2:
             calza(soggetto, puntata)
             frase_output=calza_frase_uscita()
          else:
             frase_output=f"\n{soggetto.nome} non ha dadi per giocare, ma può ancora calzare!"
             print(f"\n{soggetto.nome} non ha dadi per giocare, ma può ancora calzare!")
       else:
          frase_output=f"\n{soggetto.nome} è fuori dalla partita e non può rientrare!"
          print(f"\n{soggetto.nome} è fuori dalla partita e non può rientrare!")
   setattr(gioca,"reset",reset)
   tg.giocata.set(frase_output)
   tg.annuncio_giocata
   return puntata

def puntata_utente(puntata, input_puntata):
    if input_puntata.get():
        frase_puntata=input_puntata.get()
        puntata_ingresso=frase_puntata.split(" ")
        try:
            if len(puntata_ingresso)==2 and (int(puntata_ingresso[1])>1 and int(puntata_ingresso[1])<7 and ((int(puntata_ingresso[0])==puntata[0] and int(puntata_ingresso[1])>puntata[1]) or int(puntata_ingresso[0])>puntata[0])) or (int(puntata_ingresso[1])==1 and int(puntata_ingresso[0])>=int(math.ceil(puntata[0]/2))):
                print(f"puntata in ingresso= {puntata_ingresso}")
                puntata[0]=int(puntata_ingresso[0])
                puntata[1]=int(puntata_ingresso[1])
            else:
                print(f"ciò che dici non va bene come puntata!, {puntata_ingresso}")
        except Exception as err:
            print(err, puntata_ingresso)
    return puntata
 
 
def gioco_utente(azione, soggetto, oggetto, puntata, input_puntata):
    global reset
    global azione_scelta
    azione_scelta=False
    reset=False
    if azione=="bugiardo":
        bugiardo(soggetto, oggetto, puntata)
        frase_output=bugiardo_frase_uscita()
        reset=True
        azione_scelta=True
        #avanza()
    elif azione=="calza":
        calza(soggetto, puntata)
        frase_output=calza_frase_uscita()
        reset=True
        azione_scelta=True
        #avanza()
    elif azione=="passa_alle_lame":
        passa_alle_lame(soggetto, puntata)
        frase_output=f"\n{soggetto.nome} dice {puntata}!\n"
        print(f"\n{soggetto.nome} dice {puntata}!\n")
        azione_scelta=True
        #avanza()
    elif azione=="puntata_utente":
        frase_puntata=input_puntata.get()
        puntata_ingresso=frase_puntata.split(" ")
        if len(puntata_ingresso)==2 and (int(puntata_ingresso[1])>1 and int(puntata_ingresso[1])<7 and ((int(puntata_ingresso[0])==puntata[0] and int(puntata_ingresso[1])>puntata[1]) or int(puntata_ingresso[0])>puntata[0])) or (int(puntata_ingresso[1])==1 and int(puntata_ingresso[0])>=int(math.ceil(puntata[0]/2))):
            puntata_utente(puntata, input_puntata)
            frase_output=f"\n{soggetto.nome} dice {puntata}!\n"
            print(f"\n{soggetto.nome} dice {puntata}!\n")
            azione_scelta=True
            #avanza()
        else:
            print("La tua puntata non è valida, riprova!")
            frase_output=f"La tua puntata non è valida, riprova!\nLa puntata precedente è {puntata}"
            tg.giocata.set(frase_output)
            tg.annuncio_giocata
            stop()
    else:
        frase_output=f"Tocca a te, {soggetto.nome}!\nLa puntata precedente è {puntata}"
        print(f"Tocca a te, {soggetto.nome}!\nLa puntata precedente è {puntata}")
        tg.giocata.set(frase_output)
        tg.annuncio_giocata
        stop()
    setattr(gioco_utente,"azione_scelta",azione_scelta)
    setattr(gioco_utente,"reset",reset)
    tg.giocata.set(frase_output)
    tg.annuncio_giocata
    return puntata
  
    
def aggiornamento_avanza_utente(soggetto, azione_scelta):
    global stato_bottone_avanzare
    global state_button
    state_button=tk.NORMAL
    if soggetto!=utente:
        stato_bottone_avanzare=tk.NORMAL
    else:
        azione_scelta=gioco_utente.azione_scelta
        #print(f"\nazione_scelta={azione_scelta}\n")
        if azione_scelta == True:
            stato_bottone_avanzare=tk.NORMAL
            state_button=tk.DISABLED
        else:
            stato_bottone_avanzare=tk.DISABLED
            state_button=tk.NORMAL
    setattr(aggiornamento_avanza_utente, "state_button", state_button)
    return azione_scelta
#################################################################################################################################################        
##################################                             tavolo e bottoni giocatore                           #############################
#################################################################################################################################################

class tavolo_gioco:
    def __init__(self, table):
        #creazione finestra
        table.geometry("1000x700")
        table.resizable(True,True)
        table.title("TAVOLO DELLA PARTITA")
        table.configure(background="red")
        self.table=table
        self.giocata=tk.StringVar()
    
    @property
    def annuncio_giocata(self):
        #stringa con quel che accade 
        a=2
        b=2
        outputFrame = tk.Frame(self.table, bg="red", width=400, height=100)
        outputFrame.grid(row=a, column=b, sticky="n", pady=10, padx=10)
        outputFrame.grid_propagate(False)
        outputFrame.columnconfigure(0, weight=10)
        outputFrame.rowconfigure(0, weight=10)
        self.textarea=tk.Text(outputFrame, font=("Franklin Gothic Medium",20))
        self.textarea.grid(sticky="n")
        self.label_giocata=tk.Label(self.textarea, textvariable=self.giocata, fg="black", bg="white", anchor="n")      
        self.label_giocata.grid(row=a, column=b, pady=10, padx=10)
        
    @property
    def label_npc(self):    
        actual_row=0        
        shift=0
        a=2
        b=4
        global playerFrame
        playerFrame=[0]*(Giocatore.numero_giocatori)
        for k in range(0, Giocatore.numero_giocatori-1):
            i=k+1
            playerFrame[i]=tk.Frame(self.table, bg="red", width=160, height=100)
            playerFrame[i].grid(row=actual_row-a*(1-i%2), column=b*(1-i%2), sticky="n", pady=10, padx=10)
            playerFrame[i].grid_propagate(False)
            label_giocatori_i=tk.Label(playerFrame[i], text=f"{giocatori[k].nome}", bg="green", fg="black", font=("Franklin Gothic Medium",20))   
            #label_giocatori_i.grid(row=actual_row-a*(1-i%2), column=b*(1-i%2), sticky="n", pady=10, padx=10)
            label_giocatori_i.grid(row=1, column=1, sticky="n")
            for n in range(1,a+1):
                if i%2==0 and n==1:
                    shift=-a+1
                else:
                    shift=1
                for j in range(1,b):
                    label_vuote_inj=tk.Label(self.table, text=f"                        ", bg="red", fg="black")
                    label_vuote_inj.grid(row=actual_row, column=j, sticky="n", pady=10, padx=10)
                actual_row+=shift
                #print(f"giocatore_{i} sulla riga={actual_row}, {a*(1-i%2)}, {shift}")
                
                
    @property
    def mostra_dadi(self):
        a=2
        actual_row=int(a/2)
        b=4
        global label_dadi
        label_dadi=[0]*(Giocatore.numero_giocatori)
        for k in range(0, Giocatore.numero_giocatori-1):
            i=k+1
            label_dadi[k]=tk.Label(playerFrame[i], text=f"{giocatori[k].valore_dadi}", bg="black", fg="white", font=("Franklin Gothic Medium",20))                 
            label_dadi[k].grid(row=2, column=1, sticky="n")
            actual_row+=int((a/2+2)*(1-i%2))
              
       
    def utente(self, soggetto, oggetto, puntata):
        row_utente=5
        label_utente=tk.Label(self.table, text=f"{giocatori[num_npc].nome}", bg="green", fg="black", font=("Franklin Gothic Medium",20))   
        label_utente.grid(row=row_utente, column=2, sticky="s", pady=10, padx=10)
            
        state_button=""
        if soggetto==utente:
            try:
                state_button=aggiornamento_avanza_utente.state_button
                state_button_calza=state_button
            except Exception:
                state_button=tk.NORMAL
                state_button_calza=state_button
            if utente.numero_dadi==0 and utente.rientro==False:
                state_button=tk.DISABLED
                state_button_calza=state_button
            elif utente.numero_dadi==0 and utente.rientro==True:
                state_button=tk.DISABLED
                state_button_calza=tk.NORMAL
        else:
            state_button=tk.DISABLED
            state_button_calza=state_button
            
        global input_puntata
        input_puntata=[0,0]
        
        input_puntata=tk.Entry(self.table)
        input_puntata.grid(row=row_utente+2, column=0, pady=10, padx=10)
        
        bottone_calza=tk.Button(self.table, text="Calza", relief=tk.SUNKEN, command=partial(gioco_utente, "calza", soggetto, oggetto, puntata, input_puntata), state=state_button_calza)           
        bottone_calza.grid(row=row_utente+1,column=3, pady=20, padx=10)
        
        bottone_bugiardo=tk.Button(self.table, text="Bugiardo", relief=tk.SUNKEN, command=partial(gioco_utente, "bugiardo", soggetto, oggetto, puntata, input_puntata), state=state_button)         
        bottone_bugiardo.grid(row=row_utente+1,column=2, pady=20, padx=10)
        
        bottone_lame=tk.Button(self.table, text="Passa alle lame", relief=tk.SUNKEN, command=partial(gioco_utente, "passa_alle_lame", soggetto, oggetto, puntata, input_puntata), state=state_button)
        bottone_lame.grid(row=row_utente+1,column=1, sticky="e", pady=20, padx=10) 
        
        bottone_punta=tk.Button(self.table, text="Dichiara", relief=tk.SUNKEN, command=partial(gioco_utente, "puntata_utente", soggetto, oggetto, puntata, input_puntata), state=state_button)
        bottone_punta.grid(row=row_utente+1,column=0, pady=20, padx=10)
        
        global label_dadi_utente
        try:
            label_dadi_utente.grid_forget()
            label_dadi_utente.destroy()
        except Exception as err:
            print(f"\nNon trovo i dadi dell'utente, {err}\n")
            
        label_dadi_utente=tk.Label(self.table, text=f"{utente.valore_dadi}", bg="black", fg="white", font=("Franklin Gothic Medium",20))   
        label_dadi_utente.grid(row=row_utente+2, column=2, sticky="n", pady=10, padx=10)
        
    def avanzare(self, soggetto):
        global stato_bottone_avanzare
        if soggetto==utente and utente.numero_dadi==0:
            stato_bottone_avanzare=tk.NORMAL
        row_utente=5
        #print("ma la funzione tg.avanzare viene chiamata in continuazione?")        
        bottone_avanzamento=tk.Button(self.table, text="Prossimo turno", relief=tk.SUNKEN, command=avanza, state=stato_bottone_avanzare)
        bottone_avanzamento.grid(row=row_utente,column=4, sticky="s", pady=20, padx=10)
        
    @property
    def nascondi_dadi(self):
        for k in range(0, Giocatore.numero_giocatori-1):
            try:
                label_dadi[k].grid_forget()
                label_dadi[k].destroy()  
            except Exception as err:
                print(f"\nNon ci sono dadi da nascondere, {err}\n")
                
        
#################################################################################################################################################
###################################                             settaggi partita                            #####################################
#################################################################################################################################################

# creazione npc
input_num_npc=int(input("\nContro quanti giocatori vuoi giocare?(da 1 a 6)\n"))
if input_num_npc>0 and input_num_npc<7:
    num_npc=input_num_npc

for i in range(1, num_npc+1):
    creazione_giocatore(f"giocatore_{i}")
    
# test creazione del giocatore utente
utente=Giocatore("utente", numero_dadi_iniziali, 0)
    
numero_totale_dadi=Giocatore.numero_totale_dadi
partita=True
avanzamento=True
molti_giocatori=True
turno=randint(0, Giocatore.numero_giocatori-1)

for g in giocatori:
   g.tira_dadi
   #print(g.Scheda)
   #print(g.frequenza_dadi)
   
# istanziamento GUI tavolo di gioco
table=tk.Tk()
tg=tavolo_gioco(table)
tg.label_npc
scelta_utente="nessuna"
azione_scelta=""
giro=0

#################################################################################################################################################        
##################################                               loop della partita                                 #############################
#################################################################################################################################################

#print(f"molti_giocatori={molti_giocatori}\n")
while molti_giocatori:   
    #print(f"partita={partita}, avanzamento={avanzamento}\n")
    if partita and avanzamento:
      
       giro+=1
       #giocatori e turno
       global soggetto
       soggetto=giocatori[turno]
       j=1
       while True:
          if j<len(giocatori):
             try:
                if giocatori[turno-j].numero_dadi>0:
                   oggetto=giocatori[turno-j]
                   break
             except Exception:
                if giocatori[-j].numero_dadi>0:
                   oggetto=giocatori[-j]
                   break
             else:
                j+=1
          else:
             print("--------------------------------------------------------")
             print(f"\n---------------{g.nome} vince la partita!---------------\n")
             print("--------------------------------------------------------\n")
             partita=False
             break
           
       
       if reset:
          puntata=[0,0]
          turno-=2      
          print("\n\n---------------------------------------------------------------------------------------------------")
          print("\n--------------------------------------Nuovo giro-------------------------------------\n")
          print("---------------------------------------------------------------------------------------------------\n")
          tg.nascondi_dadi
          print("\nRollando i dadi...\n\n")
          frase_output="\nRollando i dadi...\n"
          tg.giocata.set(frase_output)                       
          tg.annuncio_giocata
          for g in giocatori:
             g.tira_dadi
             print(g.Scheda)
             print(g.frequenza_dadi)
          reset=False
       else:
          #gioco 
          tg.utente(soggetto, oggetto, puntata)
          if soggetto!=utente:
              puntata=gioca(soggetto, oggetto, puntata)
          else:
              puntata=gioco_utente(scelta_utente, soggetto, oggetto, puntata, input_puntata)
              azione_scelta=gioco_utente.azione_scelta
          
          aggiornamento_avanza_utente(soggetto, azione_scelta)
          tg.avanzare(soggetto)
          turno=(turno+1)%len(giocatori) 
          #print("\nnuovo turno=",turno)
          #ritiro dei dadi se 
          try:
             if soggetto==utente:
                reset=gioco_utente.reset
                print("reset utente=", reset)
             else:
                reset=gioca.reset
                print("reset npc=", reset)
          except Exception:
             print("reset exception=", reset)
             reset=False
             
       #print("\nreset=",reset)
       
       for g in giocatori:
          if g.numero_dadi==Giocatore.numero_totale_dadi:
             print("\n\n---------------------------------------------------------------------------------------------------")
             print(f"\n--------------------------------------{g.nome} vince la partita!-------------------------------------\n")
             print("---------------------------------------------------------------------------------------------------\n")
             tg.giocata.set(f"--------------------------------------------------------\n---------------{g.nome} vince la partita!---------------\n--------------------------------------------------------") 
             partita=False    
             molti_giocatori=False
       
       stop()       
       table.update()    
       count=0       
    else:
       # inizializzazione ogni prima volta che si passa dal if del gioco a questo
       if count==0:
           azione_scelta=False
           azione_scelta_prec=False
           soggetto_prec=""
           count+=1
           
       # aggiornamento del bottone per avanzare solo quando serve, cioè se varia soggetto o azione scelta
       azione_scelta=aggiornamento_avanza_utente(soggetto, azione_scelta)
       if azione_scelta!= azione_scelta_prec or soggetto!=soggetto_prec:
           tg.avanzare(soggetto)
           tg.utente(soggetto, oggetto, puntata)
           
       azione_scelta_prec=aggiornamento_avanza_utente(soggetto, azione_scelta)
       soggetto_prec=soggetto
       
       # aggiornmento costante della GUI
       table.update()           
       continue       

   
   
if __name__=="__main__":
    table.mainloop()
     

