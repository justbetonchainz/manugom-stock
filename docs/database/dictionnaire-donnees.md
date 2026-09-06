# Dictionnaire de données

Les dates `date_creation`/`date_modification` sont respectivement automatiques à l'insertion et à chaque modification. `id` est une clé primaire `BigAutoField` dans chaque table.

| Table | Champ | Type | Obligatoire | Clé/unique | Défaut | Validation / description |
|---|---|---|---|---|---|---|
| User | username | varchar(150) | oui | U | — | identifiant Django |
| User | email | varchar(254) | oui | U | — | adresse de connexion/contact |
| User | role | varchar(20) | oui | index | CLIENT | ADMIN, EMPLOYEE, CLIENT |
| ProfilUtilisateur | utilisateur_id | bigint | oui | FK,U | — | profil 0..1 de l'utilisateur |
| Client | numero | varchar(20) | oui | U | généré | `CLI-00001` |
| Client | utilisateur_id | bigint | non | FK,U | NULL | compte client éventuel |
| Client | nom/prenom | varchar(100) | nom oui | — | — | identité |
| Client | type_client | varchar(20) | oui | — | PARTICULIER | particulier/entreprise |
| Client | email | varchar(254) | oui | U | — | normalisé en minuscules |
| Client | actif | bool | oui | index | vrai | archivage logique |
| Marque | nom | varchar(100) | oui | U | — | nom de marque |
| Marque | actif | bool | oui | index | vrai | visibilité catalogue |
| Categorie | nom | varchar(100) | oui | U | — | catégorie fonctionnelle |
| Pneu | reference_interne | varchar(60) | oui | U | — | majuscules, sans espace |
| Pneu | marque_id | bigint | oui | FK | — | suppression protégée |
| Pneu | categorie_id | bigint | oui | FK | — | suppression protégée |
| Pneu | largeur/hauteur/diametre | smallint+ | oui | index composite indirect | — | plages réalistes |
| Pneu | dimension_complete | varchar(30) | oui | index | — | cohérente avec composants |
| Pneu | indice_charge | smallint+ | oui | — | — | 50–200 |
| Pneu | indice_vitesse | varchar(1) | oui | — | — | lettre majuscule |
| Pneu | saison | varchar(20) | oui | index | 4_SAISONS | été/hiver/4 saisons |
| Pneu | prix_achat/prix_vente | decimal(10,2) | oui | CHECK | — | non négatif, vente ≥ achat |
| Pneu | quantite_disponible | int+ | oui | CHECK,index | 0 | modifiée via mouvements |
| Pneu | seuil_minimum | int+ | oui | — | 5 | niveau d'alerte |
| Pneu | statut | varchar(20) | oui | index | ACTIF | actif/archivé |
| Panier | client_id | bigint | oui | FK | — | un panier actif maximum |
| Panier | actif | bool | oui | U conditionnelle | vrai | panier courant |
| LignePanier | panier_id/pneu_id | bigint | oui | FK,U paire | — | produit unique par panier |
| LignePanier | quantite | int+ | oui | — | 1 | ≥1 et ≤ stock (service) |
| Commande | numero | varchar(25) | oui | U | généré | `CMD-2026-00001` |
| Commande | client_id | bigint | oui | FK | — | suppression protégée |
| Commande | statut | varchar(25) | oui | index | EN_ATTENTE | machine d'états |
| Commande | montant_total | decimal(12,2) | oui | — | 0 | recalcul serveur |
| Commande | stock_retire/stock_restaure | bool | oui | — | faux | idempotence du stock |
| LigneCommande | commande_id/pneu_id | bigint | oui | FK,U paire | — | une référence par commande |
| LigneCommande | reference_pneu/marque/modele/dimension | varchar | oui | — | — | instantané historique |
| LigneCommande | prix_unitaire/sous_total | decimal | oui | — | — | prix figé à la commande |
| Fournisseur | raison_sociale | varchar(150) | oui | U | — | identification fournisseur |
| Approvisionnement | numero | varchar(25) | oui | U | généré | `APP-2026-00001` |
| Approvisionnement | fournisseur_id | bigint | oui | FK | — | suppression protégée |
| Approvisionnement | statut | varchar(20) | oui | index | BROUILLON | brouillon/commandé/reçu/annulé |
| Approvisionnement | recu_le | datetime | non | — | NULL | verrou de double réception |
| LigneApprovisionnement | approvisionnement_id/pneu_id | bigint | oui | FK,U paire | — | ligne d'achat |
| MouvementStock | pneu_id | bigint | oui | FK,index | — | référence concernée |
| MouvementStock | type_mouvement | varchar(25) | oui | index | — | entrée/sortie/retour/ajustement |
| MouvementStock | quantite | int+ | oui | — | — | strictement positive |
| MouvementStock | stock_avant/stock_apres | int+ | oui | — | — | traçabilité complète |
| MouvementStock | commande_id/approvisionnement_id | bigint | non | FK | NULL | origine facultative |
| MouvementStock | utilisateur_id | bigint | oui | FK | — | responsable |
| DemandeDevis | dimensions_recherchees | varchar(100) | oui | — | — | besoin du prospect |
| DemandeDevis | statut | varchar(20) | oui | index | NOUVELLE | suivi de traitement |
| MessageContact | lu | bool | oui | index | faux | statut de lecture |

