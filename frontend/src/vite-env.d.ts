/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly MYKN_API_URL: string;
  readonly MYKN_API_PATH: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
