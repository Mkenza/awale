'''
Created on 12 mars 2020

@author: Kenza
'''

#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
#!pip install pygame
import pygame
from copy import deepcopy
pygame.init()


# Le terrain de jeu est un tableau de deux lignes (les deux camps) et de nCoupes colonnes (les coupelles), contenant initialement n graines.
# La première constitue le camp de l'ordinateur, la seconde, celle du joueur.
# Dans chaque camp, les coupelles sont numérotées de 1 à nCoupes. A chaque tour, le joueur doit choisir un numéro de coupelle. Les graines de celle-ci sont alors transférées dans les coupes suivantes etc.
# Dans le code le joueur 1 est représenté par l'indice 0.

# In[2]:


#Notions de classe:
#https://openclassrooms.com/fr/courses/235344-apprenez-a-programmer-en-python/232721-apprehendez-les-classes

#Code par Léo et Paul
#Pb:L'ordi se permet de jouer une coupe à zéro graine
#Pb:Règle du "donner à manger" non-implémentée

class terrainDeJeu:
    def __init__(self,nCoupes,nGrainesParCoupelle,scoreGagnant) :    #Constructeur
        self.plateau = np.zeros((2,nCoupes),dtype=int)
        for i in [0,1]:
            for j in range(0,nCoupes):
                self.plateau[i][j]=nGrainesParCoupelle
        self.nCoupes = nCoupes
        self.scoreGagnant = scoreGagnant
        self.score1 = 0
        self.score2 = 0
        self.arbre_minmax=np.zeros(((nCoupes**(3+1)-1)//(nCoupes-1)))    #Somme suite géométrique

        
    def deplacer(self,joueur,nCoupe):
        nCoupe = nCoupe - 1
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
        if (joueur != coupeInitiale[0]):
            while ((nCoupe != -1 and nCoupe != self.nCoupes) and (self.plateau[joueur][nCoupe] == 2 or self.plateau[joueur][nCoupe] == 3)):
                if joueur == 0 :
                    self.score2 += self.plateau[joueur][nCoupe]
                    self.plateau[joueur][nCoupe] = 0
                    nCoupe += 1
                else :
                    self.score1 += self.plateau[joueur][nCoupe]
                    self.plateau[joueur][nCoupe] = 0
                    nCoupe -= 1

        
    def tourDuJoueur(self):
        joueur = 0
        print("C'est au tour du joueur 1. Entrez le numéro de la coupelle à jouer:")
        nCoupe = int(input())
        while nCoupe<1 or nCoupe>self.nCoupes or self.plateau[joueur][nCoupe-1]==0 :
            #Cas où la coupelle choisie n'exite pas, ou contient zéro graines
            print("Coupelle incorrecte. Entrez le numéro de la coupelle à jouer.")
            nCoupe = int(input())
        self.deplacer(0,nCoupe)
        
    def tourOrdi(self):
        deapness = 3
        self.arbre_minmax=np.zeros(((self.nCoupes**(deapness+1)-1)//(self.nCoupes-1)))
        nCoupe = int(self.IA_joueur1_minimax(deapness))
        self.deplacer(1, nCoupe)
        for k in range (deapness): #affichage des étages k de l'arbre
            print(self.arbre_minmax[(self.nCoupes**(k)-1)//(self.nCoupes-1):(self.nCoupes**(k+1)-1)//(self.nCoupes-1)] )

    def partieFinie(self):
        if self.score1>=self.scoreGagnant or self.score2>=self.scoreGagnant :
            return True
        return False

    def afficherPlateau(self):
        print(self.plateau)
        
    def afficherScores(self):
        print("score J1........."+str(self.score1))
        print("score MinMax....."+str(self.score2))
        
        
#Fonction principale      
    def jouer(self):
        joueur = 0
        tourJoueur = True    #==False si c'est à l'ordi de jouer
        while self.partieFinie() == False :
            self.afficherPlateau()
            self.afficherScores()
            
            if (tourJoueur):
                self.tourDuJoueur()
                tourJoueur = False
            else:
                self.tourOrdi()
                tourJoueur = True
                
            print("\n")
        self.afficherScores()
        print("Partie Finie !")


    ## IA minimax
    def minimax(self,plateau_noeud, score1_noeud, score2_noeud, choix, profondeur, joueurMaximisant, indice_noeud): #joueurMaximisant = True si c'est le tour du joueur 1, False sinon

        plateau_actuel= deepcopy(plateau_noeud) #On enregistre l'état actuel du plateau pour pouvoir le récupérer dès qu'on a 
                                                #fini d'évaluer un noeud fils. (car chaque noeud fils conduit à pleins de modifications 
                                                #du terrain sur lequel on travaille : on doit donc pouvoir retrouver le plateau_actuel 
                                                #correspondant au noeud actuel (cf (*)))

        score1_actuel = score1_noeud #même idée
        score2_actuel = score2_noeud

        if (profondeur == 0 or (score1_noeud >= self.scoreGagnant or score2_noeud>=self.scoreGagnant)):   #cas de base #modif: score1 et score2-> score1_noeud et score2_noeud
            return (score1_actuel-score2_actuel,choix)  #

        if joueurMaximisant:
            value = -np.inf
            
            for nCoupe in range(1,self.nCoupes): # Pour le noeud actuel, on créé nCoupes noeuds fils correspondant aux nCoupes coups possibles
#Le joueurMaximisant est l'ordi, donc je remplace plateau_actuel[0,nCoupe] par plateau_actuel[1,nCoupe]:
                if plateau_actuel[1,nCoupe]!=0:  # Le joueur ne peut pas jouer une coupelle vide.
                    self.plateau = deepcopy(plateau_actuel) # (*) on va faire évoluer LE plateau créé spécifiquement pour ce noeud fils, sans modifier plateau_actuel
                    self.score1 = score1_actuel
                    self.score2 = score2_actuel
#
                    self.deplacer(1,nCoupe)  #joueurMaximisant = True donc c'est au tour du joueur DEUX (ordi)

                    indice_fils = indice_noeud*self.nCoupes+ nCoupe #indice pour une liste donnant une structure d'arbre avec nCoupes noeuds fils par noeud père
                    valeur_fils = self.minimax(self.plateau, self.score1, self.score2, nCoupe, profondeur-1, False, indice_fils)[0]
                    self.arbre_minmax[indice_fils] = valeur_fils

                    if valeur_fils > value:
                        value = valeur_fils
                        choix_retenu = nCoupe

            return (value, choix_retenu)

        else:
            value = np.inf
            
            for nCoupe in range (1,self.nCoupes): 
# [1,nCoupe] devient [0,nCoupe]
                if plateau_actuel[0,nCoupe]!=0:    # Le joueur ne peut pas jouer une coupelle à zéro graines.
                    self.plateau = deepcopy(plateau_actuel)
                    self.score1 = score1_actuel
                    self.score2 = score2_actuel
#
                    self.deplacer(0,nCoupe)  #joueurMaximisant = False donc c'est au tour du joueur UN

                    indice_fils = indice_noeud*self.nCoupes+ nCoupe #indice pour une liste donnant une structure d'arbre avec nCoupes noeuds fils par noeud père
                    valeur_fils = self.minimax(self.plateau, self.score1, self.score2, nCoupe, profondeur-1, True, indice_fils)[0]
                    self.arbre_minmax[indice_fils] = valeur_fils

                    if valeur_fils < value:
                        value = valeur_fils
                        choix_retenu = nCoupe
            return (value, choix_retenu)

    def IA_joueur1_minimax(self,profondeur):

        plateau_actuel= deepcopy(self.plateau)
        score1_actuel = self.score1
        score2_actuel = self.score2

        valeur_retenue, choix_retenu = self.minimax (self.plateau, self.score1, self.score2, 0, profondeur, True, 0) 
        self.arbre_minmax[0] = valeur_retenue

        self.plateau = deepcopy(plateau_actuel)
        self.score1 = score1_actuel
        self.score2 = score2_actuel

        return choix_retenu #(i.e. nCoupe retenu)


# In[3]:


t = terrainDeJeu(nCoupes=6,nGrainesParCoupelle=4,scoreGagnant=25)


# In[ ]:


t.jouer()


# In[ ]:








        