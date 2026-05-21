# 🚀 Smart Buy Sentinel - Guide de Déploiement

## Table des matières

- [Déploiement Vercel](#déploiement-vercel)
- [Déploiement Docker](#déploiement-docker)
- [Configuration Telegram Bot](#configuration-telegram-bot)
- [Monitoring & Logs](#monitoring--logs)
- [Troubleshooting](#troubleshooting)

---

## 🔧 Déploiement Vercel (Recommandé)

### Prérequis

- Account Vercel (gratuit)
- Repository GitHub
- MongoDB Atlas cluster

### Étapes

#### 1. Connecter le Repository

```bash
# Push ton code sur GitHub
git init
git add .
git commit -m "Initial commit: Smart Buy Sentinel"
git remote add origin https://github.com/YOUR_USERNAME/smart-buy-sentinel.git
git push -u origin main
```

#### 2. Importer dans Vercel

1. Accéder à [vercel.com/dashboard](https://vercel.com/dashboard)
2. Cliquer "Add New" → "Project"
3. Sélectionner le repository GitHub
4. **Framework Preset** : Next.js
5. Cliquer "Import"

#### 3. Configurer les Variables d'Environnement

Dans Vercel Dashboard :
- **Settings** → **Environment Variables**

Ajouter les variables :

```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/sniper_deals?retryWrites=true&w=majority
NODE_ENV=production
```

**Pour MongoDB Atlas** :
1. Aller à [MongoDB Atlas](https://cloud.mongodb.com)
2. Cliquer sur ton cluster
3. "Connect" → "Connect your application"
4. Copier la connection string
5. Remplacer `<password>` et `<username>`

#### 4. Déployer

```bash
# Automatic: Chaque push sur main déploie automatiquement
# Manual: Cliquer "Redeploy" dans Vercel Dashboard

# Vérifier le déploiement
# https://your-project-name.vercel.app
```

### Performance

Vercel optimise automatiquement :
- ✅ Edge Functions
- ✅ Image Optimization
- ✅ Analytics
- ✅ Automatic HTTPS

---

## 🐳 Déploiement Docker

### Dockerfile

Le fichier suivant est déjà optimisé :

```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# Copier les fichiers de config
COPY package*.json ./
COPY tsconfig.json ./
COPY next.config.ts ./
COPY tailwind.config.ts ./
COPY postcss.config.js ./

# Installer les dépendances
RUN npm ci

# Copier le code source
COPY app ./app
COPY components ./components
COPY lib ./lib
COPY models ./models
COPY actions ./actions
COPY public ./public

# Build
RUN npm run build

# Runtime image
FROM node:18-alpine

WORKDIR /app

# Copier les dépendances (production only)
COPY package*.json ./
RUN npm ci --only=production

# Copier le build précédent
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000', (r) => {if (r.statusCode !== 200) throw new Error(r.statusCode)})"

# Start
CMD ["npm", "start"]
```

### Build & Run Local

```bash
# Build l'image
docker build -t smart-buy-sentinel:latest .

# Run
docker run -p 3000:3000 \
  -e MONGODB_URI="mongodb+srv://..." \
  -e NODE_ENV=production \
  smart-buy-sentinel:latest

# Accéder à http://localhost:3000
```

### Push vers Registry

```bash
# Docker Hub
docker tag smart-buy-sentinel:latest YOUR_USERNAME/smart-buy-sentinel:latest
docker push YOUR_USERNAME/smart-buy-sentinel:latest

# AWS ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com
docker tag smart-buy-sentinel:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/smart-buy-sentinel:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/smart-buy-sentinel:latest
```

---

## 🤖 Configuration Telegram Bot

### Créer le Bot

1. Ouvrir Telegram et chercher **@BotFather**
2. `/newbot`
3. Entrer le nom : `Smart Buy Sentinel Bot`
4. Entrer le username : `smart_buy_sentinel_bot`
5. Récupérer le **BOT_TOKEN** (à garder secret!)

### Configurer la Mini App

#### Option A : Via BotFather

```
/setmenubutton

Sélectionner ton bot → Envoyer la Web App URL :
https://smart-buy-sentinel.vercel.app
```

#### Option B : Manual Setup

```bash
# Utiliser Telegram Bot API directement
curl -X POST https://api.telegram.org/bot{BOT_TOKEN}/setWebAppInfo \
  -d '{
    "url": "https://smart-buy-sentinel.vercel.app",
    "user_is_admin": false
  }'
```

### Tester la Mini App

1. Accéder à ton bot Telegram : @smart_buy_sentinel_bot
2. Cliquer le bouton Menu
3. La Mini App devrait s'ouvrir

---

## 📊 Monitoring & Logs

### Vercel Logs

```bash
# Installer Vercel CLI
npm i -g vercel

# Voir les logs en temps réel
vercel logs --follow

# Voir les logs d'une fonction spécifique
vercel logs /actions/deals
```

### MongoDB Monitoring

1. Accéder à [MongoDB Atlas](https://cloud.mongodb.com)
2. **Clusters** → Ton cluster → **Metrics**

Surveiller :
- **Connections** : < 100
- **Query Time** : < 100ms average
- **Storage** : Growth rate

### Error Tracking (Optionnel)

Ajouter Sentry pour tracking errors :

```bash
npm install @sentry/nextjs
```

```typescript
// sentry.client.config.ts
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV,
});
```

---

## 🔐 Sécurité Déploiement

### Environment Variables

**À JAMAIS hardcoder** :
- ❌ MongoDB credentials
- ❌ API keys
- ❌ Bot tokens

**Solution** :
- ✅ Vercel Secrets
- ✅ `.env.local` local only
- ✅ `.gitignore` pour `.env*`

### Headers de Sécurité

Next.js ajoute automatiquement :
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: SAMEORIGIN`
- `X-XSS-Protection: 1; mode=block`

### Rate Limiting (TODO)

À implémenter :

```typescript
// middleware.ts (Future)
import { Ratelimit } from '@upstash/ratelimit';

export async function middleware(request: Request) {
  const ratelimit = new Ratelimit({
    redis: Redis.fromEnv(),
    limiter: Ratelimit.slidingWindow(100, '1 h'),
  });

  const { success } = await ratelimit.limit(request.ip);
  return success ? next() : new Response('Too many requests', { status: 429 });
}
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions (Optionnel)

```yaml
# .github/workflows/deploy.yml
name: Deploy to Vercel

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Install dependencies
        run: npm ci
      
      - name: Type check
        run: npm run type-check
      
      - name: Build
        run: npm run build
      
      - name: Deploy to Vercel
        uses: vercel/action@master
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
```

---

## 🧪 Checklist Pré-Déploiement

- [ ] `npm run build` local succeeds
- [ ] `npm run type-check` no errors
- [ ] `.env.local` fichier configuré localement
- [ ] MongoDB Atlas whitelist votre IP
- [ ] Telegram Bot créé (@BotFather)
- [ ] Mini App URL configurée
- [ ] Vercel secrets configurés
- [ ] `README.md` à jour
- [ ] Version dans `package.json` bumped

---

## 📈 Performance Post-Déploiement

### Metrics à Monitorer

| Métrique | Target | Tool |
|----------|--------|------|
| **TTFB** | < 200ms | Vercel Analytics |
| **LCP** | < 2.5s | PageSpeed Insights |
| **FID** | < 100ms | Chrome DevTools |
| **API Response** | < 150ms | MongoDB Metrics |
| **Error Rate** | < 0.1% | Sentry / Logs |

### Optimisation Continue

```bash
# Vérifier le bundle size
npm run build
# Look for .next/static/chunks

# Analyze with next/bundle-analyzer
npm install --save-dev @next/bundle-analyzer
```

---

## 🆘 Troubleshooting Déploiement

### Erreur : "MONGODB_URI not found"

```bash
# Vérifier dans Vercel Settings → Environment Variables
# Redeploy après ajouter la variable
vercel env pull

# Ou via CLI
vercel env add MONGODB_URI
```

### Erreur : "MongoDB Connection Timeout"

```bash
# MongoDB Atlas : Settings → Network Access
# Add Current IP + 0.0.0.0/0 (temporary)

# Ou vérifier la connection string
# Format: mongodb+srv://USER:PASS@CLUSTER.mongodb.net/DATABASE
```

### Erreur : "Telegram Web App not loading"

```bash
# 1. Vérifier l'URL dans Telegram Bot settings
# 2. Vérifier que le domaine est accessible publiquement
# 3. Checker la console browser (F12)
# 4. Vérifier que script Telegram est chargé:
# <script src="https://telegram.org/js/telegram-web-app.js" defer></script>
```

### Build Failures

```bash
# Clear Vercel cache
vercel build --no-cache

# Ou via dashboard
# Deployments → Select Failed → Redeploy
```

---

## 📞 Support & Ressources

- [Vercel Docs](https://vercel.com/docs)
- [Next.js Deployment](https://nextjs.org/docs/deployment/vercel)
- [MongoDB Deployment](https://docs.mongodb.com/manual/administration/deploy/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Telegram Web Apps](https://core.telegram.org/bots/webapps)

---

**Dernière mise à jour** : 21 mai 2026
**Status** : Production Ready ✅
