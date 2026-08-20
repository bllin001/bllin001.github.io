# Brian Llinás — Personal Website

Personal academic website built with Astro. Publications and media entries are
generated from CSV data during the static build.

## Project structure

```text
/
├── public/          Static images and documents
├── src/
│   ├── components/ Reusable Astro components
│   ├── data/       Publications and media CSV files
│   ├── layouts/    Shared page layout
│   ├── pages/      File-based routes
│   ├── styles/     Global styles
│   └── types/      Shared TypeScript interfaces
├── astro.config.mjs
└── package.json
```

## Commands

Install dependencies:

```sh
npm install
```

Start the development server:

```sh
npm run dev
```

Create and preview a production build:

```sh
npm run build
npm run preview
```

## Content updates

- Edit `src/data/publications.csv` to update publications.
- Edit `src/data/media.csv` to update media and outreach entries.
- Place directly served images and documents in `public/`.
