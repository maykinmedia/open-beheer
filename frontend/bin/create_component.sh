#!/bin/bash

COMPONENTS_DIR="src/components"
INDEX_FILE="$COMPONENTS_DIR/index.ts"

component_name=$1
component_name_lowercase=$(echo "$component_name" | tr '[:upper:]' '[:lower:]')
component_dir="$COMPONENTS_DIR/$component_name_lowercase"
capitalized_component_name=$(echo "$component_name" | awk '{print toupper(substr($0, 1, 1)) tolower(substr($0, 2))}')
component_name="${capitalized_component_name}"

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
  echo "export * from \"./$capitalized_component_name\";" > "$2/index.ts"
}

# Function to create the component file
function create_component_file() {
  cat > "$2/$capitalized_component_name.tsx" <<EOF
import React from "react";

export type ${component_name}Props = React.ComponentProps<"main"> & {
  // Props here.
};

/**
 * ${capitalized_component_name} component
 */
export function ${component_name}({ children, ...props }: ${component_name}Props) {
  return (
    <main className="${component_name}" {...props}>
      <pre>props: {JSON.stringify(props)}</pre>
      {children}
    </main>
  );
}
EOF
}

# Function to create the stories.tsx file
function create_stories_file() {
  cat > "$2/$capitalized_component_name.stories.tsx" <<EOF
import type { Meta, StoryObj } from "@storybook/react";

import { ${component_name} as ${component_name}Component } from "./$capitalized_component_name";

const meta: Meta<typeof ${component_name}Component> = {
  title: "Components/${capitalized_component_name}",
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

# Function to update the index.ts file in components
function update_index_file() {
  echo "// Auto-generated file. Do not modify manually." > "$INDEX_FILE"
  for component_dir in "$COMPONENTS_DIR"/*/; do
    component_name=$(basename "$component_dir")
    echo "export * from \"./$component_name\";" >> "$INDEX_FILE"
  done
}

# Main script

# Check if $COMPONENTS_DIR directory exists, if not create it
create_directory $COMPONENTS_DIR

# Check if a component name is provided
if [ -z "$1" ]; then
  echo "Error: Please provide a component name."
  exit 1
fi

# Check if component already exists
if directory_exists $component_dir; then
  echo "Error: component '$capitalized_component_name' already exists."
  exit 1
fi

# Create component directory
create_directory $component_dir

# Create individual files
create_index_file $capitalized_component_name $component_dir
create_component_file $capitalized_component_name $component_dir
create_stories_file $capitalized_component_name $component_dir

# Update components/index.ts file
update_index_file

echo "component '$capitalized_component_name' created successfully."
