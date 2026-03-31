import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from numba import njit
from pint import UnitRegistry
from sklearn.linear_model import` LinearRegression`
from sklearn.metrics import r2_score

# 1. Setup Unit Registry (Global)
ureg = UnitRegistry()
Q_ = ureg.Quantity

# 2. Hardware-Accelerated Physics Core
@njit
def gravity_core(m1, m2, r_meters, G=6.67430e-11):
    """JIT Compiled function for maximum performance."""
    return G * (m1 * m2) / (r_meters**2)

class Formulon:
    def __init__(self, name="Master Engine"):
        self.name = name
        self.G_std = 6.67430e-11 # Standard Gravitational Constant

    def parse_unit(self, value, unit_str):
        """Standardizes any input (cm, km, AU) to Meters."""
        return Q_(value, unit_str).to('meters').magnitude

    def calculate(self, m1, m2, r, unit='meter'):
        """100% Theoretical Calculation (The Physics Law)."""
        r_m = self.parse_unit(r, unit)
        return gravity_core(m1, m2, r_m, self.G_std)

    def analyze_patterns(self, df, m1_col, m2_col, r_col, f_obs_col, r_unit='km'):
        """
        Pattern Recognition: Uses ML to 'discover' the Physics Constant 
        from Real-World Data.
        """
        print(f"[{self.name}] Analyzing Real-World Data Patterns...")
        
        # Unit Conversion for the entire DataFrame
        df['r_m'] = df[r_col].apply(lambda x: self.parse_unit(x, r_unit))
        
        # Feature Engineering: F = G * (m1*m2/r^2) -> y = G * X
        # We create X as the product of masses divided by r squared
        X = (df[m1_col] * df[m2_col] / (df['r_m']**2)).values.reshape(-1, 1)
        y = df[f_obs_col].values
        
        # Machine Learning: Linear Regression without intercept (Force is 0 at infinite distance)
        model = LinearRegression(fit_intercept=False)
        model.fit(X, y)
        
        discovered_G = model.coef_[0]
        r2 = r2_score(y, model.predict(X))
        
        # Add Prediction to DataFrame
        df['predicted_f'] = model.predict(X)
        
        return discovered_G, r2, df

    def plot_discovery(self, df, discovered_G):
        """Visualizes the ML Prediction vs. the Theoretical Law."""
        plt.style.use('dark_background') # Professional scientific look
        plt.figure(figsize=(10, 6))
        
        plt.scatter(df['r_m'], df['force_obs'], color='cyan', alpha=0.5, label='Observed Data')
        
        # Create a smooth line for the ML Prediction
        r_range = np.linspace(df['r_m'].min(), df['r_m'].max(), 100)
        m1_avg, m2_avg = df.iloc[0][0], df.iloc[0][1] # Using sample masses for curve
        f_pred = gravity_core(m1_avg, m2_avg, r_range, G=discovered_G)
        
        plt.plot(r_range, f_pred, color='red', linestyle='--', label=f'ML Discovery (G={discovered_G:.3e})')
        
        plt.title("Formulon: Physics-Informed Machine Learning Discovery")
        plt.xlabel("Distance (Meters)")
        plt.ylabel("Gravitational Force (Newtons)")
        plt.legend()
        plt.grid(alpha=0.2)
        plt.show()

# --- EXAMPLE EXECUTION ---
if __name__ == "__main__":
    engine = Formulon("Astrophysics-Module")

    # A. 100% Theoretical Mode
    force = engine.calculate(m1=5.97e24, m2=7.34e22, r=384400, unit='km')
    print(f"Theoretical Earth-Moon Force: {force:.2e} N")

    # B. Real-World Pattern Mode (Generating dummy noisy data)
    data = {
        'm1': [5.97e24]*50,
        'm2': [7.34e22]*50,
        'dist_km': np.linspace(350000, 450000, 50),
        'force_obs': []
    }
    # Add noise to mimic real observations
    for d in data['dist_km']:
        clean_f = engine.calculate(5.97e24, 7.34e22, d, 'km')
        data['force_obs'].append(clean_f + np.random.normal(0, clean_f*0.05))
    
    df_real = pd.DataFrame(data)
    
    # Run ML Discovery
    g_found, accuracy, results_df = engine.analyze_patterns(
        df_real, 'm1', 'm2', 'dist_km', 'force_obs', r_unit='km'
    )
    
    print(f"ML Discovered G: {g_found:.5e} (Confidence: {accuracy:.4f})")
    engine.plot_discovery(results_df, g_found)