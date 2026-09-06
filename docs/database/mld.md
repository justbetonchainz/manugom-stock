# Modèle logique de données (MLD)

Notation : `#` clé primaire, `*` clé étrangère, `U` unicité.

```text
ACCOUNTS_USER(#id, username U, email U, password, role, is_active, is_staff, is_superuser, ...)
ACCOUNTS_PROFILUTILISATEUR(#id, utilisateur_id* U, telephone, adresse, ville, photo, date_modification)
CUSTOMERS_CLIENT(#id, numero U, utilisateur_id* U?, nom, prenom, raison_sociale, type_client,
                 telephone, email U, adresse, ville, identifiant_fiscal, actif, dates)
INVENTORY_MARQUE(#id, nom U, pays_origine, description, logo, actif, dates)
INVENTORY_CATEGORIE(#id, nom U, description, actif, dates)
INVENTORY_PNEU(#id, reference_interne U, reference_commerciale, marque_id*, modele, categorie_id*,
               largeur, hauteur, diametre, indice_charge, indice_vitesse, dimension_complete,
               saison, usage_vehicule, prix_achat, prix_vente, quantite_disponible,
               seuil_minimum, emplacement, image, description, statut, dates)
ORDERS_PANIER(#id, client_id*, actif, dates)
ORDERS_LIGNEPANIER(#id, panier_id*, pneu_id*, quantite, date_ajout)
ORDERS_COMMANDE(#id, numero U, client_id*, date, adresse, ville, type_reception,
                mode_paiement, statut_paiement, statut, montant_total, notes,
                stock_retire, stock_restaure, dates)
ORDERS_LIGNECOMMANDE(#id, commande_id*, pneu_id*, reference_pneu, marque, modele,
                     dimension, quantite, prix_unitaire, sous_total)
SUPPLIERS_FOURNISSEUR(#id, raison_sociale U, nom_contact, telephone, email, adresse,
                      ville, identifiant_fiscal, notes, actif, dates)
SUPPLIERS_APPROVISIONNEMENT(#id, numero U, fournisseur_id*, date, statut, montant_total,
                            notes, utilisateur_responsable_id*, recu_le, dates)
SUPPLIERS_LIGNEAPPROVISIONNEMENT(#id, approvisionnement_id*, pneu_id*, quantite, prix_achat)
INVENTORY_MOUVEMENTSTOCK(#id, pneu_id*, type_mouvement, quantite, stock_avant, stock_apres,
                         motif, commande_id*?, approvisionnement_id*?, utilisateur_id*, date_heure)
QUOTES_DEMANDEDEVIS(#id, nom_complet, telephone, email, marque_vehicule, modele_vehicule,
                    dimensions_recherchees, quantite, message, statut, date)
QUOTES_MESSAGECONTACT(#id, nom, telephone, email, sujet, message, date, lu)
```

La table intermédiaire Django `suppliers_fournisseur_marques_fournies` réalise la relation plusieurs-à-plusieurs entre fournisseurs et marques.

