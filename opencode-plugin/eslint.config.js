export default {
  files: ["src/**/*.ts"],
  languageOptions: {
    ecmaVersion: 2024,
    sourceType: "module",
    parser: "@typescript-eslint/parser",
    parserOptions: {
      project: "./tsconfig.json",
    },
  },
  plugins: {
    "@typescript-eslint": {
      rules: {
        "no-unused-vars": "off",
        "@typescript-eslint/no-unused-vars": ["error", {
          argsIgnorePattern: "^_",
          varsIgnorePattern: "^_",
        }],
      },
    },
    prettier: "error",
  },
  rules: {
    "no-console": "warn",
    "@typescript-eslint/no-explicit-any": "warn",
    "@typescript-eslint/explicit-function-return-type": "off",
    "@typescript-eslint/no-floating-promises": "error",
  },
  ignores: ["node_modules", "dist", "*.d.ts"],
};
