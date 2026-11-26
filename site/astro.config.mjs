// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// GitHub Pages project site: https://juherr.github.io/awesome-ev-charging/.
// Every internal link goes through `url()` (src/lib/url.ts), which prefixes
// `import.meta.env.BASE_URL`, so changing `base` here is the only edit a
// custom domain needs.
export default defineConfig({
  site: 'https://juherr.github.io',
  base: '/awesome-ev-charging',
  trailingSlash: 'always',
  integrations: [sitemap()],
});
