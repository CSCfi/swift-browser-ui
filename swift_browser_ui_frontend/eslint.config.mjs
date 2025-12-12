import vue from "eslint-plugin-vue";
import globals from "globals";
import path from "node:path";
import { fileURLToPath } from "node:url";
import js from "@eslint/js";
import { FlatCompat } from "@eslint/eslintrc";
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
import fs from 'node:fs/promises';

const compat = new FlatCompat({
    baseDirectory: __dirname,
    recommendedConfig: js.configs.recommended,
    allConfig: js.configs.all
});

export default [
    { files: ["**/*.js","**/*.vue"]},
    ...compat.extends(""),
    ...vue.configs['flat/recommended', "flat/base", "flat/essential"],
    {  ignores: await fs
      .readFile('.gitignore', { encoding: 'utf8' })
      .then((r) => r.split(/[\r\n]+/).filter((r) => !r.trim().startsWith('#') && r.trim() !== '')) },
    {
        plugins: {
            vue
        },
        languageOptions: {
            globals: {
                ...globals.browser,
                ...globals.node,
                ...globals.jest,
                Atomics: "readonly",
                SharedArrayBuffer: "readonly",
                import: "readonly",
            },

            ecmaVersion: 2021,
            sourceType: "module",
        },

        rules: {
            indent: ["error", 2, {
                SwitchCase: 1,
            }],

            "linebreak-style": ["error", "unix"],
            quotes: ["error", "double"],
            semi: ["error", "always"],
            "comma-dangle": ["error", "always-multiline"],

            "max-len": ["error", {
                code: 100,
                comments: 100,
                ignoreTemplateLiterals: true,
                ignoreUrls: true,
            }],

            "vue/html-closing-bracket-newline": ["error", {
                singleline: "never",
                multiline: "always",
            }],

            "vue/mustache-interpolation-spacing": ["error", "always"],

            "vue/script-indent": ["error", 2, {
                baseIndent: 0,
                switchCase: 1,
            }],

            "vue/require-prop-types": [0],
            "vue/no-deprecated-slot-attribute": [0],
            "vue/v-on-event-hyphenation": [0],
            "vue/require-explicit-emits": [0],

            "vue/attribute-hyphenation": ["error", "always", {
                ignore: ["footerOptions"],
            }],
        },
    },
];
