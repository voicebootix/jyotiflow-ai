#!/bin/bash

# Missing Columns Fix Runner
# This script fixes the missing columns causing SQL errors in admin and service features

echo "🔧 JyotiFlow Missing Columns Fix"
echo "================================="

# Check if we're in the right directory
if [ ! -f "fix_missing_columns.py" ]; then
    echo "❌ Error: fix_missing_columns.py not found. Please run this script from the backend directory."
    exit 1
fi

# Check if the migration file exists
if [ ! -f "migrations/fix_missing_columns.sql" ]; then
    echo "❌ Error: migrations/fix_missing_columns.sql not found."
    exit 1
fi

echo "📋 Files found:"
echo "  ✅ fix_missing_columns.py"
echo "  ✅ migrations/fix_missing_columns.sql"
echo ""

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 is not installed or not in PATH."
    exit 1
fi

echo "🐍 Python 3 found: $(python3 --version)"
echo ""

# Check for asyncpg
if ! python3 -c "import asyncpg" 2>/dev/null; then
    echo "📦 Installing asyncpg..."
    python3 -m pip install asyncpg
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to install asyncpg."
        echo "Please install it manually: python3 -m pip install asyncpg"
        exit 1
    fi
    echo "✅ asyncpg installed successfully"
else
    echo "✅ asyncpg is already installed"
fi

echo ""

# Check for DATABASE_URL environment variable
if [ -z "$DATABASE_URL" ]; then
    echo "❌ Error: DATABASE_URL environment variable is not set."
    echo "Please set it to your PostgreSQL connection string:"
    echo "  export DATABASE_URL='postgresql://username:password@host:port/database'"
    echo ""
    echo "Example:"
    echo "  export DATABASE_URL='postgresql://user:pass@localhost:5432/mydb'"
    exit 1
fi

echo "✅ DATABASE_URL environment variable is set"
echo ""

# Check if user wants to inspect database first
if [ "$1" == "check" ]; then
    echo "🔍 Checking current database state..."
    python3 fix_missing_columns.py check
    exit 0
fi

# Confirm before running migration
echo "🚨 IMPORTANT: This will modify your database schema."
echo "   Make sure you have a backup of your database!"
echo ""
read -p "Do you want to continue? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Migration cancelled."
    exit 0
fi

echo ""
echo "🚀 Running missing columns fix migration..."
echo "============================================="

# Run the migration
python3 fix_missing_columns.py

# Check the exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SUCCESS: Migration completed successfully!"
    echo ""
    echo "🎯 Next steps:"
    echo "  1. Test the /api/services/types endpoint"
    echo "  2. Test the /api/donations/top-donors/monthly endpoint"
    echo "  3. Check admin dashboard service management"
    echo "  4. Verify credit system functionality"
    echo ""
    echo "📚 For detailed verification steps, see MISSING_COLUMNS_FIX_SUMMARY.md"
else
    echo ""
    echo "❌ FAILURE: Migration failed!"
    echo "Please check the logs above for details."
    echo ""
    echo "🔧 Troubleshooting:"
    echo "  1. Verify database connection"
    echo "  2. Check DATABASE_URL environment variable"
    echo "  3. Ensure database is accessible"
    echo "  4. Review the error messages above"
    exit 1
fi