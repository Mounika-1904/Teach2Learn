import os
import sys
import shutil

# Add the backend directory to the path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

def test_db_init():
    # Use a test-specific directory to avoid locking issues with the real one
    test_instance_dir = os.path.join(os.path.dirname(backend_dir), 'test_instance')
    
    if os.path.exists(test_instance_dir):
        print(f"Removing existing test directory: {test_instance_dir}")
        shutil.rmtree(test_instance_dir, ignore_errors=True)
    
    print("Testing app creation with specific test database path...")
    
    try:
        from app import create_app
        from models import db
        from config import Config
        
        # Override the database URI for the test
        class TestConfig(Config):
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.abspath(os.path.join(test_instance_dir, 'test.db'))}"
        
        app = create_app(config_class=TestConfig)
        
        # Check if the directory was created
        if os.path.exists(test_instance_dir):
            print(f"SUCCESS: Test instance directory was created at {test_instance_dir}")
            test_db_file = os.path.join(test_instance_dir, 'test.db')
            if os.path.exists(test_db_file):
                print(f"SUCCESS: Test database file was created at {test_db_file}")
            else:
                print(f"FAILURE: Test database file was not created")
        else:
            print(f"FAILURE: Test instance directory was not created")
            
        if os.path.exists(test_instance_dir):
            shutil.rmtree(test_instance_dir)
            print("Cleanup done.")
    except Exception as e:
        print(f"ERROR during database initialization test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Final cleanup to ensure test directory is removed
        if os.path.exists(test_instance_dir):
            shutil.rmtree(test_instance_dir, ignore_errors=True)
            print("Final cleanup attempted.")

if __name__ == "__main__":
    test_db_init()
