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
}

# Function to create the CSS file
function create_css_file() {
  echo ".${component_name} {" > "$2/$capitalized_page_name.css"
  echo "  /* Rules here. */" >> "$2/$capitalized_page_name.css"
  echo "}" >> "$2/$capitalized_page_name.css"
}

# Function to create the stories.tsx file
function create_stories_file() {
  cat > "$2/$capitalized_page_name.stories.tsx" <<EOF
import type { Meta, StoryObj } from "@storybook/react";

import { ${component_name} as ${component_name}Component } from "./$capitalized_page_name";

const meta: Meta<typeof ${component_name}Component> = {
  title: "Pages/${capitalized_page_name}",
  component: ${component_name}Component,
};

export default meta;
type Story = StoryObj<typeof meta>;

export const ${component_name}: Story = {
  args: {
    children: "The quick brown fox jumps over the lazy dog.",
  },
};
EOF
}

# Function to create the page file
function create_page_file() {
  cat > "$2/$capitalized_page_name.tsx" <<EOF
import "./$capitalized_page_name.css";

export type ${component_name}Props = React.ComponentProps<"main"> & {
  // Props here.
};

/**
 * ${capitalized_page_name} page
 */
export function ${component_name}({ children, ...props }: ${component_name}Props) {
  return (
    <main className="${component_name}" {...props}>
      {children}
    </main>
  );
}
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
create_css_file $capitalized_page_name $page_dir
create_stories_file $capitalized_page_name $page_dir
create_page_file $capitalized_page_name $page_dir

# Update pages/index.ts file
update_index_file

echo "page '$capitalized_page_name' created successfully."
