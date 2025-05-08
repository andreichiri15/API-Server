
# Tema 1 ASC - Chirimeaca Andrei 332CA

## Overview
In cadrul acestei teme, am avut de implementat un API sub forma unui server in Python (FLASK) care accepta request-uri de tip POST sau GET din partea clientilor cu privire  la un fisier de tip CSV ce contine mai multe date legate de populatia americana in mai multe state. Server-ul este capabil sa accepte un numar mare de request-uri in continuu, lucru datorat implementarii multithreaded. In continuare voi vorbi despre implementarea mea, in functie de fisierul in care se afla.
 
## task_runner.py
In acest fisier se poate gasi implementarea ce are legatura cu citirea, prelucrarea si scrierea datelor. Practic, avem implementarea ThreadPool-ului, ce contine o coada simpla in care se afla tuple-uri de tipul [tipul taskului, id-ul task-ului, datele "de intrare"].
De asemenea, aici se gaseste si implementarea Thread-ului, care are comportamentul urmator:
1. verifica daca Queue-ul de task-uri este gol si a primit semnal de thread-pool sa se opreasca, caz in care thread-ul isi opreste executia
2. daca nu este goala coada, preia un task
3. verifica tipul de operatie si o aplica pe cea potrivita
4. rezultatul operatiei il scrie intr-un fisier denumit dupa id-ul intrebuintat task-ului
5. reia loop-ul de la pasul 1

## routes.py
În acest fișier se regaseste logica legata de rutele expuse de serverul Flask. Fiecare ruta gestioneaza un anumit tip de operatie cerută de client si folosește ThreadPool-ul pentru a procesa cererea în mod asincron.

Functionalitati importante incluse:

**Rute de tip POST:**

- /api/states_mean

- /api/state_mean

- /api/best5 etc.

Aceste rute preiau un request JSON din partea clientului, care contine parametrii necesari (question, state), si trimit un job către ThreadPool. Răspunsul oferit imediat contine job_id, pe baza acestui rasp clientul poate reveni mai tarziu printr-un request de tip GET(/api/get_results/<job_id>) pentru rezultat.

**Rute de tip GET:**
- /api/get_results/<job_id> – returneaza rezultatul unui job finalizat (dacă nu este gata, raspunde cu "status": "running")

- /api/jobs – returnează toate job-urile trimise și statusul lor (running / done).

- /api/num_jobs – oferă numărul de job-uri în așteptare.

- /api/graceful_shutdown – setează un shutdown_event, ceea ce oprește toate thread-urile când au terminat task-urile curente.

Securitate la shutdown: Folosind @webserver.before_request, se opreste automat orice request de tip POST dupa ce serverul a intrat în starea de shutdown, returnand un raspuns de tip 503.

Logging: Fiecare ruta loghează la intrare parametrii primiți folosind modulul logging, in fisierul webserver.log, folosind timestamp-uri în format UTC. Acest lucru ajuta la debugging și la urmarirea comportamentului serverului.

## Unittesting

Am folosit modulul unittest pentru a testa funcțiile de prelucrare din TaskRunner, cat si corectitudinea raspunsurilor de la server pentru request-uri de la client, folosind un fișier CSV mic (test.csv). Testele valideaza corectitudinea functiilor precum:

- find_state_mean

- find_global_mean

- find_best5 etc.

Fiecare funcție este testată în izolare, folosind date controlate. Astfel ne asiguram că rezultatele calculelor sunt corecte.

