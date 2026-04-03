#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="$ROOT_DIR/build"
DIST_DIR="$ROOT_DIR/dist"
APP_DIR="$ROOT_DIR/app"

echo "Root directory: $ROOT_DIR"
echo "App directory: $APP_DIR"

if [ ! -d "$APP_DIR" ]; then
  echo "Error: app directory not found at $APP_DIR"
  exit 1
fi

if [ ! -f "$APP_DIR/requirements.txt" ]; then
  echo "Error: requirements.txt not found at $APP_DIR/requirements.txt"
  exit 1
fi

echo "Cleaning old build artifacts..."
rm -rf "$BUILD_DIR" "$DIST_DIR"
mkdir -p "$BUILD_DIR" "$DIST_DIR"

echo "Installing dependencies..."
python -m pip install -r "$APP_DIR/requirements.txt" -t "$BUILD_DIR"

echo "Copying Python files..."
cp "$APP_DIR"/*.py "$BUILD_DIR"/

echo "Creating zip package..."
cd "$BUILD_DIR"
python -m zipfile -c "$DIST_DIR/lambda.zip" ./*

echo "Package created at: $DIST_DIR/lambda.zip"