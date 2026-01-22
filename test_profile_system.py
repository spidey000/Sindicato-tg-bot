#!/usr/bin/env python3
"""
Test script for Marxnager Profile System

This script tests the Supabase-backed profile system without requiring
Telegram bot interaction. Useful for development and debugging.

Usage:
    python test_profile_system.py

Requirements:
    - SUPABASE_URL and SUPABASE_KEY must be set in .env
    - Supabase migrations must be run (see docs/setup/SUPABASE_SETUP.md)
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_imports():
    """Test that required modules can be imported."""
    print("🔍 Testing imports...")
    try:
        from src.integrations.supabase_client import DelegadoSupabaseClient
        from src.user_profile import UserProfile, UserProfileManager
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_supabase_connection():
    """Test Supabase client initialization."""
    print("\n🔍 Testing Supabase connection...")
    try:
        from src.integrations.supabase_client import DelegadoSupabaseClient

        supabase = DelegadoSupabaseClient()

        if not supabase.is_enabled():
            print("❌ Supabase not enabled")
            print("   Check that SUPABASE_URL and SUPABASE_KEY are set in .env")
            return False

        # Test connection
        if supabase.test_connection():
            print("✅ Supabase connection successful")
            return True
        else:
            print("❌ Supabase connection test failed")
            return False

    except Exception as e:
        print(f"❌ Supabase connection error: {e}")
        return False


def test_profile_crud(test_user_id=999999999):
    """Test Create, Read, Update, Delete operations for profiles."""
    print(f"\n🔍 Testing Profile CRUD operations (user_id: {test_user_id})...")
    try:
        from src.integrations.supabase_client import DelegadoSupabaseClient
        from src.user_profile import UserProfile, UserProfileManager

        supabase = DelegadoSupabaseClient()
        manager = UserProfileManager(supabase_client=supabase)

        # Clean up any existing test profile
        existing = manager.get_profile(test_user_id)
        if existing:
            manager.delete_profile(test_user_id)
            print(f"🧹 Cleaned up existing test profile")

        # Test 1: Create profile
        print("\n📝 Test 1: Creating profile...")
        profile = UserProfile(
            telegram_user_id=test_user_id,
            telegram_username="test_user",
            telegram_first_name="Test",
            nombre="MARÍA GARCÍA LÓPEZ",
            dni="12345678-Z",
            email="maria.garcia@example.com",
            telefono="611223344",
            direccion="CALLE EJEMPLO 123, 1A",
            codigo_postal="28010",
            ciudad="MADRID",
            provincia="MADRID",
            naf="28/12345678/90",
            fecha_alta="15/03/2020",
            centro_trabajo="AEROPUERTO ADOLFO SUÁREZ MADRID - BARAJAS",
            puesto="Delegada de Sindicales",
            empresa_nombre="IBERIA AIRLINES",
            empresa_cif="B28123456",
            empresa_direccion="AVENIDA DE LA HISPANIDAD 1",
            empresa_codigo_postal="28042",
            empresa_ciudad="MADRID",
            empresa_provincia="MADRID",
            empresa_actividad="TRANSPORTE DE PASAJEROS POR VÍA AÉREA",
            empresa_ccc="2801234567890",
            empresa_trabajadores=150,
            empresa_horario="06.00 a 23.59"
        )

        # Validate profile
        is_valid, errors = profile.validate()
        if not is_valid:
            print(f"❌ Profile validation failed: {errors}")
            return False

        # Create profile
        success, message = manager.create_profile(profile)
        if not success:
            print(f"❌ Profile creation failed: {message}")
            return False
        print("✅ Profile created successfully")

        # Test 2: Read profile
        print("\n📖 Test 2: Reading profile...")
        retrieved = manager.get_profile(test_user_id)
        if not retrieved:
            print("❌ Failed to retrieve profile")
            return False

        # Verify data
        if retrieved.nombre != profile.nombre:
            print(f"❌ Nombre mismatch: {retrieved.nombre} != {profile.nombre}")
            return False
        if retrieved.dni != profile.dni:
            print(f"❌ DNI mismatch: {retrieved.dni} != {profile.dni}")
            return False
        print("✅ Profile retrieved successfully")
        print(f"   Nombre: {retrieved.nombre}")
        print(f"   Email: {retrieved.email}")

        # Test 3: Update profile
        print("\n✏️  Test 3: Updating profile...")
        retrieved.email = "maria.garcia.updated@example.com"
        retrieved.ciudad = "BARCELONA"

        success, message = manager.update_profile(retrieved)
        if not success:
            print(f"❌ Profile update failed: {message}")
            return False

        # Verify update
        updated = manager.get_profile(test_user_id)
        if updated.email != "maria.garcia.updated@example.com":
            print(f"❌ Email not updated: {updated.email}")
            return False
        if updated.ciudad != "BARCELONA":
            print(f"❌ Ciudad not updated: {updated.ciudad}")
            return False
        print("✅ Profile updated successfully")
        print(f"   New email: {updated.email}")
        print(f"   New ciudad: {updated.ciudad}")

        # Test 4: Cache performance
        print("\n⚡ Test 4: Testing cache performance...")
        import time

        # First read (cache miss)
        start = time.time()
        manager.get_profile(test_user_id)
        first_read_time = time.time() - start

        # Second read (cache hit)
        start = time.time()
        manager.get_profile(test_user_id)
        second_read_time = time.time() - start

        print(f"   First read (cache miss): {first_read_time*1000:.2f}ms")
        print(f"   Second read (cache hit): {second_read_time*1000:.2f}ms")
        print(f"   Speedup: {first_read_time/second_read_time:.1f}x")

        # Test 5: Delete profile
        print("\n🗑️  Test 5: Deleting profile...")
        success, message = manager.delete_profile(test_user_id)
        if not success:
            print(f"❌ Profile deletion failed: {message}")
            return False

        # Verify deletion
        deleted = manager.get_profile(test_user_id)
        if deleted is not None:
            print(f"❌ Profile still exists after deletion")
            return False
        print("✅ Profile deleted successfully")

        return True

    except Exception as e:
        print(f"❌ Profile CRUD test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_validation():
    """Test profile validation."""
    print("\n🔍 Testing profile validation...")
    try:
        from src.user_profile import UserProfile

        # Test invalid DNI format
        print("\n❌ Test 1: Invalid DNI format...")
        profile = UserProfile(
            telegram_user_id=1,
            nombre="TEST",
            dni="12345678",  # Missing letter
            email="test@example.com",
            telefono="611223344",
            direccion="TEST",
            codigo_postal="28010",
            ciudad="MADRID",
            provincia="MADRID",
            naf="28/12345678/90",
            fecha_alta="15/03/2020",
            centro_trabajo="TEST",
            empresa_nombre="TEST",
            empresa_cif="B28123456",
            empresa_direccion="TEST",
            empresa_codigo_postal="28010",
            empresa_ciudad="MADRID",
            empresa_provincia="MADRID",
            empresa_ccc="2801234567890"
        )

        is_valid, errors = profile.validate()
        if is_valid:
            print("❌ Validation should have failed for invalid DNI")
            return False
        print(f"✅ Validation correctly failed: {errors[0]}")

        # Test invalid email format
        print("\n❌ Test 2: Invalid email format...")
        profile.dni = "12345678-Z"
        profile.email = "invalid-email"

        is_valid, errors = profile.validate()
        if is_valid:
            print("❌ Validation should have failed for invalid email")
            return False
        print(f"✅ Validation correctly failed: {errors[0]}")

        # Test invalid phone format
        print("\n❌ Test 3: Invalid phone format...")
        profile.email = "test@example.com"
        profile.telefono = "12345678"  # Wrong prefix

        is_valid, errors = profile.validate()
        if is_valid:
            print("❌ Validation should have failed for invalid phone")
            return False
        print(f"✅ Validation correctly failed: {errors[0]}")

        return True

    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Marxnager Profile System Test Suite")
    print("=" * 60)

    # Check environment variables
    if not os.getenv("SUPABASE_URL"):
        print("\n❌ SUPABASE_URL not set in .env")
        print("   See docs/setup/SUPABASE_SETUP.md for setup instructions")
        return 1

    if not os.getenv("SUPABASE_KEY"):
        print("\n❌ SUPABASE_KEY not set in .env")
        print("   See docs/setup/SUPABASE_SETUP.md for setup instructions")
        return 1

    # Run tests
    results = []

    results.append(("Imports", test_imports()))
    results.append(("Supabase Connection", test_supabase_connection()))
    results.append(("Profile CRUD", test_profile_crud()))
    results.append(("Validation", test_validation()))

    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print("=" * 60)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Profile system is working correctly.")
        print("\nNext steps:")
        print("1. Start the bot: docker-compose up -d")
        print("2. Send /profile create to the bot")
        print("3. Follow the wizard to create your profile")
        print("4. Test document generation with profile injection")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("1. Ensure Supabase migrations have been run (docs/setup/SUPABASE_SETUP.md)")
        print("2. Check SUPABASE_URL and SUPABASE_KEY are correct in .env")
        print("3. Verify Supabase project is active and accessible")
        return 1


if __name__ == "__main__":
    sys.exit(main())
