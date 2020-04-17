import numpy as np
#!pip install pygame
import pygame
#from copy import deepcopy
pygame.init()
#-----------
# Modifications (Matthieu, 15/04):
# Modification de la représentation du terrain du jeu. Il est maintenant représenté par une seule liste.
# un seul identifiant par coupe semble plus simple à gérer qu'un couple (joueur,numero)
# Les indices de la liste correspondant à chaque coupe sont par exemple :
# [11] [10] [9] [8] [7] [6]  ligne de l'ordi (joueur 1)
# [0] [1] [2] [3] [4] [5]  ligne du joueur (joueur 0)
# Modifications de certaines fonctions de vérification des règles pour éviter les deepcopy
# Simplification de la structure de l'arbre (structure de dictionnaire contenant les fils de chaque noeud)
# On ne le construit que pour une profondeur donnée profondeurArbre (1 par défaut), ou même pas du tout
# Algo alpha beta
# Pbs : 
# Fonction qui permettrait de détecter les situations ou le jeu peut boucler à l'infini
# Pouvoir tester les performances de l'ia, par exemple sur quelques centaines de parties, combien de % 
# sont gagnées par l'ia contre un algo qui joue aléatoirement
# Améliorer la fonction d'évaluation qui est pour l'instant très basique
##-------------
# Le terrain de jeu est un tableau de deux lignes (les deux camps) et de nCoupes colonnes (les coupelles),
# contenant initialement n graines. La première constitue le camp du joueur, la seconde, celle de l'ordinateur.
# Dans chaque camp, les coupelles sont numérotées de 1 à nCoupes.
# A chaque tour, le joueur doit choisir un numéro de coupelle.
# Les graines de celle-ci sont alors transférées dans les coupes suivantes etc.
#
# modifs du 17.03 par Léo:
# -suppression de scoreGagnant, qui n'apparait pas dans les règles de base de l'Awalé
# -Pour faciliter les manipulations du code et sa compréhension, on parle maintenant
# du joueur 0 et du joueur 1 (au lieu de 1 et 2) et les coupelles sont numérotées de 0 à nCoupes-1.
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
    # [11] [10] [9] [8] [7] [6]// ligne de l'ordi (joueur 1)
    # [0] [1] [2] [3] [4] [5]// ligne du joueur (joueur 0)
    def __init__(self,nCoupes,profondeur,nGrainesParCoupelle=4) :    #Constructeur
        self.plateau = np.full(2*nCoupes,nGrainesParCoupelle)
        self.nGrainesParCoupelleInit = nGrainesParCoupelle
        self.nCoupes = nCoupes
        self.scores = [0,0] # scores[0] = score du joueur 0...
        self.tour = 0
        self.finie = False
        self.profondeurMinimax = profondeur
        self.arbreFils = {}
        
    
    #clone le terrain de jeu pour pouvoir simuler un coup par la suite
    def clone(self):
        clone = terrainDeJeu(self.nCoupes,self.profondeurMinimax,self.nGrainesParCoupelleInit)
        clone.plateau= self.plateau.copy()
        clone.scores = self.scores.copy()
        clone.tour = self.tour
        clone.finie = self.finie
        return clone
    
    #retourne l'id de la coupe suivant idCoupe sur le plateau (suivant = sens trigo)
    def coupeSuivante(self,idCoupe):
        return (idCoupe + 1)%(2*self.nCoupes)
    #retourne l'id de la coupe précédant idCoupe sur le plateau (précédant = sens horaire)
    def coupePrecedente(self,idCoupe):
        return (idCoupe - 1)%(2*self.nCoupes)
    #retourne le joueur (0 ou 1) à qui appartient la coupe idCoupe
    def joueurCoupe(self,idCoupe):
        return 0 if idCoupe < self.nCoupes else 1
    #retourne si idCoupe peut être prise (contient 2 ou 3 graines)
    def coupePrenable(self,idCoupe):
        return (self.plateau[idCoupe]==2 or self.plateau[idCoupe]==3)
    def deplacer(self,joueur,idCoupe):
        coupeInitiale = idCoupe    #id de la coupelle choisie
        nGraines = self.plateau[idCoupe]
        self.plateau[idCoupe] = 0
        while (nGraines != 0):    #On redistribue les graines de la coupelle initiale
            idCoupe = self.coupeSuivante(idCoupe)
            if (idCoupe != coupeInitiale):    #On ne redistribue pas dans la coupelle initiale
                    self.plateau[idCoupe] += 1
                    nGraines -= 1
        coupeFinale = idCoupe
        joueurCoupeFinale = self.joueurCoupe(coupeFinale)
        if (joueur != joueurCoupeFinale): 
            #on vérifie si on va affamer l'adversaire
            #si non, on prend les graines normalement
            if (self.nourrirAdversaire(joueur,coupeFinale)):
                while (self.joueurCoupe(idCoupe)==joueurCoupeFinale and self.coupePrenable(idCoupe)):
                    self.scores[joueur]+=self.plateau[idCoupe]
                    self.plateau[idCoupe]=0
                    idCoupe = self.coupePrecedente(idCoupe)
            #si on va affamer l'adversaire :
            # on ne prend aucune graine donc on ne fait rien
        self.tour=(self.tour+1)%2
        
    #On compte le nombre de graines restantes sur le plateau
    def grainesRestantes(self): 
        return np.sum(self.plateau)
    #on compte le nombre de graines restantes sur le plateau pour les coupes de joueur
    def grainesRestantesJoueur(self,joueur):
        if joueur==0:
            return np.sum(self.plateau[0:self.nCoupes])
        else:
            return np.sum(self.plateau[self.nCoupes:len(self.plateau)])
    #détermine si, dans le cas où joueur finit son coup sur la coupe coupeFinale,
    #Yson adversaire sera affamé ou pas 
    #on regarde donc si il restera au moins une graine sur le terrain de l'adversaire
    def nourrirAdversaire(self,joueur,coupeFinale): 
        adversaire = (joueur+1)%2 
        #on commence la vérification à la coupe la plus éloignée de adversaire (dans le sens horaire)
        admissible = False
        idCoupe = (self.nCoupes*(adversaire+1))-1
        while (self.joueurCoupe(idCoupe)==adversaire):
            #si idCoupe est après coupeFinale et qu'il reste des graines dedans le coup est admissible
            if (idCoupe>coupeFinale and self.plateau[idCoupe]!=0):
                admissible=True
            #si joueur peut pas prendre la coupe idCoupe le coup est admissible
            elif (not self.coupePrenable(idCoupe)):
                admissible=True
            idCoupe=self.coupePrecedente(idCoupe)
        #True si le coup est admissible pour la règle "nourrir"
        return admissible 
    #coupes admissibles que peut jouer joueur pour nourrir son adversaire
    def coupesAdmissiblesNourrir(self,joueur):
        coupesAdmissibles = []
        #on commence par la coupe la plus proche de l'adversaire (dans le sens trigo)
        idCoupe = (self.nCoupes*(joueur+1))-1
        distance = 1
        while (self.joueurCoupe(idCoupe)==joueur):
            #s'il y a plus de graines dans idCoupe que la distance qui la sépare aux coupes de l'adversaire
            #le coup est admissible, au moins une graine nourrira l'adversaire
            if self.plateau[idCoupe]>=distance:
                coupesAdmissibles.append(idCoupe)
            idCoupe = self.coupePrecedente(idCoupe)
            distance +=1
        return coupesAdmissibles
    def coupesAdmissibles(self,joueur):
        adversaire = (joueur+1)%2
        if self.grainesRestantesJoueur(adversaire) == 0:
            coupesAdmissibles = self.coupesAdmissiblesNourrir(joueur)
            #si aucun coup ne peut être joué pour nourrir l'adversaire
            if len(coupesAdmissibles)==0:
                self.scores[joueur] += self.grainesRestantes()
                self.plateau = np.zeros(2*self.nCoupes,dtype=int)
                self.finie = True
                #partie terminée
       
        #sinon toutes les coupes non vides sont admissibles
        else :
            coupesAdmissibles = [(k+joueur*self.nCoupes) for k in range(self.nCoupes) if self.plateau[(k+joueur*self.nCoupes)]>0]
            
        return coupesAdmissibles
    
    def tourDuJoueur(self):
        joueur = 0
        #si l'adversaire n'a plus de graines, il faut obligatoirement le nourrir
        coupesAdmissibles = self.coupesAdmissibles(joueur)
        print("C'est au tour du joueur 1. Entrez le numéro de la coupelle à jouer:")
        nCoupe = int(input())
        #print("coupesAdmissibles",coupesAdmissibles)
        while nCoupe<0 or nCoupe>self.nCoupes-1 or (not (nCoupe in coupesAdmissibles)):
            #cas où la coupelle n'existe pas, ou correspond à un coup non admissible
            print("Coupelle incorrecte. Entrez le numéro de la coupelle à jouer.")
            nCoupe = int(input())
        self.deplacer(joueur,nCoupe)
        self.jouer()
        
    def tourOrdi(self):
        joueur = 1
        self.profondeur  = 0
        self.value = self.alphabeta(joueur,-np.inf,np.inf)
        for idCoupe in self.arbreFils.keys():
            print("coupe = ",idCoupe," : valeur = ",self.arbreFils[idCoupe].value)
        for idCoupe in self.arbreFils.keys():
            if self.value==self.arbreFils[idCoupe].value:
                self.deplacer(joueur,idCoupe)
                break
        
        
        self.jouer()
            
    def partieFinie(self):
        #True si le plateau ne contient plus aucune graine
        limiteGagne = self.nCoupes*self.nGrainesParCoupelleInit
        self.finie = (self.grainesRestantes()==0 or self.scores[0]> limiteGagne or self.scores[1]> limiteGagne)
        return self.finie

    def afficherPlateau(self):
        print(np.array([self.plateau[self.nCoupes:len(self.plateau)][::-1],self.plateau[0:self.nCoupes]])) # [::-1] permet d'inverse la liste

    def afficherScores(self):
        print("score J1........."+str(self.scores[0]))
        print("score MinMax....."+str(self.scores[1]))

    def evaluation(self,joueur):
        adversaire = (joueur+1)%2
        return self.scores[joueur]-self.scores[adversaire]
    
    
    #Fonction principale
    def jouer(self):
        
        if (not self.partieFinie()) :
            self.afficherPlateau()
            self.afficherScores()
            if (self.tour==0):
                self.tourDuJoueur()
            else:
                self.tourOrdi()
            print("\n")
        else:
            self.afficherPlateau()
            self.afficherScores()
            print("Partie Finie !")

    #plus vraiment utile, le code du minimax est repris dans celui de la fonction alphabeta
    def minimax(self, joueurMaximisant, profondeurArbre=1): #joueurMaximisant = joueur pour lequel on veut maximiser le score (0 ou 1)
        #On simule ici des situations fictives de jeu de manière récursive (l'I.A. lit en quelque sorte l'avenir pour n=profondeur tours en avance)
        self.arbreFils = {}
        
        #on détermine les coups possibles
        #si aucun coup n'est possible cette fonction arrête aussi la partie
        coupesPossibles = self.coupesAdmissibles(self.tour) 
        
        if (self.profondeur == self.profondeurMinimax or self.finie):   #cas de base
            self.value = self.evaluation(joueurMaximisant)
            return self.value
            
        if self.tour==joueurMaximisant:
            fctComparaison = max
            self.value = - np.inf
        else:
            fctComparaison = min
            self.value = np.inf
            
        #on parcourt tous les coups possibles
        for idCoupe in coupesPossibles:
            fils=self.clone()
            fils.profondeur=self.profondeur+1
            fils.deplacer(fils.tour,idCoupe)
            fils.value = fils.minimax(joueurMaximisant)
            
            #on ne remplit effectivement l'arbre (attribut arbreFils)
            #que pour une profondeur < à profondeurArbre
            #on pourrait même ne pas le remplir du tout mais profondeurArbre = 1
            #permet d'afficher les valeurs associées à chaque coup...
            if (self.profondeur < profondeurArbre):
                self.arbreFils[idCoupe]=fils
            self.value = fctComparaison(self.value, fils.value)
        
        return self.value
    
    def alphabeta(self, joueurMaximisant, alpha, beta, profondeurArbre=1): #joueurMaximisant = joueur pour lequel on veut maximiser le score (0 ou 1)
        #On simule ici des situations fictives de jeu de manière récursive (l'I.A. lit en quelque sorte l'avenir pour n=profondeur tours en avance)
        self.arbreFils = {}
        
        #on détermine les coups possibles
        #si aucun coup n'est possible cette fonction arrête aussi la partie
        coupesPossibles = self.coupesAdmissibles(self.tour) 
        
        if (self.profondeur == self.profondeurMinimax or self.finie):   #cas de base
            self.value = self.evaluation(joueurMaximisant)
            return self.value
            
        if self.tour==joueurMaximisant:
            fctComparaison = max
            self.value = - np.inf
        else:
            fctComparaison = min
            self.value = np.inf
            
        #on parcourt tous les coups possibles
        for idCoupe in coupesPossibles:
            fils=self.clone()
            fils.profondeur=self.profondeur+1
            fils.deplacer(fils.tour,idCoupe)
            fils.value = fils.alphabeta(joueurMaximisant,alpha,beta)
            
            #on ne remplit effectivement l'arbre (attribut arbreFils)
            #que pour une profondeur < à profondeurArbre
            #on pourrait même ne pas le remplir du tout mais profondeurArbre = 1
            #permet d'afficher les valeurs associées à chaque coup...
            if (self.profondeur < profondeurArbre):
                self.arbreFils[idCoupe]=fils
                
            self.value = fctComparaison(self.value, fils.value)
            
            #coupures alpha et beta si on est sûrs d'avoir le meilleur résultat possible
            if self.tour==joueurMaximisant:
                if self.value >= beta:
                    return self.value
                alpha = fctComparaison(alpha,self.value)
            else:
                if alpha >= self.value:
                    return self.value
                beta = fctComparaison(beta,self.value)
        
        return self.value
            
        

t = terrainDeJeu(nCoupes=6,nGrainesParCoupelle=4,profondeur=8)
t.jouer()