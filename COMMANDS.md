# 🛠️ Smart Buy Sentinel - Commandes Utiles

## Development

### Démarrer le serveur local
```bash
npm run dev
# Ouvre http://localhost:3000
# Hot reload activé
```

### Vérifier les types TypeScript
```bash
npm run type-check
# Affiche les erreurs TS sans compiler
```

### Build production
```bash
npm run build
# Crée .next/ directory
# Optimise le bundle
```

### Lancer la build localement
```bash
npm run build
npm start
# Simule la production
# Accès: http://localhost:3000
```

### Linter (optionnel)
```bash
npm run lint
# Vérifie la qualité du code
```

---

## Installation & Setup

### Installer les dépendances
```bash
npm install
# ou
npm ci  # Pour CI/CD (exact versions)
```

### Ajouter une nouvelle dépendance
```bash
npm install package-name

# Exemple:
npm install axios  # HTTP client
npm install date-fns  # Date utilities
```

### Ajouter une dev dependency
```bash
npm install --save-dev package-name

# Exemple:
npm install --save-dev @types/node
```

### Mise à jour des dépendances
```bash
# Vérifier les updates disponibles
npm outdated

# Mettre à jour tout
npm update

# Mettre à jour une spécifique
npm install mongoose@latest
```

---

## Configuration

### Créer .env.local
```bash
# Depuis le template
cp .env.local.example .env.local

# Puis éditer avec ton éditeur
```

### Vérifier les variables d'env
```bash
# Node.js (dans un script)
console.log(process.env.MONGODB_URI);
```

---

## Database

### Connexion MongoDB Atlas CLI
```bash
# Installer MongoDB Shell
# https://www.mongodb.com/try/download/shell

mongosh "mongodb+srv://username:password@cluster.mongodb.net/sniper_deals"
```

### Requêtes Mongo (dans Shell)
```javascript
// Lister les deals
db.deals.find({}).limit(5)

// Compter les deals
db.deals.countDocuments()

// Deals par catégorie
db.deals.countDocuments({ category: "Smartphones" })

// Top 5 meilleur profit
db.deals.find().sort({ profit_margin: -1 }).limit(5)

// Injecter des deals de test
db.deals.insertOne({
  title: "Test Product",
  category: "Smartphones",
  current_price: 100,
  idealo_price: 150,
  profit_margin: 50,
  z_score: 2.5,
  source: "Idealo",
  url: "https://...",
  product_id: "test-123",
  availability: "In Stock",
  created_at: new Date(),
  scraped_at: new Date()
})

// Supprimer tous les deals (DANGER!)
db.deals.deleteMany({})
```

### Visualiser avec MongoDB Compass
```bash
# Télécharger: https://www.mongodb.com/products/tools/compass
# Connexion: Copier connection string depuis MongoDB Atlas
# Browse les collections visualmente
```

---

## Git & Version Control

### Initialiser repository
```bash
git init
git remote add origin https://github.com/username/smart-buy-sentinel
```

### Committer le code
```bash
git status                  # Voir les changes
git add .                  # Stage tout
git commit -m "message"    # Committer
git push -u origin main    # Push to GitHub
```

### Créer une branche feature
```bash
git checkout -b feature/new-feature
# Faire les changes
git commit -m "Add new feature"
git push -u origin feature/new-feature
# Créer Pull Request sur GitHub
```

---

## Deployment

### Déployer sur Vercel via CLI
```bash
# Installer Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
vercel

# Deploy en production
vercel --prod
```

### Voir les logs Vercel
```bash
vercel logs
vercel logs --follow  # Real-time
```

### Docker

```bash
# Build l'image
docker build -t smart-buy-sentinel:latest .

# Run localement
docker run -p 3000:3000 \
  -e MONGODB_URI="mongodb+srv://..." \
  smart-buy-sentinel:latest

# Push vers registry
docker push your-registry/smart-buy-sentinel:latest
```

---

## Testing (À Implémenter)

### Run tests (avec Jest/Vitest)
```bash
npm test
npm test -- --watch
npm test -- --coverage
```

### Run tests spécifique
```bash
npm test -- DealCard.test.tsx
```

---

## Performance

### Analyser le bundle
```bash
# Installer analyzer
npm install --save-dev @next/bundle-analyzer

# Voir le rapport
npm run analyze
```

### Profiler React
```bash
# DevTools Chrome
# F12 → Performance tab
# Record → Interact → Stop
# Analyser l'timeline
```

### Analyser les requêtes MongoDB
```bash
# MongoDB Atlas Dashboard
# Clusters → Performance Advisor
# Voir les queries lentes
```

---

## Debugging

### Console Logs
```typescript
console.log('Debug:', variable);
console.error('Error:', error);
console.table(array);  // Tableau formaté
```

### VS Code Debugger
```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Next.js",
      "type": "node",
      "request": "launch",
      "program": "${workspaceFolder}/node_modules/.bin/next",
      "args": ["dev"],
      "console": "integratedTerminal"
    }
  ]
}
```

### Browser DevTools
```
F12 → Console
F12 → Network (voir les requêtes API)
F12 → Application (voir les variables d'env)
```

---

## Maintenance

### Cleanup
```bash
# Nettoyer .next cache
rm -rf .next

# Nettoyer node_modules
rm -rf node_modules
npm install

# Nettoyer logs
npm run build 2>&1 | tee build.log
```

### Dependency Security
```bash
# Vérifier les vulnérabilités
npm audit

# Réparer automatiquement
npm audit fix

# Vérifier strictement
npm audit --audit-level=moderate
```

### Update documentation
```bash
# Générer une table des matières (avec markdown-toc)
npm install -g markdown-toc
markdown-toc README.md -i
```

---

## Utilities

### Formatter du code
```bash
# Prettier (si installé)
npx prettier --write .

# ESLint fix
npm run lint -- --fix
```

### Vérifier les types
```bash
npx tsc --noEmit
```

### Rebuild dépendances natives
```bash
npm rebuild
```

### Clear npm cache
```bash
npm cache clean --force
```

---

## Productivity Tips

### Raccourcis VS Code
```
Ctrl+Shift+P     → Command palette
Ctrl+K Ctrl+0    → Collapse all folders
Ctrl+/           → Toggle comment
Alt+Up/Down      → Move line
Ctrl+D           → Select word (multi-select)
Ctrl+H           → Find & replace
```

### Terminal Tips
```bash
# Supprimer l'historique terminal
clear

# Réutiliser la dernière commande
!!

# Chercher dans l'historique
Ctrl+R

# Arrêter le processus
Ctrl+C

# Exécuter en background
command &
```

---

## Emergency Commands

### Reset everything
```bash
# ⚠️ DANGER - Perd tous les changes non-commités
git reset --hard HEAD
```

### Kill port 3000 (if stuck)
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID [PID] /F

# Mac/Linux
lsof -i :3000
kill -9 [PID]
```

### Force push (use carefully!)
```bash
git push origin main --force
```

---

## Cheatsheet Rapide

| Command | Purpose |
|---------|---------|
| `npm run dev` | 🚀 Start dev server |
| `npm run build` | 🏗️ Build production |
| `npm run type-check` | ✔️ Check types |
| `npm test` | 🧪 Run tests |
| `npm audit` | 🔒 Security check |
| `vercel deploy` | 📤 Deploy to Vercel |
| `docker build .` | 🐳 Build Docker image |
| `git push` | ⬆️ Push to GitHub |
| `mongosh` | 🗄️ MongoDB shell |
| `clear` | 🧹 Clear terminal |

---

**Last Updated** : 21 mai 2026
**Status** : Complete command reference
