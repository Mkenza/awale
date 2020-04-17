import numpy as np
#!pip install pygame
import pygame
from copy import deepcopy
pygame.init()
#Notions de classe:
#https://openclassrooms.com/fr/courses/235344-apprenez-a-programmer-en-python/232721-apprehendez-les-classes

#Explication de l'algorithme minimax général (page 52) :
#http://stephane.ayache.perso.luminy.univ-amu.fr/zoom/cours/Cours/IA_Jeux/IAEtJeux2.pdf

#Code par Léo et Paul
#Pb: le jeu peut boucler à l'infini à la fin d'une partie (souvent lorsqu'il reste 2 graines disposées symétriquement)
# -> se pencher sur la fonction "partieFinie" et peut-être essayer d'intégrer cette fonction dans l'algo récursif minimax..
#Pb: structure d'arbre trop compliquée: (*)
#l'arbre est construit à partir d'une liste selon le principe suivant:
#les nCoupes fils de l'élément d'indice k sont d'indices k*nCoupes  + l, avec l variant entre 1 et nCoupes
#On vérifie alors (à l'aide d'un dessin par exemple) qu'il y a une bijection naturelle entre la structure d'arbre et la liste (ou tableau) de taille voulue

class terrainDeJeu:
    def __init__(self,nCoupes,nGrainesParCoupelle,profondeur) :    #Constructeur
        self.plateau = np.zeros((2,nCoupes),dtype=int)
        for i in [0,1]:
            for j in range(0,nCoupes):
                self.plateau[i][j]=nGrainesParCoupelle
        self.nCoupes = nCoupes
        self.profondeur = profondeur  # profondeur de l'exploration minimax
        self.score1 = 0
        self.score0 = 0
        self.arbre_minmax=np.zeros(((nCoupes**(profondeur+1)-1)//(nCoupes-1)))    #Somme suite géométrique (cf (*))

        
    def deplacer(self,joueur,nCoupe):
        #joueur est utilisé par la suite comme itérateur de ligne dans le tableau self.plateau
        #nCoupe est l'itérateur de colonne
        
        coupeInitiale = (joueur, nCoupe)    #Coordonnées de la coupelle choisie
        nGraines = self.plateau[joueur][nCoupe]
        self.plateau[joueur][nCoupe] = 0
        while (nGraines != 0):    #On redistribue les graines de la coupelle initiale
            if (joueur == 1):    #On est côté joueur 2
                nCoupe += 1
                if (nCoupe == self.nCoupes):    #On est au bord du plateau, on doit redistribuer chez l'autre joueur
                    joueur, nCoupe = 0, self.nCoupes-1
                if ((joueur, nCoupe) != coupeInitiale):     #On ne redistribue pas dans la coupelle initiale
                    self.plateau[joueur][nCoupe] += 1
                    nGraines -=1
            elif (joueur == 0):    #On est côté joueur 1
                nCoupe -=1
                if (nCoupe == -1):    #On est au bord du plateau, on doit redistribuer chez l'autre joueur
                    joueur, nCoupe = 1, 0
                if ((joueur, nCoupe) != coupeInitiale):    #On ne redistribue pas dans la coupelle initiale
                    self.plateau[joueur][nCoupe] += 1
                    nGraines -= 1
                    
        #On retire les graines le cas échéant et on mets les scores à jour
        if (joueur != coupeInitiale[0]): #si l'itérateur "joueur" (ne correspondant pas au joueur initial,
            adversaire = joueur          #qui est coupeInitiale[0]) correspond bien à l'adversaire, alors..
            while ((nCoupe != -1 and nCoupe != self.nCoupes) and (self.plateau[adversaire][nCoupe] == 2 or self.plateau[adversaire][nCoupe] == 3)):
                if adversaire == 1 :
                    self.score0 += self.plateau[adversaire][nCoupe]
                    self.plateau[adversaire][nCoupe] = 0
                    nCoupe -= 1
                else :
                    self.score1 += self.plateau[adversaire][nCoupe]
                    self.plateau[adversaire][nCoupe] = 0
                    nCoupe += 1

    def nourrirAdversaire(self,joueur): #détermine si le coup qui vient d'être fait est admissible pour la règle "nourrir"
        adversaire = (joueur+1)%2 #on regarde donc si il reste au moins une graine sur le terrain de l'adversaire
        admissibilite = False
        for nCoupe in range(self.nCoupes):
            admissibilite = admissibilite or self.plateau[adversaire][nCoupe] != 0
        return admissibilite #True si le coup précédent est admissible pour la règle "nourrir"
        
    def grainesRestantes(self): #On compte le nombre de graines restantes sur le plateau
        somme = 0
        for joueur in [0,1]:
            for nCoupe in range(self.nCoupes):
                somme += self.plateau[joueur,nCoupe]
        return somme
        
    
    def tourDuJoueur(self):
        joueur = 0
        coupsAdmissibles = np.zeros((self.nCoupes)) #On aura une liste de booléens:
                                               #coupsAdmissibles[nCoupe] == True ssi le coup nCoupe est admissible
        for nCoupe in range(self.nCoupes): #On détermine les coups admissibles
            coupsAdmissibles[nCoupe] = (self.plateau[joueur,nCoupe] != 0)
            
            plateau_actuel = deepcopy(self.plateau) #On garde en mémoire la situation actuelle de jeu ..
            score1_actuel = self.score1
            score0_actuel = self.score0
            
            self.deplacer(joueur,nCoupe) #.. on regarde si la règle "nourrir" est respectée pour cette valeur de nCoupe..
            coupsAdmissibles[nCoupe] = coupsAdmissibles[nCoupe] and self.nourrirAdversaire(joueur)
            
            self.plateau = plateau_actuel # ..et on récupère l'état du terrain de jeu qu'on avait mémorisé
            self.score1 = score1_actuel
            self.score0 = score0_actuel
            
        aucunAdmissible = np.zeros((self.nCoupes)) #On crée un tableau de False pour le comparer avec coupsAdmissibles
        for k in range(self.nCoupes):
            aucunAdmissible[k] = False
            
        if np.array_equal(coupsAdmissibles, aucunAdmissible): #Si le joueur ne peut pas jouer de coup admissible, la partie se termine:
            self.score0 += self.grainesRestantes() #le joueur récupère alors toutes les graines restantes
            self.plateau = np.zeros((2,self.nCoupes),dtype=int)
            
        else:
            print("C'est au tour du joueur 1. Entrez le numéro de la coupelle à jouer:")
            nCoupe = int(input())
            while nCoupe<0 or nCoupe>self.nCoupes-1 or (not coupsAdmissibles[nCoupe]):
                #cas où la coupelle n'existe pas, ou correspond à un coup non admissible
                print("Coupelle incorrecte. Entrez le numéro de la coupelle à jouer.")
                nCoupe = int(input())

            self.deplacer(joueur,nCoupe)

    def tourOrdi(self):
        self.arbre_minmax=np.zeros(((self.nCoupes**(self.profondeur+1)-1)//(self.nCoupes-1))) #(cf (*))
        nCoupe = int(self.IA_joueur1_minimax(self.profondeur)) #On détermine le coup choisi par l'IA à l'aide de l'algo minimax
        if nCoupe != -1:
            self.deplacer(1, nCoupe)
        else:    # nCoupe vaut -1 lorsque la règle "nourrir" ne pouvait pas être appliquée. La partie se termine alors:
            self.score1 += self.grainesRestantes() #l'ordi récupère les graines restantes
            self.plateau = np.zeros((2,self.nCoupes),dtype=int)
            
        #for k in range (self.profondeur): #affichage des étages k de l'arbre
        #    print(self.arbre_minmax[(self.nCoupes**(k)-1)//(self.nCoupes-1):(self.nCoupes**(k+1)-1)//(self.nCoupes-1)] )

    def partieFinie(self):
        #True si le plateau ne contient plus aucune graine
        return np.array_equal(self.plateau, np.zeros((2,self.nCoupes),dtype=int)) 
    

    def afficherPlateau(self):
        print(self.plateau)
        
    def afficherScores(self):
        print("score J1........."+str(self.score0))
        print("score MinMax....."+str(self.score1))
        
        
#Fonction principale      
    def jouer(self):
        joueur = 0
        tourJoueur0 = True    #==False si c'est à l'ordi de jouer
        while self.partieFinie() == False :
            self.afficherPlateau()
            self.afficherScores()
            
            if (tourJoueur0):
                self.tourDuJoueur()
                tourJoueur0 = False
            else:
                self.tourOrdi()
                tourJoueur0 = True
                
            print("\n")
        self.afficherPlateau()
        self.afficherScores()
        print("Partie Finie !")


    ## IA minimax
    
    def IA_joueur1_minimax(self,profondeur):

        plateau_actuel= deepcopy(self.plateau) #On garde en mémoire la situation actuelle REELLE de jeu ..
        score1_actuel = self.score1
        score0_actuel = self.score0
        
        #.. et on part pour l'exploration totale des nCoupes**profondeur 
        #situations FICTIVES de jeu atteintes au bout de n=profondeur tours..
        valeur_retenue, choix_retenu = self.minimax (self.plateau, self.score1, self.score0, 0, profondeur, True, 0) 
        self.arbre_minmax[0] = valeur_retenue

        self.plateau = plateau_actuel #On récupère l'état REEL du terrain de jeu qu'on avait mémorisé
        self.score1 = score1_actuel
        self.score0 = score0_actuel

        return choix_retenu #(i.e. nCoupe retenu)
    
    def minimax(self,plateau_noeud, score1_noeud, score0_noeud, choix, profondeur, joueurMaximisant, indice_noeud): #joueurMaximisant = True si c'est le tour du joueur 1, False sinon
        #On simule ici des situations fictives de jeu de manière récursive (l'I.A. lit en quelque sorte l'avenir pour n=profondeur tours en avance)
        if (profondeur == 0):   #cas de base
            return (score1_noeud-score0_noeud,choix) 

        if joueurMaximisant: #Ici, le joueur maximisant est l'ordinateur , correspondant donc au joueur 1!
            value = -np.inf #On va chercher à maximiser cette valeur
            
            for nCoupe in range(0,self.nCoupes): # Pour le noeud actuel, on créé nCoupes noeuds fils correspondant aux nCoupes coups possibles
                if plateau_noeud[1,nCoupe]!=0:  # Le joueur ne peut pas jouer une coupelle vide.
                    self.plateau = deepcopy(plateau_noeud) # On va faire évoluer LE plateau créé spécifiquement pour ce noeud fils, sans modifier plateau_noeud
                    self.score1 = score1_noeud # On garde donc en mémoire toutes les informations correspondant au noeud père,
                    self.score0 = score0_noeud # qui seront potentiellement réutilisées plusieurs fois à travers la boucle "for" précédente
                    
                    self.deplacer(1,nCoupe)  #joueurMaximisant = True donc c'est au tour du joueur DEUX (ordi)
    
                    if self.nourrirAdversaire(1): #Il faut que le coup du joueur ait nourri l'adversaire. Sinon, on ne retient pas ce choix de coup.

                        indice_fils = indice_noeud*self.nCoupes+ (nCoupe+1) #indice pour une liste donnant une structure d'arbre avec nCoupes noeuds fils par noeud père (cf (*))
                        valeur_fils = self.minimax(self.plateau, self.score1, self.score0, nCoupe, profondeur-1, False, indice_fils)[0] #On calcule la valeur associée au coup par récursivité
                        self.arbre_minmax[indice_fils] = valeur_fils #La construction de cet arbre des valeurs est optionnelle  
                        #et permettra de vérifier que l'algorithme fonctionne correctement en 
                        #affichant par exemple les différents étages de "self.arbre_minmax"
                        
                        if valeur_fils > value: # On sélectionne le choix de coupelle si il maximise la valeur
                            value = valeur_fils
                            choix_retenu = nCoupe

            if value != -np.inf: # Cette condition est vérifiée si au moins un des coups de la boucle "for" était admissible
                return (value, choix_retenu) #(pour les règles "nourrir" et "on ne peut pas choisir une coupelle vide")
            else:  #Cette condition est vérifiée si il est impossible de nourrir l'adversaire : 
                self.plateau = deepcopy(plateau_noeud)  
                return ((score1_noeud + self.grainesRestantes()) - score0_noeud, -1) 
                #Le jeu s'arrête et le joueur actuel (ici, le joueur 1) remporte alors toutes les graines restantes

        
        else: #i.e. si c'est le tour du joueurMinimisant (correspondant ici au joueur 0!)
            value = np.inf # On va chercher à minimiser cette valeur
            
            for nCoupe in range (0,self.nCoupes): 
# [1,nCoupe] devient [0,nCoupe]
                if plateau_noeud[0,nCoupe]!=0:    # Le joueur ne peut pas jouer une coupelle à zéro graines.
                    self.plateau = deepcopy(plateau_noeud) #même remarques que pour le joueurMaximisant
                    self.score1 = score1_noeud
                    self.score0 = score0_noeud
                    
#
                    self.deplacer(0,nCoupe)  #joueurMaximisant = False donc c'est au tour du joueur UN
                    
                    if self.nourrirAdversaire(0): #Il faut que le coup du joueur ait nourri l'adversaire. Sinon, on ne retient pas ce choix de coup.

                        indice_fils = indice_noeud*self.nCoupes+ (nCoupe+1) #indice pour une liste donnant une structure d'arbre avec nCoupes noeuds fils par noeud père
                        valeur_fils = self.minimax(self.plateau, self.score1, self.score0, nCoupe, profondeur-1, True, indice_fils)[0]
                        self.arbre_minmax[indice_fils] = valeur_fils

                        if valeur_fils < value: # On sélectionne le choix de coupelle si il minimise la valeur
                            value = valeur_fils
                            choix_retenu = nCoupe
                            
            if value != np.inf: 
                return (value, choix_retenu)
            else:  #Cette condition est vérifiée si il est impossible de nourrir l'adversaire : 
                self.plateau = deepcopy(plateau_noeud)
                return (score1_noeud - (score0_noeud + self.grainesRestantes()), -1) 
                #Le jeu s'arrête et le joueur actuel (ici, le joueur 0) remporte alors toutes les graines restantes

t = terrainDeJeu(nCoupes=6,nGrainesParCoupelle=4,profondeur=5)
for k in range(6):
    t.plateau[1,k]=0
    t.plateau[0,k]=1
    
t.jouer()