# Système de Pointage par QR Code — Solution de secours au dispositif biométrique

## 🎯 Contexte

Projet réalisé durant mon stage au Ministère de la Décentralisation et du Développement
Local (MINDDEVEL), Cameroun, pour l'administration centrale et ses deux annexes à Yaoundé.

## ❗ Problème

Le suivi des arrivées/départs du personnel reposait sur un système biométrique
(empreinte digitale), sujet à des interruptions récurrentes :
- pannes du capteur biométrique
- pertes de configuration réseau rendant le dispositif indisponible

Ces interruptions empêchaient tout suivi fiable de la présence sur l'ensemble
de l'administration centrale et de ses deux annexes.

## ✅ Solution

Application web en Flask permettant de suppléer au système biométrique via un
mécanisme de QR codes, conçue pour couvrir l'ensemble du ministère central et
ses deux annexes à Yaoundé :
- génération d'un QR code unique par employé
- pointage (arrivée/départ) par scan via smartphone
- tableau de bord administrateur pour consulter et exporter les données de présence

## ⚙️ Fonctionnalités

- Génération de QR codes individuels par employé
- Scan des pointages via smartphone (entrée/sortie)
- Tableau de bord admin : consultation et export des données de présence
- Authentification avec rôles 

## 🛠️ Stack technique

- Backend : Python / Flask
- Base de données utilisée : MySQL
- Bibliothèque de génération : qrcode
- Bibliothèque de lecture QR côté smartphone : qrcode html5
- Frontend : moteur de rendu Jinja2 intégré à flask 

## 📊 Statut du projet

Prototype fonctionnel, conçu et développé durant le stage. N'a pas été déployé en
production, mais couvre le périmètre complet demandé (administration centrale +
2 annexes) avec un tableau de bord d'administration opérationnel.

## 🚀 Installation

\`\`\`bash
git clone https://github.com/RyryBioumlaTech/attendance-tracking-system-ATS-v0
cd attendance-tracking-system-ATS-v0
pip install -r requirements.txt
python app.py
\`\`\`

## 📸 Captures d'écran

<img width="1354" height="679" alt="view_datas" src="https://github.com/user-attachments/assets/9172df50-2c2f-49a0-a6dd-6846c62a8d22" />
<img width="1366" height="768" alt="qrScreen" src="https://github.com/user-attachments/assets/6f95a723-3b63-4e7d-a9ea-048b9101df92" />

## 💡 Ce que ce projet m'a appris

- Concevoir une solution de continuité de service face à une contrainte
  d'infrastructure publique réelle (fiabilité, disponibilité réseau)
- Penser un système multi-sites (siège + 2 annexes) dès la conception
- Construire un tableau de bord orienté utilisateur non-technique (les admins RH)

## 👤 Auteur

Ryan Bioumla — https://www.linkedin.com/in/ryan-bioumla/ · bpaulstevenryan@gmail.com
