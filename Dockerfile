FROM ghcr.io/puppeteer/puppeteer

WORKDIR /app

COPY tsconfig.json .
COPY package.json .
COPY package-lock.json .
COPY ./patches ./patches
RUN npm ci

COPY ./src ./src
RUN npm run build

CMD ["npm", "run", "start"]
