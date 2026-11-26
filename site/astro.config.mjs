// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import { getData } from './src/lib/data.ts';

/**
 * Load and validate the export (AEC_DATA_DIR) before any page renders, so a
 * missing or invalid file stops the build once, with the loader's message,
 * instead of failing in whichever page happens to render first.
 * @type {import('astro').AstroIntegration}
 */
const validateData = {
  name: 'aec-validate-data',
  hooks: {
    'astro:build:start': ({ logger }) => {
      const { dataDir, projects, csms } = getData();
      logger.info(`${projects.length} projects and ${csms.length} CSMS products from ${dataDir}`);
    },
  },
};

// GitHub Pages project site: https://juherr.github.io/awesome-ev-charging/.
// Every internal link goes through `url()` (src/lib/url.ts), which prefixes
// `import.meta.env.BASE_URL`, so changing `base` here is the only edit a
// custom domain needs.
export default defineConfig({
  site: 'https://juherr.github.io',
  base: '/awesome-ev-charging',
  trailingSlash: 'always',
  integrations: [validateData, sitemap()],
});
