"""ML model loader module."""
import joblib
import os
from pathlib import Path


class MLModels:
    """Singleton class to load and hold ML models."""
    
    _instance = None
    _models_loaded = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MLModels, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._models_loaded:
            self.rf_model = None
            self.lr_model = None
            self.iso_model = None
            self.load_models()
    
    def load_models(self):
        """Load all ML models from disk."""
        try:
            # Get the models directory path
            base_dir = Path(__file__).resolve().parent.parent.parent.parent
            models_dir = base_dir / "models"
            
            # Load Random Forest model
            rf_path = models_dir / "full_rf.pkl"
            if rf_path.exists():
                self.rf_model = joblib.load(str(rf_path))
                print(f"✓ Loaded Random Forest model from {rf_path}")
            else:
                print(f"⚠ Random Forest model not found at {rf_path}")
            
            # Load Logistic Regression model
            lr_path = models_dir / "full_lr.pkl"
            if lr_path.exists():
                self.lr_model = joblib.load(str(lr_path))
                print(f"✓ Loaded Logistic Regression model from {lr_path}")
            else:
                print(f"⚠ Logistic Regression model not found at {lr_path}")
            
            # Load Isolation Forest model
            iso_path = models_dir / "iso.pkl"
            if iso_path.exists():
                self.iso_model = joblib.load(str(iso_path))
                print(f"✓ Loaded Isolation Forest model from {iso_path}")
            else:
                print(f"⚠ Isolation Forest model not found at {iso_path}")
            
            self._models_loaded = True
            
            # Check if all models loaded
            if all([self.rf_model, self.lr_model, self.iso_model]):
                print("✓ All ML models loaded successfully!")
            else:
                print("⚠ Some ML models failed to load. Predictions may not work correctly.")
                
        except Exception as e:
            print(f"✗ Error loading ML models: {e}")
            raise
    
    def get_rf_model(self):
        """Get Random Forest model."""
        return self.rf_model
    
    def get_lr_model(self):
        """Get Logistic Regression model."""
        return self.lr_model
    
    def get_iso_model(self):
        """Get Isolation Forest model."""
        return self.iso_model
    
    def models_ready(self):
        """Check if all models are loaded."""
        return all([self.rf_model, self.lr_model, self.iso_model])


# Global instance
ml_models = MLModels()
