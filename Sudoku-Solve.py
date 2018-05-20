"""Dieses Programm kan Sudoku lösen.

Die Struktur ist wie folgt aufgebaut: Das Brett besteht aus n*n*n Gruppen. Zum Beispiel aus 9 Reihen,
9 Zeilen und 9 Blöcken. Jede Gruppe enthält n Felder mit den möglichen Werten 1,...,n."""

def powerset(set):
    laenge = len(set)
    for index in range(1 << laenge):
        print [s[j] for j in range(laenfe) if (index & (1 << j))]

#Klassen
class Feld:
    """Die Objekte der Klasse <<Feld>> representieren die Felder auf einem Sudoku-Brett.
    Bevor der Sudokolöser anfängt sind die möglichen Werte 1 bis 9. Danach haben sie einen
    Wert. Jedes Feld gehört zu 3 <<Gruppen>>."""
    bekannte_Felder = 0
    unbekannte_Felder = 0

    def __init__(self, input_wert, anzahl_moeglichkeiten, neue_gruppe):
        self.wert = input_wert
        self.gruppen = []
        self.gruppen.append(neue_gruppe)
        if input_wert == 0: # 0 steht für "unbekannt".
            self.bekannt = False
            Feld.unbekannte_Felder += 1
            self.moeglichkeiten = [zahl+1 for zahl in range(anzahl_moeglichkeiten)]
            # print(self.moeglichkeiten)
        else:
            self.bekannt = True
            Feld.bekannte_Felder += 1
            self.moeglichkeiten = []

    def fuege_zu_gruppe(self, neue_gruppe):
        self.gruppen.append(neue_gruppe)

    def aender_wert(self, neuer_wert):
        if neuer_wert > 0:
            self.wert = neuer_wert
            self.moeglichkeiten = []
            self.bekannt = True
            Feld.bekannte_Felder += 1
            Feld.unbekannte_Felder -= 1
        else:
            print("Error: Falscher Wert!")

    def zeige_wert(self):
        return self.wert

    def entferne_moeglichkeiten(self, input_moeglichkeiten = []):
        zaehl_aenderungen = 0
        if self.wert != 0:
            for aktuelle_gruppe in self.gruppen:
                for aktuelles_feld in aktuelle_gruppe.felder:
                    if aktuelles_feld.moeglichkeiten.count(self.wert) > 0:
                        aktuelles_feld.moeglichkeiten.remove(self.wert)
                        zaehl_aenderungen += 1
                        if (not aktuelles_feld.bekannt) and (aktuelles_feld.moeglichkeiten.__len__() == 1):
                            zaehl_aenderungen += aktuelles_feld.setze_fest()
                if aktuelle_gruppe.moeglichkeiten_der_gruppe.count(self.wert) > 0: #Auch für die ganze Gruppe muss deutlich werden, dass die Zahl nicht mehr zur Verfügung steht.
                    aktuelle_gruppe.moeglichkeiten_der_gruppe.remove(self.wert)
        else:
            #if (not self.bekannt) and input_moeglichkeiten != []: #Dann werden feste Möglichkeiten für dieses Feld vorgegeben.
            print("Hallo")    
        return zaehl_aenderungen

    def setze_fest(self, input_wert = 0):
        zaehl_aenderungen = 0
        if not self.bekannt:
            if self.moeglichkeiten.__len__() == 1: # Dann ist deutlich was der Wert des Feldes ist, es kann als bekannt markiert werden.
                self.wert = self.moeglichkeiten[0] #der letzte verbleibende wert
                self.bekannt = True
                Feld.bekannte_Felder += 1
                Feld.unbekannte_Felder -= 1
                zaehl_aenderungen += 1
                zaehl_aenderungen += self.entferne_moeglichkeiten()
            else: #D.h. __len__ > 1
                if (input_wert != 0) and (not self.bekannt) and (input_wert != 0): #Dann wird ein Wert errzwungen, zum Beispiel wenn man ausschließen kann das andere Felder diesen Wert haben.
                    self.moeglichkeiten = [input_wert]
                    zaehl_aenderungen += self.setze_fest()
        return zaehl_aenderungen


class Gruppe:
    """Die Felder eines jeden Sudoku-Bretts können in Gruppen aufgeteilt werden."""
    def __init__(self, anzahl_felder = 0, neu = False):
        self.felder = [] #definiere die Felder
        self.max_anzahl = anzahl_felder
        self.moeglichkeiten_der_gruppe = [zahl+1 for zahl in range(anzahl_felder)] #Hier wird mitgezählt welche Zahlen in der Gruppe noch möglich sind.
        if neu:
            for index in range(anzahl_felder):
                self.felder.append(Feld(input_wert = 0, anzahl_moeglichkeiten = anzahl_felder, neue_gruppe = self))

    def fuege_feld_zu(self, bestehendes_feld):
        """Diese methode weist einer Gruppe bereits bestehende Felder zu."""
        self.felder.append(bestehendes_feld) #Die Gruppe nimmt das Feld auf, ...
        bestehendes_feld.fuege_zu_gruppe(neue_gruppe = self) #... das Feld merkt sich zu welcher Gruppe es gehört.

    def suche_einsame_zahlen(self):
        """Diese methode schaut ob es Zahlen gibt, die nur in einem Feld stehen können und setzt diese dann."""
        zaehl_aenderungen = 0
        for ziffer in self.moeglichkeiten_der_gruppe:
            haeufigkeit_zahl = 0
            relevante_felder = []
            for aktuelles_feld in self.felder:
                enthaelt_ziffer = aktuelles_feld.moeglichkeiten.count(ziffer) #0 falls nicht enthalten, 1 falls enthalten.
                if enthaelt_ziffer > 0:
                    haeufigkeit_zahl += enthaelt_ziffer
                    relevante_felder.append(aktuelles_feld)
            if haeufigkeit_zahl == 1: #Falles es das einzige Feld mit der Zahl ist, dan einsetzen:
                for aktuelles_feld in relevante_felder:
                    zaehl_aenderungen += aktuelles_feld.setze_fest(input_wert = ziffer)
        return zaehl_aenderungen

    def suche_zahlcluster(self):
        """Diese Methode schaut ob es n Zahlen gibt die über genau n Felder einen geschlossen cluster bilden."""
        zaehl_aenderungen = 0
        for n in range(int(self.moeglichkeiten_der_gruppe.__len__)/2 + 1): # Es reicht um für Tupel der größe n/2 zu schauen, weil die anderen Feder dann automatisch einen Cluster bilden. Bekannte Zahelen zählen können ignoriert werden.
            for index in range(1 << n):
                ziffern_index = [j for j in range(n) if (index & (1 << j))]
                count_felder = 0 #Zählt wie viele Felder das Tuper ziffern_index enthalten.
                falsch_feld_liste = [] #merkt sich welche Fleder das Tupel nicht enthalten.
                for feld in self.felder:
                    tupel_enthalten = True
                    for ziffer in ziffern_index:
                        if feld.moeglichkeiten.count(ziffer) == 0: #Dann ist die Ziffer nicht auf dem Feld...
                            tupel_enthalten = False
                            break
                    if tupel_enthalten:
                        count_felder += 1
                    else:
                        falsch_feld_liste.append(feld)
                if count_felder == n: #Dann gibt es tatsächlich so ein Tupel im Block. Die Ziffern aus diesem Tupel können auf allen anderen Feldern aus den Möglichkeiten gelöscht werden.
                    for feld in falsch_feld_liste:
                        for ziffer in ziffern_index:
                            feld.moeglichkeiten.remove(ziffer)
                            zaehl_aenderungen += 1        
        return zaehl_aenderungen

class Brett:
    """Das Sudokubrett auf dem gespielt wird."""
    def __init__(self, block_hoehe, block_breite):
        self.block = [] #Alle Blockgruppen
        self.reihe = [] #Alle Reigengruppen
        self.spalte = [] #Alle Spaltengruppen
        #Erst einmal alle Gruppen definieren. Nur die Blöcke kriegen Felder zugewiesen.
        for index_h in range(block_hoehe):
            for index_b in range(block_breite):
                self.block.append(Gruppe(anzahl_felder = block_hoehe * block_breite, neu = True))
                self.reihe.append(Gruppe())
                self.spalte.append(Gruppe())
        #Jetzt, im zweiten Schritt, werden auch der Reihengruppe und der Spaltengruppe Felder zugewiesen.
        for block_index_breit in range(block_hoehe): #Es gibt immer so viele Blöcke in der Breite, wie jeder Block hoch ist.
            for block_index_hoch in range(block_breite):
                aktueller_block = self.block[block_index_hoch + block_breite * (block_index_breit)]
                for feld_index_breit in range(block_breite): #Natürlich gibt es in jedem Block so viele Felder in der Breite, wie der Block breit ist.
                    for feld_index_hoch in range(block_hoehe):
                        aktuelles_feld = aktueller_block.felder[feld_index_breit + feld_index_hoch * block_hoehe]
                        self.reihe[block_index_hoch * block_hoehe + feld_index_hoch].fuege_feld_zu(aktuelles_feld)
                        self.spalte[block_index_breit * block_breite + feld_index_breit].fuege_feld_zu(aktuelles_feld)
    def aender_feld(self, reihen_nummer, spalten_nummer,neuer_feldwert):
        self.reihe[reihen_nummer-1].felder[spalten_nummer-1].aender_wert(neuer_wert = neuer_feldwert)
    
    def zeige_reihe(self, index_gruppe, index_feld):
        return self.reihe[index_gruppe].felder[index_feld].wert
    def zeige_moeglichkeiten_der_reihe(self, index_gruppe, index_feld):
        return self.reihe[index_gruppe].felder[index_feld].moeglichkeiten
    def zeige_spalte(self, index_gruppe, index_feld):
        return self.spalte[index_gruppe].felder[index_feld].wert
    def zeige_block(self, index_gruppe, index_feld):
        return self.block[index_gruppe].felder[index_feld].wert

def __initialize_sudoku__(hoch, breit):
    """Diese Funktion initialisiert das Spielbrett"""
    Spielbrett = Brett(hoch, breit)
    
    #Sudoku 1
    # Spielbrett.aender_feld(1,1,1)
    # Spielbrett.aender_feld(1,3,3)
    # Spielbrett.aender_feld(1,4,8)
    # Spielbrett.aender_feld(1,6,5)
    # Spielbrett.aender_feld(1,7,7)
    # Spielbrett.aender_feld(1,9,6)
    # Spielbrett.aender_feld(2,2,2)
    # Spielbrett.aender_feld(2,5,4)
    # Spielbrett.aender_feld(2,8,1)
    # Spielbrett.aender_feld(3,1,7)
    # Spielbrett.aender_feld(3,6,1)
    # Spielbrett.aender_feld(3,9,9)
    # Spielbrett.aender_feld(4,1,8)
    # Spielbrett.aender_feld(4,3,2)
    # Spielbrett.aender_feld(4,9,7)
    # Spielbrett.aender_feld(5,2,6)
    # Spielbrett.aender_feld(5,8,9)
    # Spielbrett.aender_feld(6,1,5)
    # Spielbrett.aender_feld(6,7,3)
    # Spielbrett.aender_feld(6,9,8)
    # Spielbrett.aender_feld(7,1,6)
    # Spielbrett.aender_feld(7,4,4)
    # Spielbrett.aender_feld(7,9,5)
    # Spielbrett.aender_feld(8,2,1)
    # Spielbrett.aender_feld(8,5,8)
    # Spielbrett.aender_feld(8,8,3)
    # Spielbrett.aender_feld(9,1,3)
    # Spielbrett.aender_feld(9,3,4)
    # Spielbrett.aender_feld(9,4,6)
    # Spielbrett.aender_feld(9,6,7)
    # Spielbrett.aender_feld(9,7,9)
    # Spielbrett.aender_feld(9,9,1)

    # Sudoku 2:
    Spielbrett.aender_feld(1,2,7)
    Spielbrett.aender_feld(1,5,4)
    Spielbrett.aender_feld(1,8,5)
    Spielbrett.aender_feld(2,1,1)
    Spielbrett.aender_feld(2,4,3)
    Spielbrett.aender_feld(2,6,7)
    Spielbrett.aender_feld(2,7,9)
    Spielbrett.aender_feld(2,9,6)
    Spielbrett.aender_feld(3,2,9)
    Spielbrett.aender_feld(4,2,4)
    Spielbrett.aender_feld(4,8,1)
    Spielbrett.aender_feld(5,1,7)
    Spielbrett.aender_feld(5,5,8)
    Spielbrett.aender_feld(5,9,2)
    Spielbrett.aender_feld(6,2,5)
    Spielbrett.aender_feld(6,8,9)
    Spielbrett.aender_feld(7,8,2)
    Spielbrett.aender_feld(8,1,3)
    Spielbrett.aender_feld(8,3,5)
    Spielbrett.aender_feld(8,4,2)
    Spielbrett.aender_feld(8,6,9)
    Spielbrett.aender_feld(8,9,1)
    Spielbrett.aender_feld(9,2,6)
    Spielbrett.aender_feld(9,5,1)
    Spielbrett.aender_feld(9,8,8)


    return Spielbrett

def __test_sudoku__(Das_Brett, brett_hoehe, brett_breite):
    """Diese Funktion zeigt das Brett über die verschiedenen Gruppen, um zu testen ob die Felder und die Gruppen gut gelinkt sind."""
    for ind_h in range(brett_hoehe * brett_breite):
        output_string = "|"
        for ind_b in range(brett_hoehe * brett_breite):
            output_string += " {0} |".format(Das_Brett.zeige_reihe(ind_h, ind_b))
        output_string += " -- |"
        for ind_b in range(brett_hoehe * brett_breite):
            output_string += " {0} |".format(Das_Brett.zeige_spalte(ind_b, ind_h))
        output_string += " -- |"
        index_block = int(ind_h / brett_hoehe)
        for block_switch in range(brett_hoehe):
            for ind_b in range(brett_breite):
                output_string += " {0} |".format(Das_Brett.zeige_block(index_block + brett_breite * block_switch,ind_b + (ind_h % brett_hoehe) * brett_breite))
        print(output_string)

def __test_moeglichkeiten__(Das_Brett, brett_hoehe, brett_breite):
    for ind_h in range(brett_breite * brett_hoehe):
        for ind_b in range(brett_hoehe * brett_breite):
            print("{0} -> {1}".format(Das_Brett.zeige_reihe(ind_h, ind_b), Das_Brett.zeige_moeglichkeiten_der_reihe(ind_h, ind_b)))
            

def __show_sudoku__(Das_Brett, block_hoehe, block_breite):
    """Diese Funktion zeigt das ganze Sudokuspiel."""
    

    for ind_h in range(block_hoehe * block_breite):
        if ind_h % block_hoehe == 0:
            output_string = "-"
            for ind_b in range(block_hoehe * block_breite):
                output_string += "----"
            print(output_string)
        output_string = "║"
        for ind_b in range(block_hoehe * block_breite):
            if ind_b % block_breite != 2:
                output_string += " {0} |".format(Das_Brett.zeige_reihe(ind_h, ind_b))
            else:
                output_string += " {0} ║".format(Das_Brett.zeige_reihe(ind_h, ind_b))
        print(output_string)
    
    output_string = "-"
    for ind_h in range(block_hoehe * block_breite):
        output_string += "----"
    print(output_string)

def __solve_sudoku__(Das_Brett):
    aenderungen = 0 #Sofort auf 0 setzen, weil der Default ist, dass es keine Änderungen gibt und die Schleife dann stoppen muss.

    for aktuelle_reihe in Das_Brett.reihe:
        for aktuelles_feld in aktuelle_reihe.felder:
            if aktuelles_feld.bekannt:
                aenderungen += aktuelles_feld.entferne_moeglichkeiten()
                
    print("Deze beurt zijn er {0} acties uitgevoerd.".format(aenderungen))

    while aenderungen > 0:
        aenderungen = 0 #Sofort auf 0 setzen, weil der Default ist, dass es keine Änderungen gibt und die Schleife dann stoppen muss.

        for aktuelle_reihe in Das_Brett.reihe:
            for aktuelles_feld in aktuelle_reihe.felder:
                if not aktuelles_feld.bekannt: #Das feld ist unbekannt, hier kann noch was passieren.
                    if aktuelles_feld.moeglichkeiten.__len__() == 1:
                        aenderungen = aktuelles_feld.setze_fest()
            aenderungen += aktuelle_reihe.suche_einsame_zahlen()

        for aktuelle_gruppe in Das_Brett.spalte:
            aenderungen += aktuelle_gruppe.suche_einsame_zahlen()

        for aktuelle_gruppe in Das_Brett.block:
            aenderungen += aktuelle_gruppe.suche_einsame_zahlen()
                    
        print("Deze beurt zijn er {0} acties uitgevoerd.".format(aenderungen))
        

def __main__():
    print("Dit is de Sudoko-Solver. Als je een sudoku niet kunt oplossen, hulpt je deze app uit de knel.")
    print("Ieder sudokuspel is opgebouwt uit rijen, colommen en blokken. Om het sudokuveld te maken zijn vooraal de blokken interessant.")
    print("Hoe breed en hoe hoog is ieder blok op jouw sudokuveld (b.v. 3 breed en 3 hoog)?")
    breite = 3 #input("Wat is de breedte? ")
    hoehe = 3 #input("Wat is de hoogte? ")
    print("Okay, ieder blok is dus {0} velden breed en {1} velden hoog.".format(breite, hoehe))

    sudoku_brett = __initialize_sudoku__(hoch = hoehe, breit = breite)

    __test_sudoku__(sudoku_brett, hoehe, breite)

    print("Er zijn {0} onbekende velden.".format(Feld.unbekannte_Felder))
    __solve_sudoku__(sudoku_brett)

    __show_sudoku__(sudoku_brett, hoehe, breite)

    # __test_moeglichkeiten__(sudoku_brett, hoehe, breite)

    print("Er zijn {0} onbekende velden.".format(Feld.unbekannte_Felder))
    
    if Feld.unbekannte_Felder == 0:
        print("Sudoku solved!")
    else:
        print("Sudoku unsolved.")

__main__()
