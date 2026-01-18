import tseslint from '@typescript-eslint/eslint-plugin';
import tsParser from '@typescript-eslint/parser';

export default {
  files: ["src/**/*.ts"],
  languageOptions: {
    ecmaVersion: 2024,
    sourceType: "module",
    parser: tsParser,
    parserOptions: {
      project: "./tsconfig.json",
    },
  },
  plugins: {
    "@typescript-eslint": tseslint,
  },
  rules: {
    "no-console": "warn",
    "@typescript-eslint/no-explicit-any": "warn",
    "@typescript-eslint/explicit-function-return-type": "off",
  },
  ignores: ["node_modules", "dist", "*.d.ts"],
};
