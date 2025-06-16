#!/bin/bash

PAGES_DIR="src/pages"
INDEX_FILE="$PAGES_DIR/index.ts"

page_name=$1
page_name_lowercase=$(echo "$page_name" | tr '[:upper:]' '[:lower:]')
page_dir="$PAGES_DIR/$page_name_lowercase"
capitalized_page_name=$(echo "$page_name" | awk '{print toupper(substr($0, 1, 1)) tolower(substr($0, 2))}')
component_name="${capitalized_page_name}Page"

# Function to check if a directory exists
function directory_exists() {
  [ -d $1 ]
}

# Function to create a directory if it doesn't exist
function create_directory() {
  if ! directory_exists $1; then
    mkdir -p $1
  fi
}

# Function to create the index.ts file
function create_index_file() {
  echo "export * from \"./$capitalized_page_name\";" > "$2/index.ts"
  echo "export * from \"./${page_name}.action\";" >> "$2/index.ts"
  echo "export * from \"./${page_name}.loader\";" >> "$2/index.ts"
}

# Function to create the page file
function create_page_file() {
  cat > "$2/$capitalized_page_name.tsx" <<EOF
import React from "react";
import { Outlet, useLoaderData } from "react-router";
import { useCurrentMatch } from "~/hooks/useCurrentMatch";

import { ${capitalized_page_name}LoaderData } from "./${page_name}.loader.ts";

export type ${component_name}Props = React.ComponentProps<"main"> & {
  // Props here.
};

/**
 * ${capitalized_page_name} page
 */
export function ${component_name}({ children, ...props }: ${component_name}Props) {
  const activeMatch = useCurrentMatch();
  const loaderData = useLoaderData<${capitalized_page_name}LoaderData>();

  return (
    <main className="${component_name}" {...props}>
      <pre>match: {JSON.stringify(activeMatch)}</pre>
      <pre>data: {JSON.stringify(loaderData)}</pre>
      <Outlet />
    </main>
  );
}
EOF
}

# Function to create the loader file
function create_loader_file() {
  cat > "$2/$page_name.loader.ts" <<EOF
export type ${capitalized_page_name}LoaderData = object;

/**
 * ${capitalized_page_name} loader.
 * Loader data can be obtained using \`useLoaderData()\` in ${component_name}.
 */
export async function ${page_name}Loader(): Promise<${capitalized_page_name}LoaderData> {
  return {};
}
EOF
}

# Function to create the action file
function create_action_file() {
  cat > "$2/$page_name.action.ts" <<EOF
export type ${capitalized_page_name}ActionData = object;

/**
 * ${capitalized_page_name} action.
 * Action data can be obtained using \`useActionData()\` in ${component_name}.
 */
export async function ${page_name}Action(): Promise<${capitalized_page_name}ActionData> {
  return {};
}
EOF
}

# Function to create the stories.tsx file
function create_stories_file() {
  cat > "$2/$capitalized_page_name.stories.tsx" <<EOF
import type { Meta, StoryObj } from "@storybook/react";
import {
  reactRouterParameters,
  withRouter,
} from "storybook-addon-remix-react-router";

import { ${component_name} as ${component_name}Component } from "./$capitalized_page_name";
import { ${page_name}Loader } from "./${page_name}.loader";

const meta: Meta<typeof ${component_name}Component> = {
  title: "Pages/${capitalized_page_name}",
  component: ${component_name}Component,
  decorators: [withRouter],
};

export default meta;
type Story = StoryObj<typeof meta>;

export const ${component_name}: Story = {
  parameters: {
    reactRouter: reactRouterParameters({
      routing: {
        loader: ${page_name}Loader,
      },
    }),
  },
  args: {
    children: "The quick brown fox jumps over the lazy dog.",
  },
};
EOF
}

# Function to update the index.ts file in pages
function update_index_file() {
  echo "// Auto-generated file. Do not modify manually." > "$INDEX_FILE"
  for page_dir in "$PAGES_DIR"/*/; do
    page_name=$(basename "$page_dir")
    echo "export * from \"./$page_name\";" >> "$INDEX_FILE"
  done
}

# Main script

# Check if $PAGES_DIR directory exists, if not create it
create_directory $PAGES_DIR

# Check if a page name is provided
if [ -z "$1" ]; then
  echo "Error: Please provide a page name."
  exit 1
fi

# Check if page already exists
if directory_exists $page_dir; then
  echo "Error: page '$capitalized_page_name' already exists."
  exit 1
fi

# Create page directory
create_directory $page_dir

# Create individual files
create_index_file $capitalized_page_name $page_dir
create_page_file $capitalized_page_name $page_dir
create_loader_file $capitalized_page_name $page_dir
create_action_file $capitalized_page_name $page_dir
create_stories_file $capitalized_page_name $page_dir

# Update pages/index.ts file
update_index_file

echo "page '$capitalized_page_name' created successfully."
