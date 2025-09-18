# Room API Lighting Integration Tests

init python:
    def test_room_lighting_integration():
        """Test room API extensions for lighting and z-order support"""
        
        print("=== Testing Room API Lighting Integration ===")
        
        # Test 1: Z-order property enforcement
        print("Test 1: Z-order property enforcement")
        test_obj = {"x": 100, "y": 100, "width": 50, "height": 50}
        ensure_object_z_properties(test_obj, "test_object")
        
        expected_keys = {"z", "light_affectable", "layer"}
        if expected_keys.issubset(set(test_obj.keys())):
            print("✓ Z-order properties added correctly")
            print(f"  z={test_obj['z']}, light_affectable={test_obj['light_affectable']}, layer='{test_obj['layer']}'")
        else:
            print("✗ Failed to add z-order properties")
        
        # Test 2: Z-order clamping and layer assignment
        print("\nTest 2: Z-order clamping and layer assignment")
        test_cases = [
            (-5, 0, "room_bg"),    # Below minimum
            (10, 10, "room_bg"),   # In background range
            (25, 25, "room_mid"),  # In middle range  
            (40, 40, "room_fg"),   # In foreground range
            (100, 50, "room_fg")   # Above maximum
        ]
        
        for input_z, expected_z, expected_layer in test_cases:
            test_obj_z = {"z": input_z}
            ensure_object_z_properties(test_obj_z, "test")
            if test_obj_z["z"] == expected_z and test_obj_z["layer"] == expected_layer:
                print(f"✓ Z={input_z} -> z={expected_z}, layer='{expected_layer}'")
            else:
                print(f"✗ Z={input_z} -> z={test_obj_z['z']}, layer='{test_obj_z['layer']}' (expected z={expected_z}, layer='{expected_layer}')")
        
        # Test 3: Z-order utility functions  
        print("\nTest 3: Z-order utility functions")
        if hasattr(store, 'room_objects') and store.room_objects:
            first_obj = list(store.room_objects.keys())[0]
            
            # Test getting z-order
            current_z = get_object_z_order(first_obj)
            if current_z is not None:
                print(f"✓ get_object_z_order('{first_obj}') = {current_z}")
                
                # Test setting z-order
                new_z = 35 if current_z != 35 else 15
                if set_object_z_order(first_obj, new_z):
                    actual_z = get_object_z_order(first_obj)
                    if actual_z == new_z:
                        print(f"✓ set_object_z_order('{first_obj}', {new_z}) successful")
                    else:
                        print(f"✗ set_object_z_order failed: expected {new_z}, got {actual_z}")
                else:
                    print(f"✗ set_object_z_order('{first_obj}', {new_z}) failed")
            else:
                print(f"✗ get_object_z_order('{first_obj}') failed")
        else:
            print("⚠ No room objects available to test z-order functions")
        
        # Test 4: Layer bucket function
        print("\nTest 4: Layer bucket function")
        layer_tests = [
            (0, "room_bg"),
            (16, "room_bg"), 
            (17, "room_mid"),
            (33, "room_mid"),
            (34, "room_fg"),
            (50, "room_fg")
        ]
        
        for z_val, expected_layer in layer_tests:
            actual_layer = z_to_bucket(z_val)
            if actual_layer == expected_layer:
                print(f"✓ z_to_bucket({z_val}) = '{actual_layer}'")
            else:
                print(f"✗ z_to_bucket({z_val}) = '{actual_layer}' (expected '{expected_layer}')")
        
        # Test 5: Migration function
        print("\nTest 5: Migration function")
        try:
            migrated_count = migrate_room_objects_z_order()
            print(f"✓ migrate_room_objects_z_order() completed: {migrated_count} objects migrated")
        except Exception as e:
            print(f"✗ migrate_room_objects_z_order() failed: {e}")
        
        # Test 6: YAML export capability (without actual export)
        print("\nTest 6: YAML export/import functions availability")
        yaml_functions = [
            'export_room_to_yaml',
            'import_room_from_yaml', 
            'export_all_rooms_to_yaml',
            'room_apply_lighting_from_data'
        ]
        
        for func_name in yaml_functions:
            if hasattr(store, func_name):
                print(f"✓ {func_name} function available")
            else:
                print(f"✗ {func_name} function missing")
        
        print("\n=== Room API Lighting Integration Test Complete ===")
        return True

# Label to run the test
label test_room_api_lighting:
    python:
        test_room_lighting_integration()
    
    "Room API lighting integration test completed. Check console output for results."
    return
