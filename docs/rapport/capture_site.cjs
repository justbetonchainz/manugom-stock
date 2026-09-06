/**
 * Captures réelles de MANUGOM pour le rapport académique.
 * Exécution : node docs/rapport/capture_site.cjs
 * Navigateur Microsoft Edge piloté par Playwright. Aucun rendu reconstitué.
 * Seules les connexions sont soumises ; toutes les pages métier restent en GET.
 */
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'C:/Users/khali/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

const root = path.resolve(__dirname, '../..');
const output = path.join(__dirname, 'assets/screenshots');
const baseURL = process.env.MANUGOM_URL || 'http://127.0.0.1:8000';
const viewport = { width: 1440, height: 1000 };
const manifest = { project: 'MANUGOM Stock', captured_at: new Date().toISOString(), method: 'Microsoft Edge headless / Playwright, genuine browser screenshots', viewport, device_scale_factor: 1.5, business_mutations: false, screenshots: [], errors: [] };

async function settle(page) {
  await page.waitForLoadState('networkidle', { timeout: 25000 }).catch(() => {});
  await page.evaluate(() => document.fonts.ready);
  await page.waitForFunction(() => Array.from(document.images).every(img => img.complete), null, { timeout: 15000 }).catch(() => {});
}

async function capture(page, spec) {
  const response = await page.goto(baseURL + spec.url, { waitUntil: 'domcontentloaded' });
  if (!response || response.status() !== 200) throw new Error(`${spec.file}: HTTP ${response && response.status()}`);
  await settle(page);
  if (spec.readyText) await page.getByText(spec.readyText, { exact: true }).first().waitFor();
  if (spec.scrollTo) await page.locator(spec.scrollTo).scrollIntoViewIfNeeded();
  const imagePath = path.join(output, spec.file + '.png');
  await page.screenshot({ path: imagePath, fullPage: Boolean(spec.fullPage), animations: 'disabled' });
  const png = fs.readFileSync(imagePath);
  const entry = { id: spec.file, file: 'docs/rapport/assets/screenshots/' + spec.file + '.png', role: spec.role, title: spec.title, description: spec.description, url: page.url(), http_status: response.status(), width: png.readUInt32BE(16), height: png.readUInt32BE(20), full_page: Boolean(spec.fullPage), source_files: spec.sources, sha256: crypto.createHash('sha256').update(png).digest('hex') };
  manifest.screenshots.push(entry);
  console.log(`${spec.file}: ${entry.width}x${entry.height} — ${entry.url}`);
}

async function login(page, username, password) {
  await page.goto(baseURL + '/comptes/connexion/', { waitUntil: 'domcontentloaded' });
  await page.locator('#id_username').fill(username);
  await page.locator('#id_password').fill(password);
  await Promise.all([page.waitForURL(url => !url.pathname.includes('/connexion/')), page.getByRole('button', { name: 'Se connecter', exact: true }).click()]);
  await settle(page);
}

async function main() {
  fs.mkdirSync(output, { recursive: true });
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    for (const role of ['Visiteur', 'Client', 'Employé', 'Administrateur']) {
      const context = await browser.newContext({ viewport, deviceScaleFactor: 1.5, locale: 'fr-FR', colorScheme: 'light', reducedMotion: 'reduce' });
      await context.route('**/*', async route => {
        const req = route.request();
        const pathname = new URL(req.url()).pathname;
        if (req.method() !== 'GET' && req.method() !== 'HEAD' && !['/comptes/connexion/', '/django-admin/login/'].includes(pathname)) {
          throw new Error('Mutation non autorisée dans le scénario de capture : ' + req.method() + ' ' + req.url());
        }
        await route.continue();
      });
      const page = await context.newPage();
      page.on('pageerror', error => manifest.errors.push({ role, message: error.message, url: page.url() }));
      if (role === 'Client') await login(page, 'client1', process.env.MANUGOM_CLIENT_PASSWORD || 'Client@2026!');
      if (role === 'Employé') await login(page, 'employe1', process.env.MANUGOM_EMPLOYEE_PASSWORD || 'Employe@2026!');
      if (role === 'Administrateur') await login(page, 'admin', process.env.MANUGOM_ADMIN_PASSWORD || 'Admin@2026!');
      const specs = {
        Visiteur: [
          { file: '01-visiteur-accueil', url: '/', title: 'Accueil public', description: 'Accueil réel : navigation publique, présentation MANUGOM, appel à la consultation du catalogue et prise de contact.', sources: ['core/views.py', 'templates/core/home.html'] },
          { file: '02-visiteur-catalogue', url: '/catalogue/', title: 'Catalogue public', description: 'Consultation publique des pneus : recherche, filtres, prix et disponibilité des produits de démonstration.', sources: ['inventory/views.py', 'templates/inventory/catalog.html'] },
          { file: '03-visiteur-fiche-pneu', url: '/catalogue/pneu/1/', title: 'Fiche détaillée d’un pneu', description: 'Caractéristiques, disponibilité et prix d’un article ; proposition de connexion pour commander.', sources: ['inventory/views.py', 'templates/inventory/detail.html'] }
        ],
        Client: [
          { file: '04-client-commandes', url: '/commandes/mes-commandes/', title: 'Espace client : mes commandes', description: 'Compte client1 connecté, affichage de ses commandes existantes et de leur statut.', sources: ['orders/views.py', 'templates/orders/order_list.html'] },
          { file: '05-client-detail-commande', url: '/commandes/1/', title: 'Espace client : détail de commande', description: 'Commande existante livrée CMD-2026-00001, lignes et montants historiques visibles par son propriétaire.', sources: ['orders/views.py', 'templates/orders/order_detail.html'] }
        ],
        Employé: [
          { file: '06-employe-commandes', url: '/gestion/commandes/', title: 'Espace employé : suivi des commandes', description: 'Liste opérationnelle accessible à employe1, filtres de statut et accès aux fiches de commande.', sources: ['dashboard/views.py', 'templates/dashboard/order_list.html'] },
          { file: '07-employe-stock', url: '/gestion/pneus/', title: 'Espace employé : gestion du stock', description: 'Référentiel des pneus : stocks, prix, recherche et actions de gestion, sans soumission d’action.', sources: ['dashboard/views.py', 'templates/dashboard/tire_list.html'] }
        ],
        Administrateur: [
          { file: '08-dashboard-synthese', url: '/gestion/', title: 'Tableau de bord : indicateurs et ventes', description: 'Indicateurs réellement calculés depuis SQLite et graphiques Chart.js des ventes et des statuts.', sources: ['dashboard/views.py', 'templates/dashboard/index.html'] },
          { file: '09-dashboard-graphiques', url: '/gestion/', scrollTo: '#brandChart', title: 'Tableau de bord : analyses de stock', description: 'Deuxième vue du même tableau de bord : distribution du stock par marque, produits vendus et mouvements.', sources: ['dashboard/views.py', 'templates/dashboard/index.html'] },
          { file: '10-admin-utilisateurs', url: '/gestion/utilisateurs/', title: 'Administration des utilisateurs', description: 'Gestion des rôles et des comptes par un administrateur, avec comptes de démonstration.', sources: ['dashboard/views.py', 'templates/dashboard/user_list.html'] },
          { file: '11-admin-django', url: '/django-admin/', title: 'Administration Django', description: 'Interface native Django réservée au personnel autorisé, distincte de l’espace de gestion applicatif.', sources: ['manugom_stock/urls.py', 'accounts/admin.py', 'inventory/admin.py', 'orders/admin.py'] }
        ]
      }[role];
      for (const spec of specs) await capture(page, { ...spec, role });
      await context.close();
    }
  } finally {
    await browser.close();
    fs.writeFileSync(path.join(output, 'manifest.json'), JSON.stringify(manifest, null, 2) + '\n');
  }
  if (manifest.errors.length) console.log(JSON.stringify(manifest.errors, null, 2));
  console.log(`${manifest.screenshots.length} captures réelles enregistrées.`);
}

main().catch(error => { console.error(error); process.exitCode = 1; });
