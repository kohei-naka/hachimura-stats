
FROM node:20-alpine

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install --no-fund --no-audit

COPY next.config.mjs ./next.config.mjs
COPY tsconfig.json ./tsconfig.json
COPY app ./app
COPY components ./components
COPY public ./public
COPY styles ./styles
COPY postcss.config.js ./postcss.config.js
COPY tailwind.config.ts ./tailwind.config.ts

EXPOSE 3000
CMD ["npm", "run", "dev"]
