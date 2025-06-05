/**
 * @example :sparkles: [#1] feat: implement new feature
 * @see https://regexr.com/8dt4d
 */
const COMMIT_PATTERN = /(:\w+:\s)(?:\[#(\d+)\]\s)?([\w\s()]+):\s(.+)/;

// We can't use commitlint type enum here due to gitmoji.
const TYPE_ENUM = [
  "build",
  "chore",
  "ci",
  "docs",
  "feat",
  "fix",
  "perf",
  "refactor",
  "revert",
  "style",
  "test",
];

/**
 * Simple commitlint plugin that allows a custom function to be executed.
 */
const functionRulePlugin = {
  rules: {
    functionRule: (
      parsed: { header: string },
      when: string,
      value: unknown,
    ) => {
      if (typeof value !== "function") {
        throw new Error(`${value} is not a function!`);
      }
      return value(parsed, when);
    },
  },
};

// Export commitlint config using TypeScript types
const config = {
  plugins: [functionRulePlugin],
  rules: {
    "header-full-stop": [2, "never"],
    functionRule: [
      2,
      "always",
      ({ header }: { header: string }) => {
        const match = header.match(COMMIT_PATTERN);

        if (match) {
          // eslint-disable-next-line @typescript-eslint/no-unused-vars
          const [_header, _gitmoji, _ticket, type, _scope, _description] =
            match;
          if (!TYPE_ENUM.includes(type)) {
            return [false, `${type} is not in ${TYPE_ENUM.join(", ")}`];
          }

          // Message matched.
          return [true, ""];
        }

        // Message did not match format.
        return [
          false,
          "Commit message format invalid: \n\nFormat: <gitmoji>[ [ticket]] <type>[([optional scope])]: <description>.\nExample: :sparkles: [#1] feat: implement new feature",
        ];
      },
    ],
  },
};

export default config;
